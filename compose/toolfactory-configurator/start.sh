#!/bin/bash
# seem to need a delay here
# needs changes to base_config.yml to enable master and touch-reload on uwsgi and watchdog: auto for galaxy
# http://192.168.1.9:8080/api/histories returns nothing until the server is good to go
/venv/bin/python /usr/local/bin/waitforquiet.py
# should only return when the admin exists and no jobs running
echo "slept well.."
DONEONCE="0"
if [ -f "/export/galaxy/tools/toolfactory/ToolFactory.xml" ]; then
  DONEONCE="1"
  echo "configurator found the toolfactory already present so not installing anything"
else
  echo "configurator found no toolfactory - loading sample history and overwriting configs as needed"
  mkdir /export/galaxy/tested_TF_tools
  chown galaxy:galaxy /export/galaxy/tested_TF_tools
  mkdir /export/galaxy/tested_TF_reports
  chown galaxy:galaxy /export/galaxy/tested_TF_reports
  #cp /Singularity.def /export/galaxy/database/container_cache/singularity/mulled/
  cp -r /tools/* /export/galaxy/tools/
  cp -r /tools/TFtools /export/galaxy/tools/TFtools/
  cp -r /config/* /export/galaxy/config/
  cp /config/welcome.html /export/galaxy/static/welcome.html
  chown -R galaxy:galaxy /export/galaxy/config
  chown -R galaxy:galaxy /export/galaxy/tools
  chown -R galaxy:galaxy /export/galaxy/static
  sudo -H -u galaxy bash -c '. /export/galaxy/.venv/bin/activate ; python3 -m pip install -U pip; python3 -m pip install watchdog ; deactivate'
  chown -R galaxy:galaxy /export/tool_deps
  echo "#### PLEASE STAND BY - waiting before restarting Galaxy. Should be inactive!"
  /venv/bin/python /usr/local/bin/waitforquiet.py
  echo "#### Restarting Galaxy. Job queue seems empty"
  touch /export/galaxy/config/reload_uwsgi.touchme
  chown galaxy:galaxy /export/galaxy/config/reload_uwsgi.touchme
  bash -c ". /venv/bin/activate ; python /usr/local/bin/waitforquiet.py"
  echo "configurator is installing the demonstration history"
  sudo -H -u galaxy bash -c  '. /venv/bin/activate ; python3 /usr/local/bin/install-history.py'
fi
# run rpyc server to trigger planemo tests when requested by toolfactory

chown -R galaxy:galaxy /home/galaxy
bash -c "cd /planemo ; . /venv/bin/activate ; python3 /usr/local/bin/planemo_rpyc.py"
echo "## All configuration done. Please login and enjoy your ToolFactory Appliance"
while [ 1 ]
do
# so we can restart above for testing
    sleep 1h
done
