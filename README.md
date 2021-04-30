This is mostly copied from https://github.com/bgruening/docker-galaxy-stable - it has excellent documentation at
that site not repeated here.

It adds:
1.    watchdog support for detecting new tools
2.    an external tool directory watchdog to run Planemo test and update all newly updated toolshed archives that are all stored in /export/galaxy/tooltardir

It supports the ToolFactory and was built for the GTN ToolFactory tutorial

Ross Lazarus April 2021
