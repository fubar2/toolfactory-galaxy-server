# Galaxy ToolFactory Appliance

## A [GTN ToolFactory developer tutorial PR is in beta testing on a private server](https://training.galaxy.lazarus.name/training-material/topics/dev/tutorials/tool-generators/tutorial.html).

This Appliance takes the basic docker server configuration and creates a ToolFactory appliance in Docker by adding:

1.    A working copy of the ToolFactory - a form driven code generator to make new Galaxy tools from scripts
2.    A container that does post-install adjustment of the docker-compose to add the ToolFactory flavour. It runs planemo, to test tools, returning the planemo test
reports, log and updated archive to the user's current history.
3.    A warning that it would be extraordinarily unwise to ever expose this appliance anywhere on the public internet. Please, just don't. Read on to learn why.

## Depends upon

This is a flavour of the docker-compose infrastructure copied from https://github.com/bgruening/docker-galaxy-stable - there is excellent documentation at
that site. Respect. A few minor pointers only are provided below - please refer to the original documentation for details about this extensive infrastructure for Galaxy flavours.


## WARNING!

**This appliance has been configured to "work around" some of Galaxy's normally very strict job runner isolation features**

Users are advised **not to run it on any server accessible from the public internet and potential miscreants**.
It is safe to run on a normally secured Linux laptop or desktop. It runs as a set of Docker containers, so it is secured to that extent from the
host system. ToolFactory and other related source code is included in this repository for the curious or the dubious. The rpyc remote procedure call
server and calling client code are described below.

## Installation and startup

Something like this should get it started

```
git clone https://github.com/fubar2/toolfactory-galaxy-server
cd toolfactory-galaxy-server/compose
docker-compose pull
docker-compose up
```

 - Your appliance should be running with a local Galaxy on localhost:8080 after a fair bit of activity.
 - Watch the logs as they scroll by on the terminal. They are very instructive and informative for those who need to understand how Galaxy actually works.

- Out of the box login is `admin@galaxy.org` and the password is `password`
- This is obviously insecure but convenient and easily changed at first login.
- Change it more permanently in docker-compose.yml if you intend to use this Appliance for your own work.
  - Please also change the admin_key from the default`fakekey` to something less well known
  - The API key is the administrative key for the appliance Galaxy so if you are exposed on any large network, you are
exposed to easy API based remote mischief until it is changed.

The container `/export` directory is mounted locally at `compose/export` .

## Demonstration tools are the functional documentation

Follow the welcome page instructions to start exploring how they were built by rerunning the generating job to recreate the ToolFactory form
for the run and looking at the settings for each one to see what can be done.

To view the form that generated each job, open the toolshed archive or the XML by clicking on it, and select the `rerun` button.
Edit the form and rerun to create an updated tool. The history has previous versions.
Change the tool ID to change the tool name.

## Generating your own tools

Generated tools are installed on build. The whole process takes a few seconds.
Choose the names thoughtfully and be warned: there are no checks on tool names - any existing installed tool with the same name will be overwritten permanently. The history
will retain all the generating jobs if you accidentally overwrite a tool.

Refresh the page (by clicking the home icon or the "analysis" tab) to see them in the `ToolFactory Generated Tools` section and try them out.

Rerun the job and adjust the form. Rinse and repeat until ready.

The generated tool has not been run to generate test outputs, so the archive is not complete although the installed tool may work fine.

To generate a real, tested toolshed archive, use the companion `planemo_test` tool. Planemo will be run in a separate
container. The generated test outputs and the newly updated tested toolshed archive will appear in the history when ready.

The first test takes 6 minutes. Subsequently more like a minute or two, depending on conda and the complexity of dependencies needed
for the tool to run.


## To safely shut the appliance down

`docker-compose down`

from the same place you started should shut it down nicely


## Note on remote command execution for Galaxy tools in a private environment.

The Galaxy framework runs tools in a highly constrained and secure way. The job runner creates a tool execution environment that is very restricted in terms of resource access, in order to protect the framework, data and database from accidental bugs overwriting critical files or even from malicious damage.

There may be circumstances where it is useful for a tool to be able to do things that are ill-advised and not possible in a normal, secure Galaxy server job runner. A publicly accessible server is not suited to the methods described here. They introduce substantial security risks through deliberately impaired job security. On the other hand, in a completely private, dedicated Docker appliance used by a developer might be an acceptable risk to the user. After all, they are unlikely to deliberately damage their own development machine. Even if they do damage, the cost is minimal because the Docker containers and associated local exported volumes can quickly be rebuilt from scratch.

The motivating use case for this deliberate security “work-around” is the requirement for the ToolFactory tool to install newly generated tools into the running Galaxy, and to test them with Planemo. These are functions available in the ToolFactory appliance, a flavour of the docker-galaxy-stable core. The Appliance adds automated post-installation configuration by a specialised server container based on the normal docker-galaxy-stable server. As soon as the Galaxy server installation is completed, the additional container loads tools, demonstration data, history and workflows to provide the “flavour”. It also starts a minimal Rpyc server capable of accepting commands from tools running in the Galaxy server container. It is this rpyc server that is the key to running tasks independently of the normal Galaxy job runner system, but triggered by a specially configured running tool - the planemo test tool.

The testing tool built in to the appliance uses the remote container server by making RPC calls. The server invokes the command using the Python subprocess module inside the dedicated container. When the task completes, outputs are returned to the tool as a response.

For the ToolFactory, running Planemo to test tools has proven difficult. It was not designed to work as a Galaxy tool and is difficult to manage when called by a tool running as a Galaxy job. It was designed for command line use and works without problems in the dedicated container when called by the testing tool. Only a few lines of Python code are needed for the running tool to connect to the Rpyc server running in the dedicated container:


>import rpyc
>conn = rpyc.connect("planemo-server", port=9999,  config={'sync_request_timeout':1200})

Default docker networking is used by the ToolFactory appliance, so the remote server can be accessed using just the container name. Docker automatically permits the RPC calls to pass between the two containers. After the connection is established, the tool code can run shell commands on the remote container and receive the output with a call to the Rpyc server such as:

>res = conn.root.run_cmd("planemo lint %s" % toolxml)

The output from the lint proceedure is returned to the calling tool as res and from there can be sent to a history item by the tool in the usual way.

The server is a minor adaption of simple samples from the Rpyc documentation. Note that the threadcount given as nbThreads allows only a single thread to run at any one time. This is
necessary because if two or more Planemo test tasks are installing dependencies, the Planemo Conda data is quickly corrupted since Conda and Planemo have not been designed to
provide any resource locking.

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



The ToolFactory runs as a private developer appliance, and does not make use of security features offered by Rpyc such as authenticated connections
and exposing only constrained functions. These are easy to configure and would be recommended for a production environment where this remote
procedure call work-around is used.


Ross Lazarus May 2021
