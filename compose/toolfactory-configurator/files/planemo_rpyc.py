
import logging
import os
from rpyc.utils.server import ForkingServer
from rpyc import Service
import shlex
import subprocess
import sys



class cmd_service(Service):

    def exposed_run_cmd(self, cmd):
        logging.info('Processing cmd %s' % cmd)
        cl = shlex.split(cmd)
        if ">" in cl:
            sp = subprocess.Popen(
               cl, shell=False, capture_output=True, encoding="utf-8")
            output_str="stdout was captured by the command"
            return(output_str)
        else:
            sp = subprocess.run(
               cl, shell=False, capture_output=True, encoding="utf-8")
            outs = sp.stdout + sp.stderr
            logging.info('retcode %d; output=%s' % (sp.returncode, outs))
            return(outs)


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(level='INFO')
    t = ForkingServer(cmd_service, port=9999, logger=logger)
    t.start()


