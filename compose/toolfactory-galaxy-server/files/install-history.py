
#!/usr/bin/python3

import argparse
import os
import requests
import time

from bioblend import galaxy


def _parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--galaxy", help='URL of target galaxy', default="http://nginx")
    parser.add_argument("-k", "--key", help='Galaxy admin key', default="fakekey")
    parser.add_argument("-e", "--email", help='admin email of target galaxy', default="admin@galaxy.org")
    parser.add_argument("-p", "--password", help='Galaxy admin password', default="password")
    parser.add_argument("-i", "--history_path", help='Path to history gz files to be loaded', default="/galaxy/tools/toolfactory/TF_demo_history_May4.tar.gz")
    parser.add_argument("-t", "--toolid", help='tool(s) to install dependencies', default=["rgtf2",], action="append")
    return parser

import requests


def main():
    """
    load a folder of histories or a single gz
    """
    args = _parser().parse_args()
    time.sleep(5) # for some reason, the galaxy admin user doesn't appear for a while. Go figure..
    if args.key:
        gi = galaxy.GalaxyInstance(url=args.galaxy, key=args.key)
    else:
        gi = galaxy.GalaxyInstance(url=args.galaxy, email=args.email, password=args.password)
    hdir = args.history_path
    # h = gi.histories.get_most_recently_used_history()
    if os.path.isdir(hdir):
        for fp in os.listdir(hdir):
            hp = os.path.join(hdir,fp)
            if os.path.isfile(hp):
                x = gi.histories.import_history(file_path=hp, url=None)
                print('installed ',hp,'res=',x)
    else:
        x = gi.histories.import_history(file_path=hdir, url=None)
        print('installed',hdir,'res=',x)
    for tfid in args.toolid:
        x = gi.tools.install_dependencies(tfid)
        print('installed rgtf2 dependencies',hdir,'res=',x)


if __name__ == "__main__":
    main()

