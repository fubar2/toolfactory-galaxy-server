from bioblend import galaxy
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
    rpyc restricted server providing access to 2 very specific ToolFactory functions exposed to lint and test a tool with planemo
    and to update tool_conf.xml and tools with a newly generated tool.
    Uses an unrestricted command runner and rsync runner but does not expose them to callers - far too generic and
    dangerous.
    """


    def run_cmd(self, cmd):
        """not exposed as too generic and dangerous.
        you'll need to alter this server to suit your needs and this function is a handy but
        completely unconstrained command runner not suitable for exposure....
        """
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

    def run_rsync(self, srcf, dstf):
        """
        not exposed
        """
        src = os.path.abspath(srcf)
        dst = os.path.abspath(dstf)
        if os.path.isdir(src):
            cll = ["rsync", "-r", src, dst]
        else:
            cll = ["rsync", src, dst]
        subprocess.run(
            cll,
            capture_output=False,
            encoding="utf8",
            shell=False,
        )

    def install_deps(self, tool_id):
        gi = galaxy.GalaxyInstance(url='http://galaxy-server', key='fakekey')
        try:
            res = gi.tools.install_dependencies(tool_id)
            logging.info('Tried installing dependencies for %s. Got %s' % (tool_id,res))
        except Exception:
            logging.warning('Attempt to install %s failed' % tool_id)


    def exposed_tool_updater(self, galaxy_root,
        tool_conf_path, new_tool_archive_path, new_tool_name, local_tool_dir):

        """# update config/tool_conf.xml with a new tool unpacked in /tools
        # requires highly insecure docker settings - like write to tool_conf.xml and to tools !
        # if in a container possibly not so courageous.
        # Fine on your own laptop but security red flag for most production instances
        Note potential race condition for tool_conf.xml update avoided if runs in a single thread
        """
        def update_toolconf(tool_conf_path, out_section, tool_id, ourdir, ourxml):  # path is relative to tools

            def sortchildrenby(parent, attr):
                parent[:] = sorted(parent, key=lambda child: child.get(attr))

            tcpaths = ["/etc/galaxy/tool_conf.xml", "/galaxy-central/config/tool_conf.xml"]
            tree = ET.parse(tcpaths[1])
            root = tree.getroot()
            hasTF = False
            TFsection = None
            for e in root.findall("section"):
                if e.attrib["name"] == out_section:
                    hasTF = True
                    TFsection = e
            if not hasTF:
                TFsection = ET.Element("section", {"id":out_section, "name":out_section})
                root.insert(0, TFsection)  # at the top!
            our_tools = TFsection.findall("tool")
            conf_tools = [x.attrib["file"] for x in our_tools]
            for xml in ourxml:  # may be > 1
                if xml not in conf_tools:  # new
                    ET.SubElement(TFsection, "tool", {"file": os.path.join('TFtools', xml)})
            sortchildrenby(TFsection,"file")
            newconf = f"{tool_id}_conf"
            tree.write(newconf, pretty_print=True)
            for tcpath in tcpaths:
                self.run_rsync(newconf, tcpath)

        tool_conf_path = os.path.join(galaxy_root, tool_conf_path)
        tool_dir = os.path.join(galaxy_root, local_tool_dir,'TFtools')
        out_section = "ToolFactory Generated Tools"
        tff = tarfile.open(new_tool_archive_path, "r:*")
        flist = tff.getnames()
        ourdir = os.path.commonpath(flist)  # eg pyrevpos
        tool_id = ourdir  # they are the same for TF tools
        ourxml = [x for x in flist if x.lower().endswith(".xml")]
        tff.extractall()
        tff.close()
        self.run_rsync(ourdir, tool_dir)
        update_toolconf(tool_conf_path, out_section, tool_id, ourdir, ourxml)
        self.install_deps(tool_id)




    def exposed_planemo_lint_test(self, xmlpath, collection):
        """ find the toolid, copy to tested directory, update with planemo test.
        Move the updated files to the real tool directory and the planemo reports
        and log to the collection so they appear in the histories. The calling tool
        will write the tar to the history file.
        """
        xmlin =  xmlpath
        print('xmlin=', xmlin, 'collection=', collection)
        tree = ET.parse(xmlin)
        root = tree.getroot()
        toolname = root.get('id')
        # safest way to get the toolid - for the TF, this determines the tool path
        pwork = os.path.join("/export", "galaxy-central", "tested_TF_archives")
        ptooldir =  os.path.join(pwork,toolname)
        pworkrep = os.path.join("/export", "galaxy-central", "tested_TF_reports")
        prepdir = os.path.join(pworkrep, toolname)
        galtooldir = os.path.join('/galaxy-central/tools/TFtools', toolname)
        toolwork = os.path.sep.join(os.path.split(collection)[:-1])
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
        res = self.run_cmd(f"cp -r  {ptooldir} /galaxy-central/tools/TFtools/")
        allres.append(res)
        for fname in os.listdir(prepdir):
            print('fname', fname, collection)
            if fname.endswith('.json'): # if this is included, the html disappears. Go figure.
                continue
            res = self.run_cmd(f"cp {prepdir}/{fname} {collection}/{fname}")
        self.run_rsync(f"{ptooldir}/{toolname}_tested.toolshed.gz", toolwork)
        self.run_rsync(f"{ptooldir}/{toolname}_tested.toolshed.gz", galtooldir)
        res = self.run_cmd(f"chown -R galaxy:galaxy {pwork} {pworkrep} {galtooldir} {collection}")
        allres.append(res)
        return '\n'.join([x for x in allres if len(x) > 0])


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(level='INFO')
    t = ThreadPoolServer(planemo_run, port=9999, logger=logger, nbThreads=1)
    # single thread experiment to see if planemo/conda behave better. Many condas spoil the conga.
    t.start()


