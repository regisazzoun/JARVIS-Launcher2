"""Codex progress ledger in the existing mission database; evidence required."""
import argparse,json,sqlite3,time
p=argparse.ArgumentParser();p.add_argument('id');p.add_argument('title');p.add_argument('state',choices=['pending','running','validated','failed','blocked']);p.add_argument('--evidence',default='');a=p.parse_args()
if a.state=='validated' and not a.evidence:raise SystemExit('Evidence required')
c=sqlite3.connect('/opt/jarvis/conversation/runtime/missions.sqlite');c.execute('CREATE TABLE IF NOT EXISTS launcher_operator_tasks(id TEXT PRIMARY KEY,title TEXT,state TEXT,started REAL,updated REAL,evidence TEXT)');now=time.time()
e=[{'ok':True,'evidence_id':a.evidence}] if a.evidence else []
c.execute('INSERT INTO launcher_operator_tasks VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,state=excluded.state,updated=excluded.updated,evidence=excluded.evidence',(a.id,a.title,a.state,now,now,json.dumps(e)));c.commit()
