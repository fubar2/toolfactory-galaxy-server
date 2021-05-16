
#!/usr/bin/python

import argparse
import os
import requests
import subprocess
import time

from bioblend import galaxy


def _parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--galaxy", help='URL of target galaxy', default="http://nginx")
    parser.add_argument("-k", "--key", help='Galaxy admin key', default="fakekey")
    parser.add_argument("-e", "--email", help='admin email of target galaxy', default="admin@galaxy.org")
    parser.add_argument("-p", "--password", help='Galaxy admin password', default="password")
    parser.add_argument("-i", "--history_path", action="append", help='Paths to history gz files to be loaded',
       default=[ "/export/galaxy/tools/toolfactory/TF_demo_history_May_12.tar.gz", "/export/galaxy/tools/toolfactory/TF-Demo-data-May-16.tar.gz"])
    parser.add_argument("-t", "--toolid", help='tool(s) to install dependencies', default=["rgtf2","planemo_lint"], action="append")
    return parser

import requests

ACTIVE = ['running', 'upload', 'waiting']

def job_check(gi):
    j = [x for x in gi.jobs.get_jobs() if x['state'] in ACTIVE]
    while j and len(j) > 0:
        time.sleep(1)
        j = [x for x in gi.jobs.get_jobs() if x['state'] in ACTIVE]
    print('Server job queue seems empty')
    return 1

def main():
    """
    load a folder of histories or a single gz
    """
    args = _parser().parse_args()
    if args.key:
        connected = False
        while not connected:
            try:
                gi = galaxy.GalaxyInstance(url=args.galaxy, key=args.key)
                connected = True
            except Exception:
                print('install-history: No gi yet...')
                time.sleep(5)
    job_check(gi)
    hists = args.history_path
    for hf in hists:
        if os.path.isdir(hf):
            for fp in os.listdir(hf):
                hp = os.path.join(hf,fp)
                if os.path.isfile(hp):
                    x = gi.histories.import_history(file_path=hp, url=None)
                    print('installed ',hp,'res=',x)
        else:
            x = gi.histories.import_history(file_path=hf, url=None)
            print('installed', hf, 'res=',x)
    job_check(gi)
    wfpaths = ["/export/galaxy/tools/toolfactory/TF_demo_make_tools_May_15.ga", "/export/galaxy/tools/toolfactory/TF_demo_make_test_tools_May_15.ga"]
    for wfpath in wfpaths:
        x = gi.workflows.import_workflow_from_local_path(wfpath, publish=True)
        print('Installed %s, res= %s' % (wfpath, x))
    job_check(gi)
    for tfid in args.toolid:
        x = gi.tools.install_dependencies(tfid)
        #x=gi.make_get_request(f"http://nginx/api/tools/{tfid}/dependencies", params={'api_key':'fakekey')
        print('installed', tfid, 'dependencies, res=',x)


if __name__ == "__main__":
    main()

