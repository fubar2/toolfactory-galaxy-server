# Galaxy ToolFactory Appliance

## Tutorials are currently at [GTN ToolFactory developer's tutorial](https://training.galaxy.lazarus.name/training-material/topics/dev/tutorials/tool-generators/tutorial.html).

This appliance takes a basic Galaxy server configuration and creates a ToolFactory appliance in Docker by adding:

1.    A working copy of the ToolFactory - a form driven code generator to make new Galaxy tools from scripts
2.    A container that does post-install adjustment of the docker-compose and can test tools using planemo, returning the planemo test
report and updated archive to the user's current history magically
3.    A warning that it would be extraordinarily unwise to ever expose this appliance anywhere on the public internet. Please, just don't.

## Depends upon

This is a flavour of the docker-compose infrastructure copied from https://github.com/bgruening/docker-galaxy-stable - there is excellent documentation at
that site. Respect. A few minor pointers only are provided below - please refer to the original documentation for details about this extensive infrastructure for Galaxy flavours.


## WARNING!

**This appliance has been configured to "work around" some of Galaxy's normally very strict job runner isolation features**

Users are strongly discouraged from running it on any server accessible from the public internet and potential miscreants.
It is safe to run on a sanely secured laptop or desktop. It runs as a set of Docker containers so secured to that extent from the
host system. ToolFactory and other related source code is included in this repository for the curious or the dubious.

## Installation and startup

Something like this should get it started

```
git clone https://github.com/fubar2/toolfactory-galaxy-server
cd toolfactory-galaxy-server/compose
docker-compose pull
docker-compose up
```

 - Your appliance should be running with a local Galaxy on localhost:8080 after a fair bit of activity.
 - Watch the logs. They are very instructive and informative for those who need to understand how Galaxy actually works.

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

To generate a real, tested toolshed archive turn the test option on. After the tool is regenerated, Planemo will start running in a separate
container. The generated test output and the newly updated tested toolshed archive will appear magically in the history when ready.

The first test takes 6 minutes. Subsequently more like a minute, depending on conda and the complexity of dependencies needed
for the tool to run.

An archive containing the tool with proper test will be returned with the planemo report in the history.

## To safely shut the appliance down

`docker-compose down`

from the same place you started should shut it down nicely



Ross Lazarus May 2021
