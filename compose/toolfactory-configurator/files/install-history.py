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
        default=[ "/export/galaxy/config/TF_demo_history_May_21.tar.gz",])
    parser.add_argument("-t", "--toolid", help='tool(s) to install dependencies', default=[], action="append")
    parser.add_argument("-w", "--wfpaths", help='workflow(s) to install',
        default=["/export/galaxy/workflows/TF_demo_make_tools_May_21.ga", "/export/galaxy/workflows/TF_demo_make_test_tools_May_21.ga"])
    return parser

ACTIVE = ['running', 'upload', 'waiting']

def job_check(gi):
    j = [x for x in gi.jobs.get_jobs() if x['state'] in ACTIVE]
    while j and len(j) > 0:
        time.sleep(2)
        j = [x for x in gi.jobs.get_jobs() if x['state'] in ACTIVE]
    print('Server job queue seems empty')
    return 1

def main():
    """
    load histories, workflows and trigger tool dependency installation. Well, try.
    Keep this idiom handy:
    #x=gi.make_get_request(f"http://nginx/api/tools/{tfid}/dependencies", params={'api_key':'fakekey'})
    """
    args = _parser().parse_args()
    if args.key:
        connected = False
        started=time.time()
        while not connected:
            try:
                gi = galaxy.GalaxyInstance(url=args.galaxy, key=args.key)
                connected = True
            except Exception:
                print('install-history: No gi yet...%d seconds' % int(time.time() - started))
                time.sleep(5)
    else:
        print('Need a key passed to install-history - no default found')
        sys.exit(1)
    job_check(gi)
    wfpaths = args.wfpaths
    for wfpath in wfpaths:
        x = gi.workflows.import_workflow_from_local_path(wfpath, publish=True)
        job_check(gi)
        print('Installed %s, res= %s' % (wfpath, x))
    hists = args.history_path
    for hf in hists:
        if os.path.isdir(hf):
            for fp in os.listdir(hf):
                hp = os.path.join(hf,fp)
                if os.path.isfile(hp):
                    x = gi.histories.import_history(file_path=hp, url=None)
                    print('installed ',hp,'res=',x)
                    job_check(gi)

        else:
            x = gi.histories.import_history(file_path=hf, url=None)
            print('installed', hf, 'res=',x)
            job_check(gi)
    x = ''
    gi = galaxy.GalaxyInstance(url=args.galaxy, key=args.key)
    for tfid in args.toolid:
        try:
            x = gi.tools.install_dependencies(tfid)
        except Exception:
            print('Attempt to install %s failed' % tfid)
        job_check(gi)
        print('tried installing dependencies for', tfid, 'dependencies, res=',x)

if __name__ == "__main__":
    main()

