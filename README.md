# This is a Galaxy ToolFactory appliance built for the GTN ToolFactory tutorial.

The docker-compose infrastructure is copied wholesale from https://github.com/bgruening/docker-galaxy-stable - the excellent documentation at
that site is not repeated here. Respect. A few minor pointers only are provided below - please refer to the original documentation for details.

This appliance takes a basic Galaxy server configuration and creates a ToolFactory appliance in Docker by adding:

1.    A working copy of the ToolFactory - a form driven code generator to make new Galaxy tools from scripts
2.    A warning that it would be extraordinarily unwise to ever expose this appliance anywhere on the public internet. Please, just don't.

## WARNING!
**This appliance has been deliberately configured to "work around" some of Galaxy's normally very strict job runner isolation security**

Running it on any server accessible from the public internet and potential miscreants is strongly discouraged as a result.
It is safe to run on a laptop or desktop and runs as a docker-compose set of containers.
ToolFactory and other related source code is included in this repository for the curious.

## Installation and startup

Something like this should get it started - singularity is essential for the planemo tester to work:

```
git clone https://github.com/fubar2/toolfactory-galaxy-server
cd toolfactory-galaxy-server/compose
docker-compose -f docker-compose.yml -f docker-compose.singularity.yml up -d
```

Your appliance should be running with a local Galaxy on localhost:8080 after a fair bit of activity.

Out of the box login is 'admin@galaxy.org' and the password is 'password'
This is obviously insecure but convenient and easily changed at first login.

The container `/export` directory is mounted locally at `compose/export` .
Take a look there to find tested archives you generated (see GTN tutorial for details) in `export/galaxy/tested_TF_tools`

## Demonstration tools are the functional documentation

Follow the welcome page instructions to load the sample tools and start exploring how they were built by
looking at the settings for each one to see what can be done.

To view the form that generated each job, open the tool's history collection, open one of the files and select the `rerun` button.

## Generating your own tools

Generated tools are installed on build. The whole process takes a few seconds.
Choose the names thoughtfully.
There are no checks - any tool with the same name will be overwritten permanently.

Refresh the page (by clicking the home icon or the "analysis" tab) to see them in the ToolFactory section and try them out.

Rerun the job and adjust the form. Rinse and repeat until ready.

The generated tool has not been run to generate test outputs, so the archive is not complete although the installed tool may work fine.

To generate a real, tested toolshed archive, use the ToolFactory generated planemo_test tool.
It will run planemo to generate outputs, then run a real test and return a proper toolshed archive.

The first test takes 6 minutes. Subsequently more like 40 seconds depending on conda and the complexity of dependencies needed
for the tool to run.

## To safely shut the appliance down

`docker-compose down`

from the same place you started should shut it down nicely



Ross Lazarus April 2021
