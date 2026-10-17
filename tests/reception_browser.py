"""Real Chromium -> installed canonical gateway. Credentials and screenshots private."""
import hashlib,hmac,json,pathlib,time
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=pathlib.Path('/home/adminjarvis/JARVIS/jl02-private/browser');OUT.mkdir(mode=0o700,exist_ok=True)
auth=json.loads(pathlib.Path('/opt/jarvis/conversation/runtime/auth.json').read_text());secret=pathlib.Path('/home/adminjarvis/JARVIS/13de-reprise/deployment/13de/private/reprise-user-password.txt').read_text().rstrip('\n')
assert hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',secret.encode(),bytes.fromhex(auth['salt']),300000).hex(),auth['hash'])
checks=[]
def check(name,ok):
 assert ok,name
 checks.append({'name':name,'passed':True})
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/home/adminjarvis/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome',headless=True,args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':1440,'height':1000});page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://localhost:8765/launcher2/');page.wait_for_selector('#account');page.locator('#account').click();page.locator('[name=username]').fill(auth['username']);page.locator('[name=password]').fill(secret);page.locator('#login-form button[type=submit]').click();expect(page.locator('#connection')).to_contain_text('Connecté')
 expect(page.locator('#model option')).to_have_count(3);check('existing_gateway_login',True)
 expect(page.locator('#resources')).to_contain_text('GPU',timeout=25000);check('real_resource_metrics',True)
 for width,height,name in [(1440,1000,'desktop'),(1024,768,'tablet'),(390,844,'phone')]:
  page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(200)
  geometry=page.evaluate('''() => ({bodyH:document.body.scrollHeight,bodyW:document.body.scrollWidth,h:innerHeight,w:innerWidth,m:getComputedStyle(document.querySelector('#messages')).overflowY,s:getComputedStyle(document.querySelector('#sandbox-scroll')).overflowY})''')
  check(name+'_fixed_page_height',geometry['bodyH']<=height+1);check(name+'_no_horizontal_overflow',geometry['bodyW']<=width+1);check(name+'_independent_scroll',geometry['m']=='auto' and geometry['s']=='auto')
  page.screenshot(path=str(OUT/(name+'.png')))
 page.set_viewport_size({'width':1440,'height':1000})
 page.locator('[data-action=ssh]').click();check('v1_protocol_link',page.locator('#launch-action').get_attribute('href').startswith('jarvis-launcher://launch/macbook-pro/ssh'));page.locator('#close-action').click()
 page.locator('#voice-tab').click();check('voice_controls',page.locator('#audio-file').is_visible());page.locator('#prompt-tab').click()
 page.locator('#new-chat').click();page.locator('#prompt').fill('Réponds uniquement : JL02_CONVERSATION_OK');page.locator('#send').click();expect(page.locator('.message.assistant .message-body').last).to_contain_text('JL02_CONVERSATION_OK',timeout=180000);check('real_qwen_conversation',True)
 page.locator('#voice-tab').click();check('shared_text_voice_conversation',page.locator('.message.assistant').count()==1)
 # Stress only DOM size, no synthetic success indicators or fake mission events.
 page.evaluate('''() => {let p=document.querySelector('#messages');for(let i=0;i<100;i++){let n=document.createElement('p');n.textContent='Contrôle de défilement '+i;p.append(n)}}''');check('long_history_keeps_composer',page.locator('#send').is_in_viewport() if hasattr(page.locator('#send'),'is_in_viewport') else page.locator('#send').is_visible())
 page.locator('#expand').click();check('sandbox_expand',page.locator('.workspace.expanded').count()==1);page.locator('#collapse').click();check('sandbox_collapse',page.locator('.workspace.collapsed').count()==1);page.locator('#collapse').click()
 page.locator('#mission-select').select_option('0aa1ab3057b74f10a441bc83980d4761');expect(page.locator('#events .event').first).to_be_visible(timeout=15000);check('real_agent_events',True)
 check('verified_task_tick',page.locator('#tasks .tick').count()>0)
 page.locator('#account').click();expect(page.locator('#connection')).to_have_text('Hors connexion');check('logout',True)
 check('no_browser_javascript_error',not errors)
 browser.close()
(ROOT/'docs/evidence').mkdir(parents=True,exist_ok=True);(ROOT/'docs/evidence/browser-checks.json').write_text(json.dumps({'browser':'Chromium on Debian, installed gateway, real Ollama backend','checks':checks,'physical_macos':False,'physical_microphone':False},ensure_ascii=False,indent=2)+'\n');print(json.dumps(checks))
