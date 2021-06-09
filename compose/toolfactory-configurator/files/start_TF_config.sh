#!/bin/bash
/venv/bin/python /usr/local/bin/waitforquiet.py
# should only return when the admin exists and no jobs running
echo "slept well.."
DONEONCE="0"
if [ -f "$GALAXY_ROOT/config/.TFDONE" ]; then
  DONEONCE="1"
  echo "configurator found the toolfactory already present so not installing anything"
else
  echo "configurator found no toolfactory - loading sample history and overwriting configs as needed"
  cp -r /files/ /galaxy-central/workflows/
  bash -c ". /venv/bin/activate && python /usr/local/bin/waitforquiet.py"
  echo "Configurator will install the demonstration history and workflows"
  sudo -H -u galaxy bash -c '. /venv/bin/activate && shed-tools install -g "http://galaxy-server" -a fakekey -t /galaxy-central/tools.yaml'
  bash -c ". /venv/bin/activate && python /usr/local/bin/waitforquiet.py"
  sudo -H -u galaxy bash -c  '. /venv/bin/activate && python3 /usr/local/bin/install-history.py'
  bash -c ". /venv/bin/activate && python /usr/local/bin/waitforquiet.py"
  touch "$GALAXY_ROOT/config/.TFDONE"
fi
# run rpyc server to trigger planemo tests when requested by toolfactory
echo "## Configuration done. If this is the first run, please wait for Conda to finish and only then, login and enjoy your ToolFactory Appliance"
bash -c "cd /planemo ; . /venv/bin/activate ; python3 /usr/local/bin/planemo_rpyc.py"
# this needs root but exposes specific and limited functions to currently unsecured visitors. Configure rpyc ssh key authentication if needed.
while [ 1 ];
do
# so we can restart above for testing
    sleep 1h
done
