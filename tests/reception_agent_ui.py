"""Submit a real agent task through the private Launcher; verify tools and file."""
import json,pathlib,hashlib,hmac,time,sqlite3
from playwright.sync_api import sync_playwright,expect
R=pathlib.Path(__file__).resolve().parents[1];a=json.loads(pathlib.Path('/opt/jarvis/conversation/runtime/auth.json').read_text());secret=pathlib.Path('/home/adminjarvis/JARVIS/13de-reprise/deployment/13de/private/reprise-user-password.txt').read_text().strip();assert hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',secret.encode(),bytes.fromhex(a['salt']),300000).hex(),a['hash'])
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/home/adminjarvis/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1000});page.goto('http://localhost:8765/launcher2/');page.locator('#account').click();page.locator('[name=username]').fill(a['username']);page.locator('[name=password]').fill(secret);page.locator('#login-form button[type=submit]').click();expect(page.locator('#connection')).to_contain_text('Connecté')
 page.locator('#agent-mode').check();page.locator('#prompt').fill('Crée maintenant le fichier /var/lib/jarvis/projects/JARVIS-Launcher2/docs/RECETTE-INTERFACE-JARVIS.txt contenant exactement JL02_UI_AGENT_OK. Utilise les outils hôte réels pour écrire puis relire ce fichier et vérifier son contenu. Enregistre ensuite un bref rapport intervention_report. Cette écriture dans le dépôt V2 est autorisée par le propriétaire.')
 with page.expect_response(lambda res:res.url.endswith('/api/missions') and res.request.method=='POST',timeout=15000) as pending:page.locator('#send').click()
 job=pending.value.json();ident=job['id'];expect(page.locator('#messages')).to_contain_text('Mission enregistrée')
 deadline=time.monotonic()+160;rows=[]
 while time.monotonic()<deadline:
  with sqlite3.connect('/opt/jarvis/conversation/runtime/missions.sqlite') as c:rows=list(c.execute('select tool,result from checkpoints where mission=?',(ident,)))
  if (R/'docs/RECETTE-INTERFACE-JARVIS.txt').exists() and any(t in ('host_write_file','host_exec') and json.loads(r).get('ok') for t,r in rows) and any('JL02_UI_AGENT_OK' in r and json.loads(r).get('ok') for t,r in rows):break
  page.wait_for_timeout(1000)
 else:raise AssertionError('No real write/read proof within reception timeout')
 assert (R/'docs/RECETTE-INTERFACE-JARVIS.txt').read_text().strip()=='JL02_UI_AGENT_OK';expect(page.locator('#events .event').first).to_be_visible(timeout=15000);b.close()
proofs=[{'tool':t,'ok':json.loads(r).get('ok'),'evidence_id':json.loads(r).get('result',{}).get('evidence_id')} for t,r in rows if t in ('host_write_file','host_read_file','host_exec')]
(R/'docs/evidence/agent-ui.json').write_text(json.dumps({'run_id':ident,'submitted_by':'Real Chromium Launcher form','model':'qwen3.5:27b-q4_K_M','file_independently_verified':'docs/RECETTE-INTERFACE-JARVIS.txt','real_events_visible':True,'proofs':proofs},ensure_ascii=False,indent=2)+'\n');print('Real Launcher mission -> Qwen -> actual file write/read -> visible events: passed')
