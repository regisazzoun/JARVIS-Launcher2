"""Run an actual Codex check and persist its command, result and timestamp."""
import json,pathlib,sqlite3,subprocess,sys,time
started=time.time();r=subprocess.run(sys.argv[1:],capture_output=True,text=True);output=(r.stdout+r.stderr)[-16000:]
c=sqlite3.connect('/opt/jarvis/conversation/runtime/missions.sqlite',timeout=30);c.execute('CREATE TABLE IF NOT EXISTS launcher_operator_events(id INTEGER PRIMARY KEY,created REAL,command TEXT,output TEXT,returncode INTEGER,duration REAL)')
import shlex
cur=c.execute('INSERT INTO launcher_operator_events(created,command,output,returncode,duration) VALUES(?,?,?,?,?)',(started,shlex.join(sys.argv[1:]),output,r.returncode,time.time()-started));c.commit();print(output);print('Codex event',cur.lastrowid,'returncode',r.returncode);sys.exit(r.returncode)
