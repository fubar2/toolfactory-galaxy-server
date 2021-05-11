#!/usr/bin/python

import logging
import os
import subprocess
import shutil
import tarfile
import time

from bioblend import galaxy

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

WATCHME = "/export/galaxy/tools/" # in the galaxy-server container
WATCH_PATTERN = [".testme"]
PLANEMO_GALAXY_ROOT = "/galaxy-central" # in our container
CONDA_PREFIX = "/planemo/con"
GALAXY_ROOT="/export/galaxy"

class ToolHandler(PatternMatchingEventHandler):

    def __init__(self, watchme='/export/galaxy/tools', planemo_galaxy_root='/galaxy-central',
        galaxy_root='/export/galaxy', conda_prefix='/planemo/con',
        patterns=['.testme',]):
        PatternMatchingEventHandler.__init__(
            self, patterns=patterns, ignore_directories=True,
            case_sensitive=False
        )
        self.tool_dir = watchme
        self.galaxy_root = galaxy_root
        self.tar_dir = os.path.join(galaxy_root, "tested_TF_tools")
        self.workdir = os.path.join(planemo_galaxy_root, 'planemo', 'work')
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)
        self.GALAXY_ROOT = planemo_galaxy_root
        self.CONDA_PREFIX = conda_prefix
        logging.info('Starting watchdog toolhandler in %s' % self.galaxy_root)
        if not os.path.exists(self.tar_dir):
            os.mkdir(self.tar_dir)


    def on_any_event(self, event):
        # rsync and watchdog work strangely
        if event.is_directory:
            logging.info(
                "ignore directory event %s on %s" % (event.event_type, event.event_path)
            )
            return
        logging.info("### saw %s on %s" % (event.event_type, event.src_path))
        targ = os.path.join(os.path.split(event.src_path)[0], ".testme")
        time.sleep(0.1)
        if os.path.exists(targ):
            try:
                os.remove(targ)
            except Exception:
                logging.info("Cannot delete %s" % targ)
            tooldir = os.path.split(event.src_path)[0]
            toolname = os.path.split(tooldir)[1]
            logging.info(f"{event.src_path} {toolname} requests testing")
            dirlist = os.listdir(tooldir)
            logging.info("### test dirlist %s, path %s" % (dirlist, tooldir))
            xmls = [x for x in dirlist if os.path.splitext(x)[1] == ".xml"]
            if not "%s.xml" % toolname in xmls:
                logging.warning(
                    "Found no %s.xml file after change to %s"
                    % (toolname, event.src_path)
                )
                return
            self.xml_path = os.path.join(tooldir,xmls[0])
            p = self.planemo_lint(tooldir, toolname)
            p = self.planemo_test(tooldir, toolname)
            if p:
                if p.returncode == 0:
                    newtarpath = self.makeToolTar(tooldir, toolname)
                    self.create_history_result(newtarpath=newtarpath,tool_test_output=self.tool_test_output,
                    lint_path=self.lint_path, xml_path=self.xml_path, toolname=toolname)
                    logging.info("### Tested toolshed tarball %s written" % newtarpath)
                else:
                    logging.debug("### planemo stdout:")
                    logging.debug(p.stdout)
                    logging.debug("### planemo stderr:")
                    logging.debug(p.stderr)
                    logging.info("### Planemo call return code = %d" % p.returncode)
        else:
            logging.info("Event %s on %s ignored" % (event.event_type, event.src_path))

    def planemo_test(self, tooldir, toolname):
        testrepdir = os.path.join(self.tar_dir, toolname)
        self.tool_test_output = os.path.join(
            testrepdir, f"{toolname}_planemo_test_report.html"
        )
        cll = [
            "planemo",
            "test",
            "--conda_prefix",
            self.CONDA_PREFIX,
            "--galaxy_root",
            self.GALAXY_ROOT,
            "--test_output",
            self.tool_test_output,
            "--update_test_data",
            os.path.join(tooldir, "%s.xml" % toolname),
        ]
        logging.info("### calling %s" % " ".join(cll))
        p = subprocess.run(
            cll,
            cwd=self.workdir,
            shell=False,
            capture_output=True,
            encoding="utf8",
        )
        return p

    def planemo_lint(self, tooldir, toolname):
        testrepdir = os.path.join(self.tar_dir, toolname)
        self.lint_path = os.path.join(
            testrepdir, f"{toolname}_planemo_lint.txt"
        )

        cll = [
            "planemo",
            "lint",
            os.path.join(tooldir, "%s.xml" % toolname),
        ]
        logging.info("### calling %s" % " ".join(cll))
        lintrep = open(self.lint_path, 'w')
        p = subprocess.run(
            cll,
            cwd=self.workdir,
            shell=False,
            stdout=lintrep,
            stderr=lintrep
        )
        lintrep.close()
        return p


    def makeToolTar(self, tooldir, toolname):
        """move outputs into test-data and prepare the tarball"""
        excludeme = "_planemo_test_report.html"

        def exclude_function(tarinfo):
            filename = tarinfo.name
            return None if filename.endswith(excludeme) else tarinfo

        os.chdir(os.path.split(tooldir)[0])
        self.newtarpath = os.path.join(self.tar_dir, toolname, "%s_tested.toolshed.gz" % toolname)
        tf = tarfile.open(self.newtarpath, "w:gz")
        tf.add(
            name=toolname,
            arcname=toolname,
            filter=exclude_function,
        )
        tf.close()
        os.chdir(self.tar_dir)
        return self.newtarpath


    def wait_for_dataset(self, dataset_id, gi, maxwait=12000, interval=3, check=True):
        """
        Wait until a dataset is in a terminal state.

        :type dataset_id: str
        :param dataset_id: dataset ID

        :type maxwait: float
        :param maxwait: Total time (in seconds) to wait for the dataset state to
          become terminal. If the dataset state is not terminal within this
          time, a ``DatasetTimeoutException`` will be raised.

        :type interval: float
        :param interval: Time (in seconds) to wait between 2 consecutive checks.

        :type check: bool
        :param check: Whether to check if the dataset terminal state is 'ok'.

        :rtype: dict
        :return: Details of the given dataset.
        """
        TERMINAL_STATES = {'ok', 'empty', 'error', 'discarded', 'failed_metadata'}
        assert maxwait >= 0
        assert interval > 0

        time_left = maxwait
        while True:
            dataset = gi.datasets.show_dataset(dataset_id)
            state = dataset['state']
            if state in TERMINAL_STATES:
                if check and state != 'ok':
                   logging.warning(f"Dataset {dataset_id} is in terminal state {state}")
                return dataset
            if time_left > 0:
                time.sleep(min(time_left, interval))
                time_left -= interval
            else:
               logging.error(f"Dataset {dataset_id} is still in non-terminal state {state} after {maxwait} s")


    def create_history_result(self, newtarpath, tool_test_output, lint_path, xml_path, toolname):
        """pure evil to get the html from Planemo into the collection.
            HTML uploads seem not permitted so upload a fake peek and then find the path and fill it.
            Seems to work just fine.
        """
        logging.info('Create_history_result %s' % toolname)
        gi = galaxy.GalaxyInstance('http://nginx', 'fakekey')
        hid= gi.histories.get_most_recently_used_history()['id']
        tar = gi.tools.upload_file(newtarpath ,hid, file_type='toolshed.gz')
        lint = gi.tools.upload_file(lint_path ,hid, file_type='txt')
        xml = gi.tools.upload_file(xml_path ,hid, file_type='xml')
        tarid = tar['outputs'][0]['id']
        lintid = lint['outputs'][0]['id']
        xmlid = xml['outputs'][0]['id']
        with open('peek','w') as f:
            f.write('Planemo test report on %s' % toolname)
        html = gi.tools.upload_file('peek', hid, file_type='txt', file_name="planemo_test")
        html_id = html['outputs'][0]['id']
        self.wait_for_dataset(html_id, gi)
        x = gi.histories.update_dataset(hid, html_id, visible=False)
        x = gi.histories.update_dataset(hid, tarid, visible=False)
        x = gi.histories.update_dataset(hid, lintid, visible=False)
        x = gi.histories.update_dataset(hid, xmlid, visible=False)
        htmldata = gi.make_get_request(url="http://nginx/api/datasets/%s" % html_id, params={"history_id":hid, 'key':'fakekey', 'api_key':'fakekey'}).json()
        htmlf = htmldata['file_name']
        h = '/export/%s' % htmlf
        shutil.copyfile(tool_test_output, h)
        x = gi.histories.update_dataset(hid, html_id, datatype="html")
        self.wait_for_dataset(html_id, gi)
        newcoll = {'collection_type': 'list',
            'element_identifiers': [{'id':html_id,
                'name': '%s Planemo test report' % toolname,
                'src': 'hda', 'file_type':'html', 'visible':'true'},
                {'id': tarid,
                'name': '%s_tested.toolshed.gz' % toolname,
                'src': 'hda', 'file_type':'toolshed.gz', 'visible':'true'},
                {'id': xmlid,
                'name': '%s.xml' % toolname,
                'src': 'hda', 'file_type':'xml', 'visible':'true'},
                {'id': lintid,
                'name': '%s Planemo lint report' % toolname,
                'src': 'hda', 'file_type':'txt', 'visible':'true'}],
            'name': '%s test reports and tested toolshed archive' % toolname}
        resdict = gi.histories.create_dataset_collection(hid, newcoll)
        logging.info('Create_results added collection with results')


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        # filename='/export/galaxy/toolwatcher.log'),
        # filemode="w",
    )
    event_handler = ToolHandler(watchme=WATCHME, planemo_galaxy_root=PLANEMO_GALAXY_ROOT,
       conda_prefix=CONDA_PREFIX, patterns=WATCH_PATTERN, galaxy_root=GALAXY_ROOT)
    observer = Observer()
    observer.schedule(event_handler, path=WATCHME, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
