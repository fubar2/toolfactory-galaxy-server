
import logging
import lxml.etree as ET
import os
from rpyc.utils.server import ThreadPoolServer
from rpyc import Service
import shlex
import shutil
import subprocess
import sys
import tarfile
import time

class planemo_run(Service):
    """
    rpyc restricted access to a very specific function exposed to lint and test a tool with planemo
    uses an unrestricted command runner but does not expose it.
    """


    def run_cmd(self, cmd):
        # not exposed - you'll need to alter this server to suit your needs but this is a completely unconstrained command runner
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
            if sp.returncode == 0:
                logging.info('retcode %d; cmd=%s' % (sp.returncode, cl))
            else:
                logging.info('### retcode %d NOT zero; cmd=%s; returned %s' % (sp.returncode, cl, outs))
            return(outs)

    def exposed_planemo_lint_test(self, xmlpath, collection):
        xmlin = os.path.join('/export', xmlpath[1:])
        print('xmlin=', xmlin, 'collection=', collection)
        tree = ET.parse(xmlin)
        root = tree.getroot()
        toolname = root.get('id')
        pwork = os.path.join("/export", "galaxy", "tested_TF_archives")
        ptooldir =  os.path.join(pwork,toolname)
        pworkrep = os.path.join("/export", "galaxy", "tested_TF_reports")
        prepdir = os.path.join(pworkrep, toolname)
        galtooldir = os.path.join('/export/galaxy/tools/TFtools', toolname)
        allres = []
        for maked in [prepdir, ptooldir]:
            if not os.path.isdir(maked):
                res = self.run_cmd(f"mkdir -p {maked}")
        res =self.run_cmd(f"cp -r {galtooldir} {pwork}/")
        allres.append(res)
        toolxml = os.path.join(ptooldir, '%s.xml' % toolname)
        res = self.run_cmd("planemo lint %s" % toolxml)
        if res:
            with open(os.path.join(prepdir, '%s_planemo_lint_report.txt' % toolname), 'w') as lint:
                lint.write(res)
                lint.write('\nEnd report\n')
        planemo_rep = os.path.join(prepdir, "%s_planemo_test_report.html" % toolname)
        planemo_json = os.path.join(prepdir, "%s_planemo_test_report.json" % toolname)
        planemo_log = os.path.join(prepdir, "%s_planemo_test_log.txt" % toolname)
        res = self.run_cmd("planemo --directory /planemo/work test --test_output_json %s --galaxy_root /galaxy-central \
           --conda_prefix /planemo/con --update_test_data --test_output %s %s" % (planemo_json, planemo_rep, toolxml))
        if not res:
            res="no response from planemo test...."
            allres.append(res)
        else:
            with open(planemo_log, 'w') as replog:
                replog.write(res)
        res = self.run_cmd(f"tar -cvz -f {ptooldir}/{toolname}_tested.toolshed.gz --directory {pwork} {toolname}")
        allres.append(res)
        res = self.run_cmd(f"cp -r  {ptooldir} /export/galaxy/tools/TFtools/")
        allres.append(res)
        for fname in os.listdir(prepdir):
            print('fname', fname, collection)
            if fname.endswith('.json'): # if this is included, the html disappears. Go figure.
                continue
            res = self.run_cmd(f"cp {prepdir}/{fname} {collection}/{fname}")
        res = self.run_cmd(f"chown -R galaxy:galaxy {pwork} {pworkrep} {galtooldir} {collection}")
        allres.append(res)
        return '\n'.join([x for x in allres if len(x) > 0])


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(level='INFO')
    t = ThreadPoolServer(planemo_run, port=9999, logger=logger, nbThreads=1)
    # single thread experiment to see if planemo/conda behave better - seems so. many condas spoil the conga - it seems to do bad things
    t.start()


