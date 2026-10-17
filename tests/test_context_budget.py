"""Unit regression with a fake transport; not evidence of JARVIS execution."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from jarvis.core import Core,ROOT
from jarvis.memory import Memory
from jarvis.tools import Registry
class EvidenceBudget(unittest.TestCase):
 def test_large_retrieval_keeps_previous_tool_evidence(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);m=Memory(root/'runtime/db');identity=root/'identity.md';identity.write_text('Identity fixture. '*280)
   cfg=json.loads((ROOT/'config/example.json').read_text());cfg.update(identity_file=str(identity),tool_rounds=3,num_ctx=8192,voice_summary=False,max_text_chars=16000)
   calls=[]
   def model(payload):
    calls.append(payload)
    if len(calls)==1:return {'role':'assistant','content':'','tool_calls':[{'function':{'name':'read_component','arguments':{}}}]}
    if len(calls)==2:
     self.assertIn('EVIDENCE_KEEP',json.dumps(payload['messages']))
     return {'role':'assistant','content':'','tool_calls':[{'function':{'name':'intervention_report','arguments':{'content':'Unit test only; fake transport.'}}}]}
    return {'role':'assistant','content':'Unit test complete.'}
   core=Core(cfg,m,model);core.tools=Registry(m,root,cfg);core.tools.specs['read_component']=('Unit-only',{},[],'read_only',lambda a:{'stdout':'EVIDENCE_KEEP '+('long output '*3000)})
   with patch.object(m,'search',return_value=[{'id':'fixture','content':'retrieved memory '*300} for _ in range(6)]),patch.object(m,'document_search',return_value=[{'source':'fixture','content':'document '*300} for _ in range(2)]):
    r=core.chat('Mission hôte fictive '+('objective '*420),cfg['default_model'],agent_mode=True)
   self.assertTrue(any(t['tool']=='intervention_report' and t['ok'] for t in r['tools']))
if __name__=='__main__':unittest.main()
