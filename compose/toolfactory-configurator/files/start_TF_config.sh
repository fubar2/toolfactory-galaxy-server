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
  mkdir /export/galaxy/tested_TF_archives
  chown galaxy:galaxy /galaxy/tested_TF_archives
  mkdir /export/galaxy/tested_TF_reports
  chown galaxy:galaxy /export/galaxy/tested_TF_reports
  mkdir -p /galaxy
  cp -r /tools/* /galaxy/tools/
  cp -r /config/* /galaxy/config/
  cp /config/base.css /galaxy/static/dist/base.css
  cp -r /workflows /export/galaxy/workflows
  cp /config/welcome.html /galaxy/static/welcome.html
  chown -R galaxy:galaxy /galaxy/config
  chown -R galaxy:galaxy /galaxy/tools
  chown -R galaxy:galaxy /galaxy/static
  sudo -H -u galaxy bash -c '. /galaxy/.venv/bin/activate ; python3 -m pip install -U pip; python3 -m pip install watchdog ; deactivate'
  echo "#### PLEASE STAND BY - waiting before restarting Galaxy. Should be inactive!"
  bash -c ". /venv/bin/activate ; python /usr/local/bin/waitforquiet.py"
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
echo "## All configuration done. Please wait for Conda to finish and only then, login and enjoy your ToolFactory Appliance"
bash -c "cd /planemo ; . /venv/bin/activate ; python3 /usr/local/bin/planemo_rpyc.py"
# this needs root sadly.
while [ 1 ]
do
# so we can restart above for testing
    sleep 1h
done
