#!/bin/bash
# seem to need a delay here
# needs changes to base_config.yml to enable master and touch-reload on uwsgi and watchdog: auto for galaxy
# http://192.168.1.9:8080/api/histories returns nothing until the server is good to go
/usr/bin/sleep 50s
echo "slept well.."
DONEONCE="0"
if [ -f "/export/galaxy/tools/toolfactory/ToolFactory.xml" ]; then
  DONEONCE="1"
  echo "configurator found the toolfactory already present so not installing anything"
else
  echo "configurator found no toolfactory - loading sample history and overwriting configs as needed"
  chown -R galaxy:galaxy /config
  chown -R galaxy:galaxy /tools
  chown galaxy:galaxy /welcome.html
  #cp /Singularity.def /export/galaxy/database/container_cache/singularity/mulled/
  sudo -H -u galaxy bash -c 'cp -r /tools/* /export/galaxy/tools/'
  sudo -H -u galaxy bash -c 'cp -r /config/* /export/galaxy/config/'
  sudo -H -u galaxy bash -c 'cp /welcome.html /export/galaxy/static/welcome.html'
  sudo -H -u galaxy bash -c '. /export/galaxy/.venv/bin/activate ; python3 -m pip install -U pip; python3 -m pip install watchdog ; deactivate'
  echo "#### PLEASE STAND BY - waiting before restarting Galaxy. Should be inactive!"
  /usr/bin/sleep 5s
  echo "#### Restarting Galaxy."
  touch /export/galaxy/config/reload_uwsgi.touchme
  chown galaxy:galaxy /export/galaxy/config/reload_uwsgi.touchme
  /usr/bin/sleep 20s
  echo "configurator is installing the demonstration history"
  sudo -H -u galaxy bash -c '. /venv/bin/activate ; python3 /config/install-history.py ; deactivate'
  mkdir /export/galaxy/tested_TF_tools
  chown galaxy:galaxy /export/galaxy/tested_TF_tools
  mkdir /export/galaxy/tested_TF_reports
  chown galaxy:galaxy /export/galaxy/tested_TF_reports
fi
# run toolwatcher watchdog to trigger planemo tests when requested by toolfactory
touch /export/galaxy/toolwatcher.log
chown galaxy:galaxy /export/galaxy/toolwatcher.log
cd /export/galaxy ; bash -c ". /venv/bin/activate ; python3 /usr/local/bin/planemo_rpyc.py"
echo "## All done. Please login and enjoy your ToolFactory Appliance"
while [ 1 ]
do
# so we can restart above for testing
    sleep 1h
done
