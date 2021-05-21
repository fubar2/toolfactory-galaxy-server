# Galaxy ToolFactory Appliance

This is a ToolFactory flavoured developer appliance in Docker extending the basic `docker-galaxy-stable` composition.

1.    The ToolFactory - a form driven code generator to make new Galaxy tools from scripts - is installed with a testing tool.
2.    A container for post-install configuration is added to create the ToolFactory flavour. The new container then runs a planemo server
outside the Galaxy tool execution environment to test tools, returning the planemo test
reports, log and updated archive to the user's current history.
3.    A history containing 15 demonstration tool generation jobs to rerun and build on. Samples use bash, python, perl (yes, even perl. Galaxy is a very welcoming community..),
Rscript and for more discerning users, prolog and lisp. Any scriptable language in Conda should work.

## Depends on docker-galaxy-stable

This flavour of the docker-compose infrastructure is copied from https://github.com/bgruening/docker-galaxy-stable - there is excellent documentation at
that site. Respect. A few minor pointers only are provided below - please refer to the original documentation for details about this extensive infrastructure for Galaxy flavours including
(untested) cluster and other deployment options. The Appliance supporting the ToolFactory is a fully featured `docker-galaxy-stable` Galaxy server, ideal for scientists and developers
who need their own pop-up desktop server for learning how Galaxy works, building new tools, using interactive environments and any available toolshed tools to do real work,
potentially at scale. The Appliance adds only one specific container. The others are all pulled from Björn's docker-galaxy-stable quay.io containers.


## Private desktop use only is recommended.

This Appliance has been configured to weaken some of Galaxy's strict job-runner isolation features so it can install and test tools conveniently.
It is safe to run on a private Linux laptop or workstation.

**Running it on any server accessible from the public internet exposes it to potential miscreants. This is discouraged unless you fully understand the risks**.

Although Galaxy's job execution security is very good, allowing potentially hostile users to build and then immediately run their own tools exposes any production server
to unwelcome security risk.

It runs as a set of Docker containers, so it is secured to that extent from the
host system. ToolFactory and other related source code is included in this repository for the curious or the dubious.
Specific security disclosure details are discussed below. The mechanisms described offer a convenient way for tools to remotely execute tasks outside the Galaxy
job execution environment in suitably private environments such as this Appliance. This may open up interesting uses for Galaxy on the desktop using GPU or
other local resources.

## Tutorial and documentation

There is an accompanying GTN ToolFactory developer tutorial PR in beta test.
[It is temporarily available here on a private server](https://training.galaxy.lazarus.name/training-material/topics/dev/tutorials/tool-generators/tutorial.html)
to help explain how this Appliance can be used to generate Galaxy tools from working command line scripts. There is a linked advanced tutorial.


## Installation and startup

```
git clone https://github.com/fubar2/toolfactory-galaxy-server
cd toolfactory-galaxy-server/compose
docker-compose pull
docker-compose up
```

 - Your appliance should be running with a local Galaxy on localhost:8080 after a fair bit of activity and about 5-10 minutes. Wait until all is done before logging in.
 - Watch the logs as they scroll by on the terminal. They are very instructive and informative for those who need to understand how Galaxy actually works.
 - Keep an eye out for Conda processes on your machine.
 - Wait until they **all** stop.
 - Restarting is much faster.

- Out of the box login is `admin@galaxy.org` and the password is `password`
- This is obviously insecure but convenient and easily changed at first login.
- Change it more permanently in docker-compose.yml if you intend to use this Appliance for your own work.
  - At present, the admin_key default (`fakekey`) is hard-wired into the ToolFactory boot process, but should be changed at first login to something less well known if
the appliance is exposed at all.
  - The API key is the administrative key for the appliance Galaxy so if the Appliance is accessible on a network, it is
exposed to easy API based remote mischief until a new API key is generated. Another good reason not to expose the Appliance anywhere.

The container `/export` directory is mounted locally at `...compose/export` .

## Demonstration tools are the functional documentation

See how they were built, by rerunning the generating job to recreate the ToolFactory form for the run.
Look at the form settings for each one to see what can be done.

To view the form that generated each job, open the toolshed archive or the XML by clicking on it, and select the `rerun` button.
Edit the form and rerun to create an updated tool. The history has previous versions so work is not entirely lost.
Change the tool ID to change the tool name and avoid overwriting previous versions.

## Generating your own tools

Generated tools are installed on build. The whole process takes a few seconds normally.

A new tool requiring Conda dependencies will take time to install those before running the first time. After that first run, the tool will run without delay.

**If two or more new tools that need new dependencies on first run try to install them at the same time, Conda will fail in interesting ways. It is not designed for multiple simultaneous users**

Run one new tool at a time to avoid this causing problems. Once the dependency is installed, the tool will not need to install it again unless the dependency is altered.

Choose the names thoughtfully and be warned: there are no checks on tool names - any existing installed tool with the same name will be overwritten permanently. The history
will retain all the generating jobs if you accidentally overwrite a tool.

Refresh the page (by clicking the home icon or the "analysis" tab) to see them in the `ToolFactory Generated Tools` section and try them out.

Rerun the job and adjust the form. Rinse and repeat until ready.

The generated tool has not been run to generate test outputs, so the archive is not complete although the installed tool may work fine.

To generate a real, tested toolshed archive, use the companion `planemo_test` tool. Planemo will be run in a separate
container. The generated test outputs and the newly updated tested toolshed archive will appear in the history when ready.

The very first test in a fresh Appliance takes a few minutes as Conda installs some dependencies - only needed once.
Subsequently more like a minute or two, depending on conda and the complexity of dependencies needed
for the tool to run.


## To safely shut the appliance down

If you used `-d` to detach,

`docker-compose down`

from the same place you started should shut it down nicely

Otherwise, CtrlC from the attached console will stop the services.

## If things go wrong or if the Appliance is no longer needed

1. Delete the `...compose/export` directory - you will need `sudo rm -rf export/*`

2. Then you can delete the parent git or wget `toolfactory-galaxy-server` directory

3. Use `docker system prune` and respond `y` to the prompt to clean up any damaged containers.

4. Remove all the docker images in the usual way.

## Some docker-galaxy-stable compose configuration notes

base-config.yml is used to alter a number of Galaxy and in particular uwsgi settings. This is neat because the stock galaxy-server image can be used unaltered.
The uwsgi process watches the touch-restart file so the configurator can reboot the server after making changes.
This requires that it operate as `master` but that is a good idea anyway probably..
Galaxy configuration includes turning on the tool change watchdog so Galaxy will update the tool panel after changes are noted.
The ToolFactory configuration completes but the container continues to run, providing a service described in detail below.


## Security disclosures

If you use the ToolFactory for ordinary scripts, it will work without endangering the Appliance. The details below explain how this is possible.

The mechanisms used will not affecting your work unless you write tools that use the methods described below.
If you do, please be mindful that it is possible to damage the appliance
by writing to the wrong places. Normal Galaxy security restrictions are removed to different degrees by these techniques. They are extremely powerful and generalisable but also
a risk if anyone hostile can access the server. Best to ensure that your Appliance is not exposed on the public internet.

More importantly, **any tools written using the Appliance that use either the server or rsync will always fail on a normally secured Galaxy server**, so they are
useless for sharing on the Toolshed. They will only work in a copy of this Appliance or something derived from it.

1. The ToolFactory uses rsync to update the running Galaxy config/tool_conf.xml when a new tool is built. That will fail on a normal Galaxy installation or
a secured cluster production system where rsync would need passwordless ssh to access the (remote) server disk. In the Appliance,
rsync can write anywhere Galaxy can which is as handy as it is insecure. If you choose to use rsync for a tool, remember it will not work in other
Galaxy servers and please, be careful where you write.
If you do accidentally break the Appliance, it takes only a few minutes to delete and recreate the entire server from scratch if necessary.

2. The `planemo_test` tool calls an rpyc (remote procedure call in python) server to run planemo, and to write tested archives to exported
directories that tools should never be able to write, described in more detail below. It is far more restricted than the rsync method because only a single function
is (currently) exposed. However, it is easy to change what the server exposes. It runs as root and has access to everything in the container so it is wise to
expose only very specific and limited functions that cannot be exploited for malicious use of this powerful resource.
At present, that container runs as root - something that could/should be changed. The remote server only exposes specific exported functions, currently only useful for
the `planemo_test` tool, so it will not be possible for a user to damage the system without changing that server code running in the toolfactory-galaxy-server container.

These techniques are completely unsupported by the Galaxy developers. They are handy for integrating the ToolFactory but completely unsuitable for
public internet exposure. Given that constraint, they offer generalisable models for other
potential private desktop Galaxy appliances. These might be integrated with specialised local GPU or other hardware or services that are restricted in some way,
in circumstances where the security risks are known and manageable, given benevolent users.

## Remote command execution for Galaxy tools in a private environment.

The Galaxy framework runs tools in a highly constrained and secure way. The job runner creates a tool execution environment that is very restricted in terms of resource access,
in order to protect the framework, data and database from accidental bugs overwriting critical files or even from malicious damage.

There may be circumstances where it is useful for a tool to be able to do things that are ill-advised and not possible in a normal, secure Galaxy server job runner.
A publicly accessible server is not suited to the methods described here. They introduce substantial security risks through deliberately impaired job security.
On the other hand, in a completely private, dedicated Docker appliance used by a developer, they might be an acceptable risk to the user.
After all, they are unlikely to deliberately damage their own development machine.
Even if they do, the Docker containers and associated local exported volumes can quickly be rebuilt from scratch, at the cost of losing any work done on the Appliance
and not backed up. Before destroying a damaged local installation, generated tool archives can be found in the local `...compose/export/galaxy/tools/TFtools` directory.

### Why would anyone want to do this?

The motivating use case for this deliberate security “work-around” is the requirement for the ToolFactory tool to immediately
install newly generated tools into the running Galaxy, and to test them with Planemo.
These are functions available in the ToolFactory appliance, a flavour of the docker-galaxy-stable core.
The Appliance adds automated post-installation configuration by a specialised server container based on the normal docker-galaxy-stable server.
As soon as the Galaxy server installation is completed, the additional container loads tools, demonstration data, history and workflows to provide the “flavour”.
It also starts a minimal Rpyc server capable of accepting commands from tools running in the Galaxy server container.
It is this rpyc server that is the key to running tasks independently of the normal Galaxy job runner system,
but triggered by a specially configured running tool.

### A generic RPC for tools

The approach described here is a generic way to allow tools executing as normal Galaxy jobs to do things that
Galaxy security, very wisely would normally not permit. These impossible things may have other interesting applications
but the potential cost of associated insecurity must be taken into account outside private settings.

The `planemo_test` tool uses the remote container server by making RPC calls.
The server exposes a single highly specialised and restricted function to test and lint a tool.
It uses but does not expose the Python subprocess module inside the dedicated container to run individual commands including
running planemo to lint and test the tool. When the task completes, the tool finishes up by moving some of the outputs.

For the ToolFactory project, running Planemo test as a tool to test tools has proven difficult.
It was not designed to work as a Galaxy tool and is difficult to manage when called by a tool running as a Galaxy job.
It was designed for command line use and works without problems in the dedicated container when called by the testing tool as if it had
been called on a command line.

There may be other situations where the model used here may be useful on a private desktop. Any desired function can be exposed by the
rpyc server as shown below. Exposed functions are named with the prefix `exposed_` and can make use of more generalised and dangerous
code like the command line runner, but that function is not visible to any calling tools.

### Using rpyc

The running tool sets up a connection to the rpyc server running in the dedicated container (code below) after rpyc is imported with:

```python
conn = rpyc.connect('planemo-server', port=9999, config={'sync_request_timeout':1200})
```

Default docker bridge networking is used by the ToolFactory appliance, so the planemo server can be accessed using the container hostname.
Docker default bridge networking permits the RPC calls to pass between the two containers.
After the connection is established, rpyc allows the tool code to run shell commands on the remote container and receive the outputs as a response,
with a blocking call to the Rpyc server such as:

```python
res = conn.root.planemo_lint_test(xmlin, collectionpath)
```

The provided rpyc server exposes a single function that runs planemo test and lint on the tool passed as the parameter. It uses a dangerous generic command line
runner but this dangerous generic function is not exposed to RPC callers directly.

Planemo is run in the remote container and the outputs from the lint and test proceedures are written to
export directories and the tool output collection, so they appear in the history in the usual way.

The threadcount given as nbThreads below is 1. This may seem strange but it deliberately allows only a single thread to run at any one time.
This is necessary because if two or more Planemo test tasks are installing dependencies, the Planemo Conda data is quickly corrupted since Conda and Planemo
have not been designed to run safely in parallel and do not perform any resource locking.

Other applications may be able to gain better throughput where rpyc can invoke multiple parallel threads. A separate service with higher threadcount could
easily be added.


``` python

import logging
import lxml.etree as ET
import os
from rpyc.utils.server import ThreadPoolServer
from rpyc import Service
import shlex
import shutil
import subprocess
import sys
import time

class planemo_run(Service):

    def run_cmd(self, cmd):
        # not exposed but useful if you need to alter this server for other purposes
        # this is a completely unconstrained command runner so exposing it is probably a bad idea
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
        res = self.run_cmd(f"cp -r {galtooldir} {pwork}/")
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

```


### Securing the rpyc server further

The ToolFactory Appliance runs as a private developer instance, and does not make use of security features offered by rpyc such as authenticated connections.
This is easy to configure for a production environment where this remote procedure call work-around is used.



Ross Lazarus May 2021
