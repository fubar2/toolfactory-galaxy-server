# ToolFactory Appliance

## Some docker-galaxy-stable configuration notes

Docker-galaxy-stable runs in one container. Another runs a configurator that supplies most of the flavour after the server settles down. It
installs workflows and the sample history then runs a server listening for RPC calls.

Configuration includes turning on the tool change watchdog so Galaxy will update the tool panel after changes are noted.
The ToolFactory configuration completes but the container continues to run, providing a service described in detail below.
Users are advised to ignore these functions and write normal, portable tools.

## How does the ToolFactory do things that are not possible in a normal Galaxy server?

They are described here because they may be useful to anyone wanting non-portable tools to have easy access to external functions in a private deployment.

This will not affect your work, unless you choose to write tools that use the RPC method described below.

If you do, please be mindful that it is possible to damage the appliance
by writing to the wrong places. Normal Galaxy security restrictions are effectively bypassed by these techniques.
Also remember that **tools written to use rpyc will always fail on a normal Galaxy server**, so they are
useless for sharing on the Toolshed. They will only work in a copy of this Appliance or something derived from it that offers a similar rpyc server. Tools written
without rpyc will work in any Galaxy server.


### Security disclosure: rpyc is used in the Appliance

Both the `ToolFactory` and the`planemo_test` tools call an rpyc (remote procedure call in python) server to do things a normal Galaxy server does not permit,
described in more detail below. Two functions are (currently) exposed and some more generalised and powerful ones are hidden from callers.
It is easy to write code to change the functions exposed by the server.
It runs as root and has access to everything in the container so it is wise to expose only very specific and limited functions that cannot be
exploited for malicious use of this powerful resource. The remote server only exposes specific exported functions, currently only useful for
the Appliance tool generator and tester, so it will not be possible for a hostile user to damage the system without changing
that server code running in the toolfactory-configurator container.

### Risks and value proposition

This technique is completely unsupported by the Galaxy developers. It is handy for integrating the ToolFactory but not recommended for
public internet exposure. It offers interesting and generalisable models for other possible private desktop Galaxy appliances. These might use
locally generated ToolFactory tools modelled on the included `planemo_test` tool, but with rpyc functions that exposes hardware or specialised services
such as data acquisition and preprocessing to calling tools that are not otherwise readily available to a tool in a normal Galaxy server.

## Details: Remote command execution for Galaxy tools in a private environment.

The Galaxy framework runs tools in a highly constrained and secure way. The job runner creates a tool execution environment that is very restricted in terms of resource access,
in order to protect the framework, data and database from accidental bugs overwriting critical files or even from malicious damage.

The ToolFactory Appliance is an example illustrating that there may be circumstances where it is useful for a tool to be able to do things that are ill-advised and not possible
in a normal, secure Galaxy server job runner. A publicly accessible server is not suited to the methods described here. They introduce substantial security risks through
bypassing normal job file access limits.

In a completely private, dedicated Docker appliance used by a developer, the small additional risk might be acceptable in return for the functionality available.
The developer is unlikely to act maliciously. Even if they do accidentally damage the system, the Docker containers and associated local exported disk
volumes can be rebuilt from scratch, at the cost of about 10 minutes and the loss any unsaved work done on the Appliance.
Before destroying a damaged local installation, tested tool archives can be found in the local `...compose/export/galaxy/tested_TF_archives` directory.

### Why would anyone want to do this?

The motivating use case for this deliberate security “work-around” is the requirement for the ToolFactory tool to immediately
install newly generated tools into the running Galaxy, and to test them with Planemo.

These are functions available in the ToolFactory appliance, a flavour of the docker-galaxy-stable core.
The Appliance adds automated post-installation configuration by a specialised server container based on the normal docker-galaxy-stable server.
As soon as the Galaxy server installation is completed, the additional container loads tools, demonstration data, history and workflows to provide the “flavour”.

It also starts a minimal `rpyc` server capable of accepting commands from tools running in the Galaxy server container.
It is this rpyc server that is the key to running tasks independently of the normal Galaxy job runner system,
when triggered by a specially configured running tool.

### What uses could there be for a generic RPC for tools?

The approach described here is a generic way to allow tools executing as normal Galaxy jobs to do things that
Galaxy job security would normally not permit. These things may have other interesting applications
but the potential cost of associated potential security risk of unlimited scripting must be taken into account outside private settings.

The ToolFactory tool uses the rpyc server to invoke a function that installs a new tool by updating the tool_conf.xml configuration file and
writing the new tool to the `tools` directory. Without that server, these steps are not normally possible. While other tools might be
written to call the exposed functions, that's all they can do so risk is low.

The `planemo_test` tool uses the remote container server by making RPC calls.
The server exposes a single highly specialised and restricted function to test and lint a tool.
It uses but does not expose the Python subprocess module inside the dedicated container to run individual commands including
running planemo to lint and test the tool. When the task completes, the tool finishes up by moving some of the outputs.

For the ToolFactory project, running Planemo test as a tool to test tools has proven difficult.
It was not designed to work as a Galaxy tool and is difficult to manage when called by a tool running as a Galaxy job.
It was designed for command line use and works without problems in the dedicated container when called by the testing tool as if it had
been called on a command line.


### rpyc makes RPC trivially easy to implement using python functions.

The running tool sets up a connection to the rpyc server running in the dedicated container after rpyc is imported with:

```python
conn = rpyc.connect('planemo-server', port=9999, config={'sync_request_timeout':1200})
```

Default docker bridge networking is used by the ToolFactory appliance, so the planemo server can be accessed using the container hostname.
Docker default bridge networking permits the RPC calls to pass between the two containers.
After the connection is established, rpyc allows the tool code to call explicitly exported functions on the remote server and receive the outputs as a response,
with a blocking call to the Rpyc server such as:

```python
res = conn.root.planemo_lint_test(xmlin, collectionpath)
```

The provided rpyc server exposes one function that runs planemo test and lint on the tool passed as the parameter. It uses a generic command line
runner but this function is not exposed to RPC callers directly. It also exposes a function used by the ToolFactory to update the
`..config/tool_conf.xml` after writing the new tool to `tools/TFtools` - things no job running on a normal, secure Galaxy server is allowed to do.

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
do not use any of the rpyc tricks will run in any normal Galaxy so do not need to be restricted in any way.

Ross Lazarus May 2021
