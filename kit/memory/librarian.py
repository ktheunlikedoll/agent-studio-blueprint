#!/usr/bin/env python3
"""Manual-first capture and candidate librarian for Memory v1.

The only session input accepted is a structured list of bounded user/assistant
observation excerpts. Whole transcript text is never sent to the model or
stored. All admission filtering runs before the model invocation.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(os.environ.get('PI_CONFIG_DIR', str(Path.home() / '.pi/agent'))).resolve()
DEFAULT_DB = HERE / 'memory/memory.db'
DEFAULT_SESSIONS = HERE / 'sessions'
LOG = HERE / 'memory/consolidation.log'
MODEL = 'z-ai/glm-5.3-flash'
MAX_BATCH = 80

def utcnow(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def log_event(event, **kw):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open('a', encoding='utf-8') as f:
        f.write(json.dumps({'ts':utcnow(),'event':event,**kw}, ensure_ascii=False)+'\n')

def content_text(message: dict) -> str:
    content = message.get('content','')
    if isinstance(content, str): return content
    if not isinstance(content, list): return ''
    bits=[]
    for item in content:
        if isinstance(item, dict) and item.get('type') == 'text' and isinstance(item.get('text'),str):
            bits.append(item['text'])
    return '\n'.join(bits)

def session_id_for(path: Path, first: dict) -> str:
    return str(first.get('id') or path.stem)

def entry_sort_key(e: dict, line_no: int):
    return (str(e.get('timestamp') or ''), str(e.get('id') or f'line-{line_no}'))

def file_observations(path: Path, cursor_eid: str|None = None, limit: int = MAX_BATCH):
    """Redacted structured observations from ONE session file.

    Resumes after cursor_eid when given (JSONL order authoritative). Returns
    (sid, observations, rejected, highest_eid, truncated). highest_eid is the last
    entry consumed — rejected entries advance it too (they are permanently judged).
    """
    observations=[]; rejected=0; highest=None; truncated=False
    try:
        lines=path.read_text(encoding='utf-8', errors='replace').splitlines()
    except OSError:
        return None, [], 0, None, False
    if not lines:
        return None, [], 0, None, False
    try: header=json.loads(lines[0])
    except Exception: return None, [], 0, None, False
    sid=session_id_for(path,header)
    entries=[]
    for n,line in enumerate(lines[1:],2):
        try: obj=json.loads(line)
        except Exception: continue
        if obj.get('type') != 'message': continue
        msg=obj.get('message') or {}
        role=msg.get('role')
        if role not in ('user','assistant'): continue
        text=content_text(msg).strip()
        if not text: continue
        eid=str(obj.get('id') or f'{path.name}:{n}')
        entries.append((entry_sort_key(obj,n),eid,obj,msg,text))
    skipping = cursor_eid is not None
    for _sort,eid,obj,msg,text in entries:
        if skipping:
            if eid == cursor_eid:
                skipping = False
            continue
        from redaction import redact_observation
        rr=redact_observation(text)
        highest=eid
        if not rr.accepted:
            rejected += 1
            continue
        # This is the structured observation envelope, not a transcript copy.
        observations.append({'session_id':sid,'entry_id':eid,
            'timestamp':str(obj.get('timestamp') or msg.get('timestamp') or utcnow()),
            'role':role,'text':rr.text,
            'pointer':f'{path}:{eid}'})
        if len(observations) >= limit:
            truncated=True; break
    return sid, observations, rejected, highest, truncated

def read_structured_observations(sessions_dir: Path, cursor_sid: str|None, cursor_eid: str|None):
    observations=[]; rejected=0; highest=(cursor_sid or '', cursor_eid or '')
    files=sorted(sessions_dir.rglob('*.jsonl')) if sessions_dir.exists() else []
    cursor_seen = cursor_sid is None
    for path in files:
        # Session files are ordered by their timestamped path, not by random UUID
        # session IDs. Resume from the cursor's file position; never compare UUIDs.
        if not cursor_seen:
            try:
                header=json.loads(path.read_text(encoding='utf-8', errors='replace').splitlines()[0])
                if session_id_for(path,header) != cursor_sid:
                    continue
            except Exception:
                continue
            cursor_seen=True
            sid,obs,rej,heid,trunc=file_observations(path, cursor_eid)
        else:
            sid,obs,rej,heid,trunc=file_observations(path)
        observations.extend(obs); rejected+=rej
        if sid and heid: highest=(sid,heid)
        if trunc: break
    return observations,rejected,highest

def next_backfill(sessions_dir: Path, last_file: str|None, last_entry_id: str|None, con):
    """Backlog (2026-11-15, user-requested): the next historical session to ingest.

    Oldest-first, one session per call. Sessions already represented in the store
    are skipped; a previously truncated session resumes mid-file via its entry id.
    Returns (path|None, observations, rejected, highest_eid).
    """
    files=sorted(sessions_dir.rglob('*.jsonl')) if sessions_dir.exists() else []
    start=0; resume_eid=None
    if last_file:
        try:
            idx=files.index(Path(last_file)); start=idx; resume_eid=last_entry_id or None
        except ValueError:
            start=0
    for path in files[start:]:
        sid,obs,rej,heid,trunc=file_observations(path, resume_eid)
        resume_eid=None  # only the cursor file resumes mid-file
        if not sid:
            return path, [], rej, None          # unparseable/empty — advance past
        if not obs and not trunc:
            has=con.execute('SELECT 1 FROM records WHERE source_session_id=? LIMIT 1',(sid,)).fetchone()
            if has:
                continue                        # fully in store already — advance past
            return path, [], rej, None          # nothing worth capturing — advance past
        return path, obs, rej, heid
    return None, [], 0, None

def extract_json(text: str):
    text=text.strip()
    try: return json.loads(text)
    except Exception: pass
    # Models occasionally wrap JSON in a markdown fence.
    m=re.search(r'\{\s*"records"\s*:\s*\[.*\]\s*\}', text, re.S)
    if m:
        try: return json.loads(m.group(0))
        except Exception: pass
    return None

def invoke_librarian(observations: list[dict], *, existing=None, dry_run=False):
    prompt = '''You are the Memory Librarian: an opinionated, studio-doctrine-aware curator.
Extract only defensible, useful knowledge from the STRUCTURED OBSERVATIONS below.
You may form curatorial judgments about how the studio runs and design decisions,
but do not fabricate facts. Every output must point to source record IDs:
source_record_ids MUST be the integer "record_id" values from the observations below.
All output is CANDIDATE status; never promote, supersede, expire, or claim verification.
Finance, client personal data, secrets and credentials are already excluded; do not recreate them.
Taste-library access is READ-ONLY context only: never write to a configured taste library.
Return JSON only, exactly: {"records":[{"decision":"add|update|noop|conflict","existing_record_id":null,"scope":"global|project:<token>","kind":"studio|design|career|process","text":"bounded claim","keys":"3-6 distinctive search terms or proper names","source_record_ids":[1],"confidence":0.0,"rationale":"why supported"}],"opinions":[{"kind":"candidate_insight|candidate_pattern|candidate_question","text":"...","keys":"3-6 distinctive search terms","source_record_ids":[1],"confidence":0.0,"rationale":"..."}]}
decisions (records only; opinions are always new): "add"=new knowledge; "update"=corrects or extends an existing record (set existing_record_id; text = the corrected claim); "noop"=duplicate of an existing record (write nothing); "conflict"=contradicts an existing record (set existing_record_id; state both sides in rationale). Never delete or invalidate anything yourself — the human decides.
Use empty arrays when unsupported. Never include secrets, raw client data, finance content, or unsupported claims.

STRUCTURED OBSERVATIONS (already redacted):
''' + json.dumps(observations, ensure_ascii=False)
    if existing:
        prompt += '\n\nEXISTING RECORDS (id | kind | text — cite these ids in existing_record_id):\n' + json.dumps(existing, ensure_ascii=False)
    else:
        prompt += '\n\nEXISTING RECORDS: none yet.'
    if dry_run: return {'records':[], 'opinions':[]}, 0, ''
    env={'PATH':'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
         'HOME':str(Path.home()),'PI_CONFIG_DIR':str(HERE),
         'LANG':'C.UTF-8'}
    # Preserve only provider key if explicitly supplied in locked env file by wrapper.
    for key in ('OPENROUTER_API_KEY','ZAI_API_KEY'):
        if os.environ.get(key): env[key]=os.environ[key]
    try:
        agent_prompt=(HERE/'agents/memory-librarian.md').read_text(encoding='utf-8')
        p=subprocess.run([str(HERE/'bin/pi'),'--print','--no-session','--no-tools','--no-extensions','--model',MODEL,
                          '--system-prompt',agent_prompt,prompt],
                         cwd=str(HERE),env=env,text=True,capture_output=True,timeout=600)
        data=extract_json(p.stdout)
        return data, p.returncode, (p.stderr[-1000:] if p.stderr else '')
    except Exception as e:
        return None, 124, str(e)

def valid_payload(data):
    return isinstance(data,dict) and isinstance(data.get('records'),list) and isinstance(data.get('opinions'),list)

def admit_candidates(con, payload, inserted_obs, rejected=0):
    """Gate v2 (B2/B3): validate and admit model proposals. Returns (accepted,candidates,noops,rejected).

    Single admission path for BOTH the forward and backfill phases — write-path
    exclusivity means nothing bypasses this loop into the records table.
    """
    sys.path.insert(0,str(HERE/'memory'))
    from db import insert_record
    accepted=0; candidates=0; noops=0
    # Every model candidate is linked to source observation IDs. Unknown IDs are rejected.
    valid_ids={rid for rid,_ in inserted_obs}
    for item in payload.get('records',[]) + payload.get('opinions',[]):
        if not isinstance(item,dict): rejected+=1; continue
        kind=item.get('kind')
        if kind not in ('candidate_insight','candidate_pattern','candidate_question','studio','design','career','process'):
            rejected+=1; continue
        txt=item.get('text'); src=item.get('source_record_ids',[])
        if not isinstance(txt,str) or not txt.strip() or not isinstance(src,list) or not src: rejected+=1; continue
        # Re-run redaction over model output. It must not reintroduce excluded content.
        from redaction import redact_observation
        rr=redact_observation(txt)
        if not rr.accepted or (src and not set(src).issubset(valid_ids)):
            rejected+=1; continue
        # B2: decision handling. Unknown/absent decisions default to 'add'; opinions are always new.
        decision=str(item.get('decision') or 'add').lower()
        if kind in ('candidate_insight','candidate_pattern','candidate_question'): decision='add'
        try: xid=int(item.get('existing_record_id')) if item.get('existing_record_id') not in (None,'','null') else None
        except (TypeError,ValueError): xid=None
        if decision=='noop':
            noops+=1; continue
        if decision in ('update','conflict'):
            if xid is None or not con.execute('SELECT 1 FROM records WHERE id=?',(xid,)).fetchone():
                rejected+=1; continue
        else:
            decision='add'; xid=None
        source_ids=[int(x) for x in src if str(x).isdigit()]
        source_ref=';'.join(str(x) for x in source_ids) or None
        # Scope allowlist (2026-11-15 containment): only 'global' or well-formed project tokens.
        scope=str(item.get('scope') or 'global')
        if scope!='global' and not re.fullmatch(r'project:[A-Za-z0-9_-]+',scope):
            rejected+=1; continue
        # B3: idempotency key includes decision + target — UPDATE/CONFLICT flows never collide with ADD.
        # Fact-augmented keys (B4): model-extracted search terms, stored in a side FTS index.
        keys=' '.join(str(item.get('keys') or '').split())[:200] or None
        eid='candidate:'+hashlib.sha256((kind+'|'+rr.text+'|'+(source_ref or '')+'|'+decision+'|'+str(xid or '')).encode()).hexdigest()[:24]
        rid,created=insert_record(con,scope=scope,kind=kind,text=rr.text,status='candidate',source_session_id='librarian',source_entry_id=eid,evidence_pointer=source_ref,evidence_kind='source-record-ids',confidence=max(0.0,min(1.0,float(item.get('confidence') or 0.0))),supersedes=(xid if decision in ('update','conflict') else None),keys=keys)
        if created and decision=='conflict':
            # Flag the contradicted record for human review; never auto-invalidate (B2 doctrine).
            con.execute("UPDATE records SET review_state=CASE WHEN review_state='none' THEN 'conflict' ELSE review_state END WHERE id=?",(xid,))
        candidates += int(created); accepted += int(created)
    return accepted,candidates,noops,rejected

def consolidate(args):
    sys.path.insert(0,str(HERE/'memory'))
    from db import connect, now, insert_record
    db_path=Path(args.db).resolve(); con=connect(db_path)
    started=now(); cur=con.execute('INSERT INTO consolidation_runs(started,exit_status) VALUES(?,?)',(started,'running')); run_id=cur.lastrowid; con.commit()
    try:
        row=con.execute('SELECT last_session_id,last_entry_id FROM sessions_cursor WHERE id=1').fetchone()
        observations,rejected,highest=read_structured_observations(Path(args.sessions_dir).resolve(), row['last_session_id'],row['last_entry_id'])
        if args.dry_run:
            con.execute('UPDATE consolidation_runs SET ended=?,batches=?,rejected=?,exit_status=? WHERE id=?',(now(),1,rejected,'dry-run',run_id)); con.commit()
            log_event('dry-run',run_id=run_id,batch=len(observations),rejected=rejected)
            print(json.dumps({'observations':len(observations),'rejected':rejected,'dry_run':True}))
            return 0
        forward_ran = bool(observations)
        accepted=0; candidates=0; noops=0; rc=None
        if forward_ran:
            inserted_obs=[]
            # Store bounded observations as candidate evidence records. They are not raw transcript copies.
            for o in observations:
                rid,created=insert_record(con,scope='global',kind='observation',text=o['text'],source_session_id=o['session_id'],source_entry_id=o['entry_id'],evidence_pointer=o['pointer'],evidence_kind='session-entry',confidence=1.0)
                inserted_obs.append((rid,o))
            con.commit()
            # Expose the integer record IDs to the model — it can only cite what it can see.
            for rid,o in inserted_obs:
                o['record_id']=rid
            # B2 gate v2: give the model the existing curated record set so it can decide
            # add/update/noop/conflict instead of always-add (retrieve-then-decide shape).
            existing=[dict(r) for r in con.execute(
                "SELECT id,kind,text FROM records WHERE kind!='observation' AND status IN ('candidate','active') "
                "ORDER BY updated DESC LIMIT 30").fetchall()]
            payload,rc,stderr=invoke_librarian(observations,existing=existing)
            # Persist per-run model output (capped) so the gate is replayable/auditable.
            try:
                outdir=HERE/'memory'/'model-outputs'; outdir.mkdir(exist_ok=True)
                (outdir/f'run-{run_id}.json').write_text(json.dumps({'rc':rc,'stderr':stderr[-500:],'payload':payload})[:20000],encoding='utf-8')
            except Exception:
                pass
            if not valid_payload(payload):
                # Fail-closed (2026-11-15 containment): no fallback admission, no cursor advance.
                # Observations already inserted are idempotent; the next run retries the model.
                con.execute('UPDATE consolidation_runs SET ended=?,rejected=?,exit_status=? WHERE id=?',(now(),rejected,'held-model-unavailable',run_id)); con.commit()
                log_event('model-failed-held',run_id=run_id,returncode=rc,stderr=stderr)
                return 0
            accepted,candidates,noops,rejected = admit_candidates(con,payload,inserted_obs,rejected)
        else:
            log_event('skip-forward',run_id=run_id,rejected=rejected)
        # Backlog (2026-11-15, user-requested): one historical session per run, oldest-first,
        # through the SAME gate. The backfill cursor advances only on a successful gated run.
        bf=con.execute('SELECT last_file,last_entry_id FROM backfill_cursor WHERE id=1').fetchone()
        bfile,bentry=(bf['last_file'],bf['last_entry_id']) if bf else (None,None)
        bpath,bobs,brej,bheid=next_backfill(Path(args.sessions_dir).resolve(),bfile,bentry,con)
        backfill_ran=False
        if bobs:
            binserted=[]
            for o in bobs:
                rid,created=insert_record(con,scope='global',kind='observation',text=o['text'],source_session_id=o['session_id'],source_entry_id=o['entry_id'],evidence_pointer=o['pointer'],evidence_kind='session-entry',confidence=1.0)
                binserted.append((rid,o))
            con.commit()
            for rid,o in binserted: o['record_id']=rid
            bexisting=[dict(r) for r in con.execute(
                "SELECT id,kind,text FROM records WHERE kind!='observation' AND status IN ('candidate','active') "
                "ORDER BY updated DESC LIMIT 30").fetchall()]
            bpayload,brc,bstderr=invoke_librarian(bobs,existing=bexisting)
            try:
                outdir=HERE/'memory'/'model-outputs'
                (outdir/f'run-{run_id}-backfill.json').write_text(json.dumps({'rc':brc,'stderr':bstderr[-500:],'payload':bpayload})[:20000],encoding='utf-8')
            except Exception:
                pass
            if valid_payload(bpayload):
                ba,bc,bn,brj=admit_candidates(con,bpayload,binserted)
                accepted+=ba; candidates+=bc; noops+=bn; rejected+=brj
                con.execute('UPDATE backfill_cursor SET last_file=?,last_entry_id=? WHERE id=1',(str(bpath),bheid or ''))
                backfill_ran=True
                log_event('backfill-complete',run_id=run_id,accepted=ba,rejected=brj,noop=bn,file=Path(bpath).name)
            else:
                # Fail-closed: backfill cursor holds; observations are idempotent; next run retries.
                log_event('backfill-held',run_id=run_id,returncode=brc)
        elif bpath:
            # Empty, unparseable, or already-in-store session — advance past it.
            con.execute('UPDATE backfill_cursor SET last_file=?,last_entry_id=? WHERE id=1',(str(bpath),''))
        if forward_ran:
            # Cursor advances only after admission + candidate transaction. A failed run leaves it in place.
            con.execute('UPDATE sessions_cursor SET last_session_id=?,last_entry_id=? WHERE id=1',highest)
        exit_status = 'ok' if forward_ran else ('backfill-only' if backfill_ran else 'skipped-no-new-entries')
        con.execute('UPDATE consolidation_runs SET ended=?,batches=?,accepted=?,candidates=?,rejected=?,exit_status=? WHERE id=?',(now(),1,accepted,candidates,rejected,exit_status,run_id))
        con.commit(); log_event('complete',run_id=run_id,batch=1,accepted=accepted,candidates=candidates,rejected=rejected,noop=noops,model_returncode=rc,exit_status=exit_status)
        return 0
    except Exception as e:
        con.rollback(); con.execute('UPDATE consolidation_runs SET ended=?,exit_status=? WHERE id=?',(now(),'failed:'+type(e).__name__,run_id)); con.commit(); log_event('failure',run_id=run_id,error=str(e)); print(str(e),file=sys.stderr); return 1
    finally: con.close()

def mark_failed(args):
    sys.path.insert(0,str(HERE/'memory'))
    from db import connect, now
    con=connect(Path(args.db).resolve())
    con.execute("UPDATE consolidation_runs SET ended=?, exit_status=? WHERE id=(SELECT id FROM consolidation_runs WHERE exit_status='running' ORDER BY id DESC LIMIT 1)", (now(), args.status))
    con.commit(); con.close(); log_event('wrapper-failure',status=args.status); return 0

def seed_cv(args):
    sys.path.insert(0,str(HERE/'memory'))
    from db import connect, insert_record
    pdf=Path(args.pdf).resolve(); out=subprocess.run(['pdftotext','-layout',str(pdf),'-'],text=True,capture_output=True,check=True).stdout
    con=connect(Path(args.db).resolve()); created=0
    # Employment/education lines are deliberately parsed into concise career claims;
    # personal contact details and the narrative profile are not seeded.
    patterns=[
      (r'2025\s*[-–]\s*Current\s*\n\s*Promise Church - San Diego \(Freelance\)\s*\n\s*([^\n]+)', '2025-Current','Promise Church - San Diego'),
      (r'2023-2024\s*\n\s*Vega - Cape Town\s*\n\s*Lecturer:\s*\n\s*([^\n]+(?:\n\s*[^\n]+){0,4})', '2023-2024','Vega - Cape Town'),
      (r'2020-Current \(Freelance\)\s*\n\s*The PRM - Johannesburg\s*\n\s*([^\n]+)', '2020-Current','The PRM - Johannesburg'),
      (r'2020-Current \(Freelance\)\s*\n\s*Joseph Ross Roberts Ministries - Tulsa\s*\n\s*([^\n]+)', '2020-Current','Joseph Ross Roberts Ministries - Tulsa'),
      (r'2020-2024 \(Freelance\)\s*\n\s*Red Marketing - Johannesburg & London\s*\n\s*([^\n]+(?:\n\s*[^\n]+){0,4})', '2020-2024','Red Marketing - Johannesburg & London'),
      (r'2018-2019\s*\n\s*Vega - Pretoria\s*\n\s*Lecturer:\s*\n\s*([^\n]+(?:\n\s*[^\n]+){0,4})', '2018-2019','Vega - Pretoria'),
      (r'2014-2017\s*\n\s*Boogertman \+ Partners Architects - Pretoria\s*\n\s*([^\n]+(?:\n\s*[^\n]+){0,3})', '2014-2017','Boogertman + Partners Architects - Pretoria'),
      (r'2013 \(Freelance\)\s*\n\s*First National Bank - Pretoria\s*\n\s*([^\n]+)', '2013','First National Bank - Pretoria'),
      (r'2012-2013\s*\n\s*Smile . Waive Promotions - Pretoria\s*\n\s*([^\n]+)', '2012-2013','Smile n Waive Promotions - Pretoria'),
    ]
    for pat,dates,org in patterns:
        m=re.search(pat,out,re.I)
        highlights=' '.join(m.group(1).split()) if m else 'Career entry extracted from CV; review against source PDF.'
        text=f'{org}; role/ highlights: {highlights}; dates: {dates}'
        _,ok=insert_record(con,scope='global',kind='career',text=text,status='candidate',source_session_id='dkcv_2026.pdf',source_entry_id=f'{org}|{dates}',evidence_pointer=f'{pdf}#page=1',evidence_kind='pdf-page',confidence=0.75,verified_by_user=0)
        created+=int(ok)
    # Skills are useful ledger candidates and remain unverified.
    skills=['Adobe Creative Cloud','HTML and CSS','Python','Vibe Coding','UX/UI (Figma and Adobe XD)','Teaching and lecturing','Academic research and writing','Voice over','Graphic design','Typography','Packaging design','Web design and branding']
    for skill in skills:
        _,ok=insert_record(con,scope='global',kind='career',text=f'Skill: {skill}; source: dkcv_2026.pdf',status='candidate',source_session_id='dkcv_2026.pdf',source_entry_id='skill:'+skill,evidence_pointer=f'{pdf}#page=1',evidence_kind='pdf-page',confidence=0.75,verified_by_user=0)
        created+=int(ok)
    con.commit(); con.close(); print(json.dumps({'created':created,'pdf':str(pdf)})); return 0

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    c=sub.add_parser('consolidate'); c.add_argument('--manual',action='store_true'); c.add_argument('--dry-run',action='store_true'); c.add_argument('--db',default=str(DEFAULT_DB)); c.add_argument('--sessions-dir',default=str(DEFAULT_SESSIONS)); c.set_defaults(fn=consolidate)
    f=sub.add_parser('mark-failed'); f.add_argument('--db',default=str(DEFAULT_DB)); f.add_argument('--status',required=True); f.set_defaults(fn=mark_failed)
    s=sub.add_parser('seed-cv'); s.add_argument('--pdf',required=True); s.add_argument('--db',default=str(DEFAULT_DB)); s.set_defaults(fn=seed_cv)
    args=ap.parse_args(); return args.fn(args)
if __name__=='__main__': raise SystemExit(main())
