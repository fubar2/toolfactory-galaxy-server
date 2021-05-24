# ToolFactory Appliance

## Some docker-galaxy-stable compose configuration notes

base-config.yml is used to alter a number of Galaxy and in particular uwsgi settings. This is neat because the stock galaxy-server image can be used unaltered.
The uwsgi process watches the touch-restart file so the configurator can reboot the server after making changes.
This requires that it operate as `master` but that is a good idea anyway probably..
Galaxy configuration includes turning on the tool change watchdog so Galaxy will update the tool panel after changes are noted.
The ToolFactory configuration completes but the container continues to run, providing a service described in detail below.


## Security disclosures

If you use the ToolFactory for ordinary scripts, it will work without endangering the Appliance. The details below explain how this is possible.

The mechanisms used will not affect your work unless you write tools that use the methods described below.
If you do, please be mindful that it is possible to damage the appliance
by writing to the wrong places. Normal Galaxy security restrictions are removed to different degrees by these techniques. They are extremely powerful and generalisable but also
a risk if anyone hostile can access the server. Best to ensure that your Appliance is not exposed on the public internet.

More importantly, **any tools written using the Appliance that use either the server or rsync will always fail on a normally secured Galaxy server**, so they are
useless for sharing on the Toolshed. They will only work in a copy of this Appliance or something derived from it.

### Rsync

The ToolFactory uses rsync to update the running Galaxy config/tool_conf.xml when a new tool is built. That will fail on a normal Galaxy installation or
a secured cluster production system where rsync would need passwordless ssh to access the (remote) server disk. In the Appliance,
rsync can write anywhere Galaxy can which is as handy as it is insecure. If you choose to use rsync for a tool, remember it will not work in other
Galaxy servers and please, be careful where you write. If you do accidentally break the Appliance, it takes only a few minutes to delete and recreate the entire
server from scratch if necessary.


### rpyc

The `planemo_test` tool calls an rpyc (remote procedure call in python) server to run planemo, and to write tested archives to exported
directories that tools should never be able to write, described in more detail below. It is far more restricted than the rsync method because only a single function
is (currently) exposed. However, it is easy to change what the server exposes. It runs as root and has access to everything in the container so it is wise to
expose only very specific and limited functions that cannot be exploited for malicious use of this powerful resource.
The remote server only exposes specific exported functions, currently only useful for
the `planemo_test` tool, so it will not be possible for a hostile user to damage the system without changing that server code running in the toolfactory-galaxy-server container.

### Risks and value proposition

These techniques are completely unsupported by the Galaxy developers. They are handy for integrating the ToolFactory but not recommended for
public internet exposure. They offer generalisable models for other
potential private desktop Galaxy appliances. These might use locally generated ToolFactory tools modelled on the `planemo_lint` tool, integrated with GPU or other
hardware or specialised services such as data acquisition and preprocessing, that are not otherwise readily available in Galaxy.

## Details: Remote command execution for Galaxy tools in a private environment.

The Galaxy framework runs tools in a highly constrained and secure way. The job runner creates a tool execution environment that is very restricted in terms of resource access,
in order to protect the framework, data and database from accidental bugs overwriting critical files or even from malicious damage.

There may be circumstances where it is useful for a tool to be able to do things that are ill-advised and not possible in a normal, secure Galaxy server job runner.
A publicly accessible server is not suited to the methods described here. They introduce substantial security risks through deliberately impaired job security.
On the other hand, in a completely private, dedicated Docker appliance used by a developer, those risks might be accepted in return for the functionality provided.
The developer is unlikely to act maliciously. Even if they do accidentally damage the system, the Docker containers and associated local exported disk
volumes can be rebuilt from scratch, at the cost of about 10 minutes and the loss any work done on the Appliance but not backed up.
Before destroying a damaged local installation, tested tool archives can be found in the local `...compose/export/galaxy/tested_TF_tools` directory.

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

### rpyc makes RPC trivially easy to implement.

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

The threadcount given as nbThreads in the planemo_rpyc.py server code is 1. This may seem strange but it is necessary to only allow a single planemo job to run at any one time.
If two or more task attempt to install dependencies at the same time, the Conda data can become corrupted since Conda and Planemo
have not been designed to run safely in parallel. They do not perform any resource locking but a single thread effectively does so for them.

Other applications could gain better throughput if rpyc can invoke multiple non-interfering parallel threads. A separate service with higher threadcount could
easily be added with concurrency provided transparently by rpyc to suit available CPU capacity.

### Securing the rpyc server further

The ToolFactory Appliance runs as a private developer instance, and does not make use of security features offered by rpyc such as authenticated connections.
This is easy to configure for a production environment where this remote procedure call work-around is used.

### The challenge of tools that will not run in a normally secured Galaxy

This Appliance raises the question of how to quarantine tools that use resources not normally available on a public Galaxy server. Tools generated with the ToolFactory that
do not use any of the rpyc or rsync tricks will run in any normal Galaxy so do not need to be restricted in any way.

Ross Lazarus May 2021
