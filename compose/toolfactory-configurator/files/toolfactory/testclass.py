import argparse
import json
import os
import requests
import time


from bioblend import galaxy

ACTIVE = ['running', 'upload', 'waiting']

class ToolTester():
    # test a newly installed tool using bioblend
    """

 https://github.com/nsoranzo/bioblend-tutorial/blob/master/historical_exercises/api-scripts.exercises/run_tool.py
import sys
import json
import requests
import output

BASE_URL = 'http://localhost:8080'

# -----------------------------------------------------------------------------
def run_tool( tool_id, history_id, **kwargs ):
    full_url = BASE_URL + '/api/tools'

    #EXERCISE: POST...

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # e.g. ./run_tool.py Filter1 ebfb8f50c6abde6d '{ "input" : { "src": "hda", "id": "77f74776fd03cbc5" }, "cond" : "c6>=100.0" }'
    # e.g. ./run_tool.py sort1 f597429621d6eb2b '{ "input": { "src": "hda", "id": "b472e2eb553fa0d1" }, "column": "c6", "style": "alpha", "column_set_0|other_column" : "c2", "column_set_0|other_style": "num" }'
    tool_id, history_id = sys.argv[1:3]
    params = json.loads( sys.argv[3] ) if len( sys.argv ) >= 4 else {}
    response = run_tool( tool_id, history_id, **params )
    output.output_response( response )


    def get_testdata(self,urlin,fout):
       '''
        grab a test file
        GET /api/tools/{tool_id}/test_data_download?tool_version={tool_version}&filename={filename}
        http://localhost:8080/api/tools/tacrev/test_data_download?tool_version=2.00&filename=in
        '''
     """
    def __init__(self, args):
        self.galaxy = args.galaxy
        self.key = args.key
        self.tool_id = args.tool_id
        self.update_tool = args.update_tool


    def update_tool(self, jobdetails):
        if jobdetails['state'] == 'ok':
            outs = jobdetails['outputs']


    def run_test(self):
        """
    GET /api/tools/{tool_id}/test_data_download?tool_version={tool_version}&filename={filename}
    http://localhost:8080/api/tools/tacrev/test_data_download?tool_version=2.00&filename=input1
        """
        inputs = {}
        gi = galaxy.GalaxyInstance(url=self.galaxy, key=self.key, verify=False)
        chistory = gi.histories.get_most_recently_used_history()
        chistory_id = chistory['id']
        #contents = gi.histories.show_history(chistory_id, contents=True)
        #print('####chistory',chistory,'\n#### contents=',contents)
        #history = gi.histories.create_history(name=f"{self.tool_id}_test_history")
        #new_hist_id = history['id']
        build_api = ''.join([self.galaxy, '/api/tools/', self.tool_id, '/build'])
        build = gi.make_get_request(url=build_api,params={"history_id":chistory_id}).json()
        testdata_api = ''.join([self.galaxy, '/api/tools/', self.tool_id, '/test_data'])
        test_data = requests.get(testdata_api, params={'key':self.key, 'history_id':chistory_id})# gi.make_get_request(url=fapi,params={"history_id":chistory_id,'key':self.key}).json()
        testinputs = test_data.json()[0].get('inputs',None)
        print('testinputs',testinputs)
        stateinputs = build.get('state_inputs',None) # 'input1': {'values': [{'id': '7b326180327c3fcc', 'src': 'hda'}]}}
        if testinputs:
            for k in testinputs.keys():
                v = testinputs[k]
                if '|' in k:
                    nk = k.split('|')[-1]
                    inputs[nk] = v
                else:
                    inputs[k] = v
        if stateinputs:
            print('stateinputs',stateinputs)
            for k in stateinputs.keys():
                inp = stateinputs[k]
                if isinstance(inp,dict):
                    if inp.get('values',None):
                         for anin in inp['values']:
                            if anin.get('id', None) and anin.get('src', None):
                                gi.histories.copy_dataset(chistory_id, anin['id'], source=anin['src'])
                                print('******copied id', anin['id'])
                                up = {k:anin}
                                print(up)
                                inputs.update(up) # replace the input def
        print('after state inputs', inputs)
        fapi = ''.join([self.galaxy, '/api/tools'])
        r = gi.tools.run_tool(chistory_id, self.tool_id, inputs, input_format='legacy')
        print(f"Called test on {self.tool_id} - got {r}")
        jid = r.get('jobs',None)
        if not jid or len(jid) == 0:
            jobid = jid[0].get('id', None)
            if jobid:
                j = [x for x in gi.jobs.get_jobs() if x['id'] == jobid and x['state'] in ACTIVE]
                while len(j) > 0:
                    time.sleep(2)
                    j = [x for x in gi.jobs.get_jobs() if x['id'] == jobid and x['state'] in ACTIVE]
                jobdetails = gi.jobs.show_job(jobid, full_details=True)
                if self.update_tool:
                    self.update_tool(jobdetails)
            else:
                print('## no job id found in return from call. Something did not go well.')
        else:
            print('## no jobs found in return from call. Something did not go well.')

def _parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--galaxy", help='URL of target galaxy',default="http://nginx")
    parser.add_argument("-a", "--key", help='Galaxy admin key', default="fakekey")
    parser.add_argument("-t", "--tool_id", help='Tool id to test', default="plotter")
    parser.add_argument("-u", "--update_tool", help='Update the ToolFactory generated tool with the outputs', default=False, action="store_true")
    return parser


if __name__ == "__main__":
    args = _parser().parse_args()
    tt = ToolTester(args)
    tt.run_test()

