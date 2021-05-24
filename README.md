# Galaxy ToolFactory Appliance

This is a ToolFactory flavoured developer appliance in Docker extending the basic `docker-galaxy-stable` composition.

1.    The ToolFactory - a form driven code generator to make new Galaxy tools from scripts - is installed with a testing tool.
2.    A container for post-install configuration is added to create the ToolFactory flavour. The new container then runs a planemo server
outside the Galaxy tool execution environment to test tools, returning the planemo test
reports, log and updated archive to the user's current history.
3.    A history containing 15 demonstration tool generation jobs to rerun and build on. Samples use bash, python, perl (yes, even perl. Galaxy is a very welcoming community..),
Rscript and for more discerning users, prolog and lisp. Any scriptable language in Conda should work.

## Built on docker-galaxy-stable

This flavour of the docker-compose infrastructure is based on https://github.com/bgruening/docker-galaxy-stable - there is excellent documentation at
that site. Respect. A few minor pointers only are provided below - please refer to the original documentation for details about this extensive infrastructure for Galaxy flavours including
(untested) cluster and other deployment options.

## A standalone, pop-up desktop Galaxy appliance

The Appliance supporting the ToolFactory is a fully featured `docker-galaxy-stable` Galaxy server, ideal for scientists and developers
who can use a private pop-up desktop server for learning how Galaxy works, building new tools, using interactive environments and any available toolshed tools to do real work,
potentially at scale. The Appliance adds only one specific container. The others are all pulled from Björn's docker-galaxy-stable quay.io containers.


## Private desktop use only is recommended.

This Appliance has been configured to weaken some of Galaxy's strict job-runner isolation features so it can install and test tools conveniently.
It is safe to run on a private Linux laptop or workstation.

**Running it on any server accessible from the public internet exposes it to potential miscreants. This is strongly discouraged**.

Although Galaxy's job execution security is very tight and safe, allowing potentially hostile users to build and then immediately run their own tools exposes any production server
to unwelcome security risk.

The Appliance runs as a set of Docker containers, so it is secured to that extent from the host system. ToolFactory and other related source code is
included in this repository for the curious or the dubious. Specific security disclosure details are discussed in the compose documentation. The mechanisms described offer a
convenient way for tools to remotely execute tasks outside the Galaxy job execution environment in suitably private environments such as this Appliance.
This may open up interesting uses for Galaxy on the desktop with specialised tools accessing GPU or other local resources.

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

Generated tools are installed on build. The whole process takes a few seconds normally. Refreshing the Galaxy panel will be needed for the tool menu to be updated after the
newly generated tool is installed. It will be found in the `ToolFactory Generated Tools` section.

A new tool requiring Conda dependencies will take time as those must be installed the first time it is run. After that first run or if the dependency is already installed,
the tool will run without delay.

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

## Security - why this Appliance is not suitable for exposing on the public internet

See [the notes on Appliance security considerations.](https://github.com/fubar2/toolfactory-galaxy-server/tree/main/compose#readme)
