#!/bin/bash
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
  cp -r /tools /export/galaxy
  cp -r /config /export/galaxy
  cp /config/base.css /export/galaxy/static/dist/
  cp -r /workflows /export/galaxy
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
  sudo -H -u galaxy bash -c '. /venv/bin/activate ; shed-tools install -g "http://nginx" -a "fakekey" -t "/config/TFtools.yml"'
  sudo -H -u galaxy bash -c  '. /venv/bin/activate ; python3 /usr/local/bin/install-history.py'
fi
# run rpyc server to trigger planemo tests when requested by toolfactory

chown -R galaxy:galaxy /home/galaxy
echo "## All configuration done. Please login and enjoy your ToolFactory Appliance"
bash -c "cd /planemo ; . /venv/bin/activate ; python3 /usr/local/bin/planemo_rpyc.py"
# this needs root sadly.
while [ 1 ]
do
# so we can restart above for testing
    sleep 1h
done
