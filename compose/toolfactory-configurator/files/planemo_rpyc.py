
import logging
import os
from rpyc.utils.server import ThreadPoolServer
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
               cl, shell=False, cwd="/planemo", capture_output=False, encoding="utf-8")
            output_str="retcode %d; stdout was captured by the command %s"  % (sp.returncode, cl)
            return(output_str)
        else:
            sp = subprocess.run(
               cl, shell=False, cwd="/planemo", capture_output=True, encoding="utf-8")
            outs = sp.stdout + sp.stderr
            logging.info('retcode %d; cmd=%s' % (sp.returncode, cl))
            return(outs)


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(level='INFO')
    t = ThreadPoolServer(cmd_service, port=9999, logger=logger, nbThreads=1)
    # single thread experiment to see if planemo/conda behave better - yes they do.
    t.start()


