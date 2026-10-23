"""JL-02 adapter on the canonical gateway: no new auth, worker or memory."""
import concurrent.futures,json,pathlib,re,sqlite3,threading,time
from contextlib import contextmanager
from .launcher_telemetry import collect
from .host_client import request
ASSETS=pathlib.Path('/opt/jarvis/conversation/launcher2')
PROJECTS_ROOT=pathlib.Path('/var/lib/jarvis/projects')
MIMES={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.svg':'image/svg+xml','.md':'text/plain; charset=utf-8','.zip':'application/zip'}
ALLOWED={'index.html','app.js','style.css','task-model.js','format.js','core.js','config.json','icon.svg','guide.html','companion-macos.zip'}
class Launcher:
    def __init__(self,root):
        self.root=pathlib.Path(root);self.metrics={'sampled_at':None,'machines':{'mac-mini':{'available':False},'dell-1':{'available':False},'dell-2':{'available':False,'reason':'Pas encore opérationnel'}}};self.lock=threading.Lock()
        threading.Thread(target=self.refresh,daemon=True,name='launcher-metrics').start()
    def refresh(self):
        while True:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                mac=pool.submit(collect);dell=pool.submit(self.dell)
                try:local=mac.result(timeout=12)
                except Exception:local={'available':False}
                try:remote=dell.result(timeout=55)
                except Exception:remote={'available':False}
            with self.lock:self.metrics={'sampled_at':time.time(),'machines':{'mac-mini':local,'dell-1':remote,'dell-2':{'available':False,'reason':'Pas encore opérationnel'}}}
            time.sleep(8)
    def dell(self):
        r=request('host_remote',{'host':'dell-observe','action':'telemetry'})
        return json.loads(r['result']['stdout'])
    def resources(self):
        with self.lock:return self.metrics
    @contextmanager
    def db(self):
        c=sqlite3.connect('file:'+str(self.root/'runtime/missions.sqlite')+'?mode=ro',uri=True,timeout=10);c.row_factory=sqlite3.Row
        try:yield c
        finally:c.close()
    def missions(self):
        with self.db() as c:
            rows=[]
            for r in c.execute('SELECT id,goal,model,state,attempts,updated,created,conversation,last_progress,active_task,spec FROM missions ORDER BY updated DESC LIMIT 80'):
                d=dict(r);metadata=json.loads(d.pop('spec') or '{}');d['original_goal']=d['goal'];d['goal']=metadata.get('display_title',d['goal']);d['related_mission']=metadata.get('related_mission');tasks=[]
                for t in c.execute('SELECT id,title,state,deps,evidence,updated,started,artifact,report_sha256 FROM tasks WHERE mission=?',(r['id'],)):
                    t=dict(t);t['evidence']=json.loads(t['evidence']);t['agent']='JARVIS';tasks.append(t)
                count=sum(t['state']=='validated' and bool(t['evidence']) for t in tasks)
                d.update(agent='JARVIS',tasks=tasks,progress={'total':len(tasks),'validated':count,'percent':round(100*count/len(tasks)) if tasks else None,'measured':True,'basis':'validated_tasks'},started=c.execute('SELECT min(created) FROM checkpoints WHERE mission=?',(r['id'],)).fetchone()[0]);rows.append(d)
            # Operator tasks are recorded separately; never attributed to Qwen.
            if c.execute("SELECT 1 FROM sqlite_master WHERE name='launcher_operator_tasks'").fetchone():
                tasks=[dict(t) for t in c.execute('SELECT * FROM launcher_operator_tasks ORDER BY started')]
                for t in tasks:t['evidence']=json.loads(t['evidence']);t['agent']='Codex'
                rows.insert(0,{'id':'JL-02-coordination','goal':'JL-02 — coordination, intégration et réception','agent':'Codex','model':None,'state':'running' if any(t['state']=='running' for t in tasks) else 'completed' if all(t['state']=='validated' for t in tasks) else 'incomplete','attempts':1,'updated':max((t['updated'] for t in tasks),default=None),'started':min((t['started'] for t in tasks),default=None),'tasks':tasks,'progress':{'total':len(tasks),'validated':sum(t['state']=='validated' for t in tasks),'percent':round(100*sum(t['state']=='validated' for t in tasks)/len(tasks)) if tasks else None,'measured':False}})
            return rows
    def artifact(self,path):
        target=pathlib.Path(path).resolve()
        if not target.is_relative_to(PROJECTS_ROOT) or any(x in ('.git','private','.ssh') for x in target.parts):raise PermissionError('Fichier hors périmètre')
        limit=16*1024*1024 if target.suffix.lower()=='.wav' else 2*1024*1024
        if not target.is_file() or target.stat().st_size>limit:raise ValueError('Fichier absent ou trop volumineux')
        if target.suffix.lower() not in ('.md','.txt','.json','.js','.py','.css','.html','.cjs','.log','.wav'):raise ValueError('Type non proposé')
        body=target.read_bytes()
        if target.suffix.lower()=='.wav' and not (body[:4]==b'RIFF' and body[8:12]==b'WAVE'):raise ValueError('WAV RIFF attendu')
        return body
    def events(self,ident,after=0):
        if ident=='JL-02-coordination':
            with self.db() as c:
                if not c.execute("SELECT 1 FROM sqlite_master WHERE name='launcher_operator_events'").fetchone():return {'events':[],'cursor':after}
                rows=list(c.execute('SELECT * FROM launcher_operator_events WHERE id>? ORDER BY id LIMIT 150',(after,)))
            return {'events':[{'id':r['id'],'created':r['created'],'agent':'Codex','tool':'verification','command':r['command'],'output':r['output'],'ok':r['returncode']==0,'returncode':r['returncode'],'duration_s':r['duration'],'evidence_id':'codex-event-'+str(r['id'])} for r in rows],'cursor':rows[-1]['id'] if rows else after}
        if len(ident)>80:raise ValueError('Identifiant invalide')
        with self.db() as c:
            if c.execute("SELECT 1 FROM sqlite_master WHERE name='mission_events'").fetchone():
                records=list(c.execute('SELECT * FROM mission_events WHERE mission=? AND id>? ORDER BY id LIMIT 150',(ident,after)))
                if records:
                    events=[]
                    for row in records:
                        args=json.loads(row['arguments'] or '{}');result=json.loads(row['result'] or '{}');value=result.get('result',{})
                        output=str(value.get('stdout',value.get('content',result.get('error',json.dumps(result,ensure_ascii=False)))))
                        output=re.sub(r'(?:github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9_]+)','[secret masqué]',output)
                        command=args.get('command') or ' '.join(str(args[k]) for k in ('host','action','service','path') if k in args)
                        events.append({'id':row['id'],'created':row['created'],'agent':row['actor'],'tool':row['tool'] or row['kind'],'kind':row['kind'],'command':command[:3000],'output':output[:12000],'ok':result.get('ok') if row['kind']=='tool_finished' else None,'duration_s':row['duration'],'evidence_id':row['invocation'],'artifacts':[value['path']] if isinstance(value.get('path'),str) and value['path'].startswith('/var/lib/jarvis/projects/') else []})
                    return {'events':events,'cursor':records[-1]['id']}
                if c.execute("SELECT 1 FROM missions WHERE id=? AND origin!='legacy'",(ident,)).fetchone():
                    return {'events':[],'cursor':after}
            rows=list(c.execute('SELECT id,tool,result,created FROM checkpoints WHERE mission=? AND id>? ORDER BY id LIMIT 150',(ident,after)))
        wanted={json.loads(x['result']).get('result',{}).get('evidence_id') for x in rows};args={}
        trace=self.root/'runtime/tool-traces.jsonl'
        # Tail capped to 3 MiB; historical events remain in checkpoints even if trace rotated.
        if trace.exists():
            with trace.open('rb') as f:
                f.seek(max(0,trace.stat().st_size-3*1024*1024));lines=f.read().decode(errors='replace').splitlines()
            for line in lines:
                try:
                    t=json.loads(line);eid=t['result'].get('result',{}).get('evidence_id')
                    if eid and eid in wanted:args[eid]=t.get('arguments',{})
                except (ValueError,KeyError):pass
        events=[]
        for row in rows:
            d=json.loads(row['result']);r=d.get('result',{});eid=r.get('evidence_id');a=args.get(eid,{})
            output=str(r.get('stdout',r.get('content',d.get('error',''))))[:5000]
            output=re.sub(r'(?:github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9_]+)','[secret masqué]',output)
            command=a.get('command') or ' '.join(str(a[k]) for k in ('host','action','service','service_action','path') if k in a)
            events.append({'id':row['id'],'created':row['created'],'agent':'JARVIS','tool':row['tool'],'ok':bool(d.get('ok')),'command':command[:3000],'output':output,'evidence_id':eid,'returncode':r.get('returncode'),'duration_s':d.get('elapsed_s'),'artifacts':[a['path']] if isinstance(a.get('path'),str) and a['path'].startswith('/var/lib/jarvis/projects/') else []})
        return {'events':events,'cursor':rows[-1]['id'] if rows else after}

def handle_get(handler,p,q):
    if p in ('/launcher2','/launcher2/') or p.startswith('/launcher2/'):
        name=p.removeprefix('/launcher2/');name='index.html' if p in ('/launcher2','/launcher2/') else name
        if name not in ALLOWED:handler.send({'error':'Introuvable'},404);return True
        f=ASSETS/name
        if not f.is_file():handler.send({'error':'Introuvable'},404);return True
        handler.send(f.read_bytes(),mime=MIMES.get(f.suffix,'application/octet-stream'));return True
    api=handler.server.launcher
    if p=='/api/launcher/artifact':
        path=q.get('path',[''])[0]
        handler.send(api.artifact(path),mime='audio/wav' if pathlib.Path(path).suffix.lower()=='.wav' else 'text/plain; charset=utf-8');return True
    if p=='/api/launcher/resources':handler.send(api.resources());return True
    if p=='/api/launcher/missions':handler.send(api.missions());return True
    if p=='/api/launcher/events':handler.send(api.events(q.get('mission',[''])[0],int(q.get('after',['0'])[0])));return True
    return False
