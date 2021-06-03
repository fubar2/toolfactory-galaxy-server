
#!/usr/bin/python

import argparse
import os
import requests
import subprocess
import time

from bioblend import galaxy


def _parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--galaxy", help='URL of target galaxy', default="http://galaxy-server")
    parser.add_argument("-k", "--key", help='Galaxy admin key', default="fakekey")
    parser.add_argument("-e", "--email", help='admin email of target galaxy', default="admin@galaxy.org")
    parser.add_argument("-p", "--password", help='Galaxy admin password', default="password")
    parser.add_argument("-i", "--history_path", help='Path to history gz files to be loaded', default="/export/galaxy/tools/toolfactory/TF_demo_history_May_12.tar.gz")
    parser.add_argument("-t", "--toolid", help='tool(s) to install dependencies', default=["rgtf2","planemo_test"], action="append")
    return parser

import requests


def main():
    """
    make sure no jobs running - status  in  [ 'running', 'upload', 'waiting' ]
    """
    args = _parser().parse_args()
    assert args.key
    connected = False
    while not connected:
        try:
            gi = galaxy.GalaxyInstance(url=args.galaxy, key=args.key)
            response = gi.users.get_users()
            if response and len(response) > 0:
                connected = True
        except Exception:
            print('install-history: No gi yet...')
            time.sleep(1)
    #gi.make_get_request(url, params=data, stream=True, timeout=user_gi.timeout)
    ACTIVE = ['running', 'upload', 'waiting']
    j = [x for x in gi.jobs.get_jobs() if x['state'] in ACTIVE]
    while j and len(j) > 0:
        time.sleep(1)
        j = [x for x in gi.jobs.get_jobs() if x['state'] in ACTIVE]
    print('Server job queue seems empty')

if __name__ == "__main__":
    main()

