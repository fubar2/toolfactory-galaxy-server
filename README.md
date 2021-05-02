This is copied from https://github.com/bgruening/docker-galaxy-stable - the excellent documentation at
that site is not repeated here. Respect.

It adds:
1.    watchdog support for detecting new tools
2.    an external tool directory watchdog to run Planemo test and generate a tested toolshed archive, stored in `/export/galaxy/tested_TF_tools`

It is the ToolFactory appliance built for the GTN ToolFactory tutorial

Something like this should get you going.
```
git clone https://github.com/fubar2/toolfactory-galaxy-server
cd toolfactory-galaxy-server/compose
docker-compose up
```

Your appliance should be available on localhost:8080
Follow the welcome page instructions to load the samples and start playing with them to see what can be done.
To rerun any job, open the tool's collection, open one of the files and use the `rerun` button.

Generated tools are installed on build.
Refresh the page to see them in the ToolFactory section and try them out.
Rerun the job and adjust the form. Rinse and repeat until ready.
Rerun with the test option set to (eventually) generate a tested toolshed archive.

`docker-compose down`

from the same place you started should shut it down nicely

The /export directory is mounted to compose/export so take a look there to find any tested archives you generated.
The first test takes 6 minutes. Subsequently more like 40 seconds depending on conda and the complexity of dependencies needed
for the tool to run.


Ross Lazarus April 2021
