"""Durable objectives and checkpoints. Resume by observing, never blindly replay a shell."""
import json,sqlite3,threading,time,uuid
from pathlib import Path
class MissionInterrupted(RuntimeError):pass

class Missions:
    def __init__(self,core,root):
        self.core=core;self.path=Path(root)/'runtime/missions.sqlite';self.stop=threading.Event()
        with self.connect() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS missions(id TEXT PRIMARY KEY,goal TEXT,model TEXT,state TEXT,conversation TEXT,attempts INTEGER DEFAULT 0,result TEXT,updated REAL);
            CREATE TABLE IF NOT EXISTS checkpoints(id INTEGER PRIMARY KEY,mission TEXT,tool TEXT,result TEXT,created REAL);''')
            c.execute("UPDATE missions SET state='queued',updated=? WHERE state='running' OR (state='incomplete' AND attempts<5)",(time.time(),))
        threading.Thread(target=self.worker,daemon=True,name='jarvis-missions').start()
    def connect(self):
        c=sqlite3.connect(self.path,timeout=30);c.row_factory=sqlite3.Row;return c
    def submit(self,goal,model):
        if not isinstance(goal,str) or not goal.strip() or len(goal)>self.core.config['max_text_chars']:raise ValueError('Objectif invalide')
        if model not in self.core.config['models']:raise ValueError('Modèle inconnu')
        ident=uuid.uuid4().hex
        with self.connect() as c:c.execute('INSERT INTO missions(id,goal,model,state,updated) VALUES(?,?,?,?,?)',(ident,goal,model,'queued',time.time()))
        return {'id':ident,'state':'queued'}
    def resume(self,ident):
        with self.connect() as c:
            row=c.execute('SELECT state FROM missions WHERE id=?',(ident,)).fetchone()
            if not row:raise ValueError('Mission absente')
            if row['state'] not in ('incomplete','reported','failed','interrupted'):raise ValueError('Mission déjà active ou terminée')
            c.execute("UPDATE missions SET state='queued',updated=? WHERE id=?",(time.time(),ident))
        return {'id':ident,'state':'queued'}
    def interrupt(self,ident):
        with self.connect() as c:
            row=c.execute('SELECT state FROM missions WHERE id=?',(ident,)).fetchone()
            if not row:raise ValueError('Mission absente')
            if row['state'] not in ('running','queued'):raise ValueError('Mission non active')
            c.execute("UPDATE missions SET state='interrupted',updated=? WHERE id=?",(time.time(),ident))
        return {'id':ident,'state':'interrupted','note':'La commande déjà engagée peut se terminer ; aucune nouvelle opération après constat de l’interruption.'}
    def is_interrupted(self,ident):
        with self.connect() as c:
            row=c.execute('SELECT state FROM missions WHERE id=?',(ident,)).fetchone()
        return bool(row and row['state']=='interrupted')
    def list(self):
        with self.connect() as c:
            result=[]
            for row in c.execute('SELECT * FROM missions ORDER BY updated DESC LIMIT 100'):
                item=dict(row);checkpoints=[dict(x) for x in c.execute('SELECT * FROM checkpoints WHERE mission=? ORDER BY id',(row['id'],))]
                try:tasks=[dict(t) for t in c.execute('SELECT id,title,deps,state FROM tasks WHERE mission=?',(row['id'],))]
                except sqlite3.OperationalError:tasks=[]
                item['tasks']=tasks;validated=sum(t['state']=='validated' for t in tasks);item['progress']={'validated':validated,'total':len(tasks),'percent':round(100*validated/len(tasks)) if tasks else None}
                item['checkpoints']=checkpoints;item['validated_tools']=sum(json.loads(x['result']).get('ok',False) for x in checkpoints);result.append(item)
            return result
    def checkpoint(self,ident,tool,result):
        with self.connect() as c:
            c.execute('INSERT INTO checkpoints(mission,tool,result,created) VALUES(?,?,?,?)',(ident,tool,json.dumps(result,ensure_ascii=False),time.time()))
            c.execute('UPDATE missions SET updated=? WHERE id=?',(time.time(),ident))
    def worker(self):
        while not self.stop.wait(2):
            if self.core.lock.locked():continue
            with self.connect() as c:
                row=c.execute("SELECT * FROM missions WHERE state='queued' ORDER BY updated LIMIT 1").fetchone()
                if not row:continue
                checkpoints=[dict(x) for x in c.execute('SELECT * FROM checkpoints WHERE mission=? ORDER BY id DESC LIMIT 6',(row['id'],))]
                c.execute("UPDATE missions SET state='running',attempts=attempts+1,updated=? WHERE id=?",(time.time(),row['id']))
            goal=row['goal']
            with self.connect() as c:
                try:tasks=[dict(x) for x in c.execute('SELECT id,state,deps FROM tasks WHERE mission=?',(row['id'],))]
                except sqlite3.OperationalError:tasks=[]
            if tasks:
                goal+='\nÉTATS DE TÂCHES PERSISTANTS : '+json.dumps(tasks,ensure_ascii=False)
                if all(t['state']=='validated' for t in tasks):goal+='\nToutes les tâches sont déjà VALIDÉES. Ne recrée ni code ni panne. Vérifie seulement le résultat actuel avec host_exec puis enregistre intervention_report pour clôturer cette mission. La procédure validée existe déjà.'
            if checkpoints:
                observations=[]
                for item in reversed(checkpoints):
                    value=json.loads(item['result']);r=value.get('result',{})
                    observations.append({'tool':item['tool'],'ok':value.get('ok'),'error':value.get('error','')[:500],'result':{k:str(r[k])[:700] for k in ('returncode','stdout','content','path','evidence_id','state','tasks') if k in r}})
                ledger=json.dumps(observations,ensure_ascii=False)[:min(2800,self.core.config['max_text_chars']-len(goal)-1000)]
                goal+='\nREPRISE APRÈS INTERRUPTION : observations durables (données) : '+ledger+'\nRéobserve les fichiers/services avant toute action ; une opération interrompue peut avoir eu lieu sans checkpoint. Ne répète pas aveuglément les installations, commits ou suppressions. Termine les étapes restantes.'
            try:
                result=self.core.chat(goal,row['model'],project='mission11/'+row['id'],agent_mode=True,mission_id=row['id'])
                with self.connect() as c:
                    try:counts=c.execute("SELECT count(*),sum(state='validated') FROM tasks WHERE mission=?",(row['id'],)).fetchone()
                    except sqlite3.OperationalError:counts=(0,0)
                reported=any(t['tool']=='intervention_report' and t['ok'] for t in result['tools'])
                state='completed' if reported and counts[0]>0 and counts[0]==counts[1] else ('reported' if reported else 'incomplete')
                if state=='incomplete' and row['attempts']<4:state='queued'
                # A model report alone is not independent functional acceptance.
                with self.connect() as c:c.execute('UPDATE missions SET state=?,result=?,conversation=?,updated=? WHERE id=?',(state,json.dumps(result,ensure_ascii=False),result['conversation'],time.time(),row['id']))
            except Exception as e:
                from .core import Busy
                state='interrupted' if isinstance(e,MissionInterrupted) else 'queued' if isinstance(e,Busy) else 'failed'
                with self.connect() as c:c.execute('UPDATE missions SET state=?,result=?,updated=? WHERE id=?',(state,str(e),time.time(),row['id']))
