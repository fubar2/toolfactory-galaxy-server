# Galaxy ToolFactory Appliance

This is a ToolFactory flavoured developer appliance in Docker extending the basic `docker-galaxy-stable` composition, by adding:

1.    A working copy of the ToolFactory - a form driven code generator to make new Galaxy tools from scripts
2.    The Appliance uses the official quay.io containers, adding a container for post-install configuration to create the ToolFactory flavour.
The new container then runs a planemo server outside the Galaxy tool execution environment to test tools, returning the planemo test
reports, log and updated archive to the user's current history.
3.    A history containing 14 demonstration tool generation jobs to rerun and build on. Samples use bash, python, perl (yes, even perl. Galaxy is a very welcoming community..),
Rscript and for more discerning users, prolog and lisp. Any scriptable language in Conda should work.
4.    A warning that it would be extraordinarily unwise to ever expose this appliance anywhere on the public internet. Please, just don't. Read on to learn why.

## Depends on docker-galaxy-stable

This is a flavour of the docker-compose infrastructure copied from https://github.com/bgruening/docker-galaxy-stable - there is excellent documentation at
that site. Respect. A few minor pointers only are provided below - please refer to the original documentation for details about this extensive infrastructure for Galaxy flavours including
(untested) cluster and other deployment options. The Appliance supporting the ToolFactory is a fully featured `docker-galaxy-stable` Galaxy server, ideal for scientists and developers
who need their own pop-up desktop server for learning how Galaxy works, building new tools, using interactive environments and any available toolshed tools to do real work,
potentially at scale.


## WARNING!

**This appliance has been configured to "work around" some of Galaxy's strict job-runner isolation features**

Users are advised **not to run it on any server accessible from the public internet and potential miscreants**.
If the user(s) are not hostile, it is perfectly safe to run on a normally secured Linux laptop or desktop that is not accessible from any remote network, particularly
if all the users understand exactly how the appliance makes very convenient but completely unconstrained resource access available to any tool.

It runs as a set of Docker containers, so it is secured to that extent from the
host system. ToolFactory and other related source code is included in this repository for the curious or the dubious. Specific security disclosure details are discussed below.


## Tutorial and documentation

There is an accompanying GTN ToolFactory developer tutorial PR in beta test. [It is available here on a private server](https://training.galaxy.lazarus.name/training-material/topics/dev/tutorials/tool-generators/tutorial.html)
to help explain how this Appliance can be used to generate Galaxy tools from working command line scripts.


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

- Out of the box login is `admin@galaxy.org` and the password is `password`
- This is obviously insecure but convenient and easily changed at first login.
- Change it more permanently in docker-compose.yml if you intend to use this Appliance for your own work.
  - At present, the admin_key default (`fakekey`) is hard-wired into the ToolFactory boot process, but should be changed at first login to something less well known if the appliance is exposed at all.
  - The API key is the administrative key for the appliance Galaxy so if the Appliance is accessible on a network, it is
exposed to easy API based remote mischief until a new API key is generated. Another good reason not to expose the Appliance anywhere.

The container `/export` directory is mounted locally at `...compose/export` .

## Demonstration tools are the functional documentation

Follow the welcome page instructions to start exploring how they were built by rerunning the generating job to recreate the ToolFactory form
for the run and looking at the settings for each one to see what can be done.

To view the form that generated each job, open the toolshed archive or the XML by clicking on it, and select the `rerun` button.
Edit the form and rerun to create an updated tool. The history has previous versions so work is not entirely lost.
Change the tool ID to change the tool name and avoid overwriting previous versions.

## Generating your own tools

Generated tools are installed on build. The whole process takes a few seconds after the very first one - Conda takes some time on the first run. A new tool requiring Conda dependencies
will also take time to install those before running the first time. After that first run, the tool will run without delay.

Choose the names thoughtfully and be warned: there are no checks on tool names - any existing installed tool with the same name will be overwritten permanently. The history
will retain all the generating jobs if you accidentally overwrite a tool.

Refresh the page (by clicking the home icon or the "analysis" tab) to see them in the `ToolFactory Generated Tools` section and try them out.

Rerun the job and adjust the form. Rinse and repeat until ready.

The generated tool has not been run to generate test outputs, so the archive is not complete although the installed tool may work fine.

To generate a real, tested toolshed archive, use the companion `planemo_test` tool. Planemo will be run in a separate
container. The generated test outputs and the newly updated tested toolshed archive will appear in the history when ready.

The very first test in a fresh Appliance takes a few minutes as Conda installs some dependencies - only needed once. Subsequently more like a minute or two, depending on conda and the complexity of dependencies needed
for the tool to run.

## Tutorial

The sample tools provided in the Appliance are supported by a GTN tutorial PR, [available here on a private server](https://training.galaxy.lazarus.name/training-material/topics/dev/tutorials/tool-generators/tutorial.html).
An advanced tutorial showing some of the features available when building tools with the ToolFactory Appliance is linked at the end of the introductory tutorial.


## To safely shut the appliance down

`docker-compose down`

from the same place you started should shut it down nicely

## Specific security disclosures

If you use the ToolFactory for ordinary scripts, it will work without endangering the appliance. The details below explain how this is possible but they will not affecting your work,
unless you write tools that use any of the methods described below. If you do, please be mindful that it is possible to damage the appliance
by writing to the wrong places. Normal Galaxy security restrictions are removed to different degrees by these techniques. They are extremely powerful and generalisable but also
a risk if anyone hostile can access the server. They could destroy it if they know how so it is best to ensure that your appliance is not exposed anywhere.

1. The ToolFactory uses rsync to update the running Galaxy config/tool_conf.xml when a new tool is built. That should fail on a secured cluster production system
where rsync would need passwordless ssh to access the (remote) server disk. In the Appliance, rsync can write anywhere Galaxy can which is as handy as it is insecure. If
you choose to adapt the rsync code for a tool, please be careful. If you do accidentally break the Appliance, it takes only a few minutes to delete and
recreate the entire server from scratch if necessary.

2. The `planemo_test` tool calls an rpyc (old fashioned remote procedure call with a python twist) server to run planemo, and to write tested archives to exported
directories that tools should never be able to write, described in more detail below. It is even less secure than the rsync method having complete access to /export.
At present, that container runs as root - something that needs repair before long. The remote server will soon be restricted to run specific exported functions just for
the tester, so it will not be possible for a user to damage the system without changing that server code in the container. Again, extremely handy for integrating the
ToolFactory but also not for public internet exposure. Given that constraint, it offers a generalisable model for other potential private desktop Galaxy appliances.
They might be integrated with specialised local GPU or other hardware and services, in circumstances where the security risks are known and manageable, given benevolent users.

## Note on remote command execution for Galaxy tools in a private environment.

The Galaxy framework runs tools in a highly constrained and secure way. The job runner creates a tool execution environment that is very restricted in terms of resource access,
in order to protect the framework, data and database from accidental bugs overwriting critical files or even from malicious damage.

There may be circumstances where it is useful for a tool to be able to do things that are ill-advised and not possible in a normal, secure Galaxy server job runner.
A publicly accessible server is not suited to the methods described here. They introduce substantial security risks through deliberately impaired job security.
On the other hand, in a completely private, dedicated Docker appliance used by a developer, they might be an acceptable risk to the user.
After all, they are unlikely to deliberately damage their own development machine.
Even if they do, the Docker containers and associated local exported volumes can quickly be rebuilt from scratch, at the cost of losing any work done on the Appliance
and not backed up.
Before destroying a damaged local installation, generated tool archives can be found in the local `...compose/export/galaxy/tools/TFtools` directory.

The motivating use case for this deliberate security “work-around” is the requirement for the ToolFactory tool to immediately
install newly generated tools into the running Galaxy, and to test them with Planemo.
These are functions available in the ToolFactory appliance, a flavour of the docker-galaxy-stable core.
The Appliance adds automated post-installation configuration by a specialised server container based on the normal docker-galaxy-stable server.
As soon as the Galaxy server installation is completed, the additional container loads tools, demonstration data, history and workflows to provide the “flavour”.
It also starts a minimal Rpyc server capable of accepting commands from tools running in the Galaxy server container.
It is this rpyc server that is the key to running tasks independently of the normal Galaxy job runner system,
but triggered by a specially configured running tool.

The mechanism described here is a completely generic and completely insecure way to allow tools executing as normal Galaxy jobs to do things that
Galaxy security, very wisely would normally not permit. These impossible things may have other interesting applications but the cost of associated insecurity cannot be over emphasised.

The planemo test tool is the testing tool built in to the appliance uses the remote container server by making RPC calls.
The server invokes the command using the Python subprocess module inside the dedicated container. When the task completes, outputs are returned to the tool as a response.

For the ToolFactory, running Planemo as a tool to test tools has proven difficult.
It was not designed to work as a Galaxy tool and is difficult to manage when called by a tool running as a Galaxy job.
It was designed for command line use and works without problems in the dedicated container when called by the testing tool.
The running tool sets up a connection to the Rpyc server running in the dedicated container after rpyc is imported with:

>conn = rpyc.connect("planemo-server", port=9999,  config={'sync_request_timeout':1200})

Default docker bridge networking is used by the ToolFactory appliance, so the planemo server can be accessed using the container name.
Docker automatically permits the RPC calls to pass between the two containers.
After the connection is established, rpyc allows the tool code to run shell commands on the remote container and receive the outputs as a response,
with a blocking call to the Rpyc server such as:

>res = conn.root.run_cmd("planemo lint %s" % toolxml)

Assuming `toolxml` is the path of a valid Galaxy tool XML file, the output from the lint proceedure is returned to the calling tool as `res`.
From there can be written to a history item by the tool in the usual way.

The server is a bare-bones adaption of a sample from the Rpyc documentation. Note that the threadcount given as nbThreads allows only a single thread to run at any one time.
This is necessary because if two or more Planemo test tasks are installing dependencies, the Planemo Conda data is quickly corrupted since Conda and Planemo
have not been designed to run safely in parallel and do not perform any resource locking.
Other applications may be able to gain better throughput where rpyc can invoke multiple parallel threads or forks with the ForkingServer if preferred.

``` python
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
            if sp.returncode == 0:
                logging.info('retcode %d; cmd=%s' % (sp.returncode, cl))
            else:
                logging.info('### retcode %d NOT zero; cmd=%s; returned %s' % (sp.returncode, cl, outs))
            return(outs)


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(level='INFO')
    t = ThreadPoolServer(cmd_service, port=9999, logger=logger, nbThreads=1)
    # single thread - planemo/conda behave better
    t.start()
```



The ToolFactory Appliance runs as a private developer instance, and does not make use of security features offered by Rpyc such as authenticated connections
and exposing only constrained functions. These are easy to configure and would be recommended for a production environment where this remote
procedure call work-around is used.



Ross Lazarus May 2021
