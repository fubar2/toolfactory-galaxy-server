This is a Galaxy ToolFactory appliance built for the GTN ToolFactory tutorial.

The docker-compose is all copied wholesale from https://github.com/bgruening/docker-galaxy-stable - the excellent documentation at
that site is not repeated here. Respect.

It adds:
1.    A working copy of the ToolFactory
1.    A background watchdog process to trigger testing when requested.
2.    Background Planemo testing generates a tested toolshed archive in `/export/galaxy/tested_TF_tools`


Something like this should get it started.
```
git clone https://github.com/fubar2/toolfactory-galaxy-server
cd toolfactory-galaxy-server/compose
docker-compose up -d
```

Your appliance should be available on localhost:8080 after a fair bit of activity.

Follow the welcome page instructions to load the samples and start playing with them to see what can be done.
To rerun any job, open the tool's collection, open one of the files and use the `rerun` button.

Generated tools are installed on build. The whole process takes a few seconds. 
The generated tool has not been run to generate test outputs, so the test is not complete. 
Long story. It can be generated when you are ready as described below.

Refresh the page to see them in the ToolFactory section and try them out.

Rerun the job and adjust the form. Rinse and repeat until ready.

Rerun with the test option selected when you are ready. You will see lots of activity on the server, but nothing 
happening in Galaxy because the test/update process is running independently of Galaxy and eventually will write
a new tested toolshed archive.

The /export directory is mounted to compose/export so take a look there to find any tested archives you generated.
The first test takes 6 minutes. Subsequently more like 40 seconds depending on conda and the complexity of dependencies needed
for the tool to run.

`docker-compose down`

from the same place you started should shut it down nicely



Ross Lazarus April 2021
