# Galaxy - ToolFactory flavour

FROM quay.io/bgruening/galaxy:20.09

MAINTAINER ross.lazarus@gmail.com

ENV GALAXY_CONFIG_BRAND="ToolFactory" ENABLE_TTS_INSTALL=True GALAXY_ROOT="/galaxy-central" \
 GALAXY_CONFIG_TOOL_PATH="/galaxy-central/tools/" \
 GALAXY_CONFIG_WATCH_TOOLS=True\
 UWSGI_MASTER=True \
 #UWSGI_TOUCH_RELOAD="$GALAXY_ROOT/config/reload_uwsgi.touchme" \
 UWSGI_ENABLE_THREADS=True

# Install tools
COPY ./files/TFtools.yml $GALAXY_ROOT/tools.yaml
COPY ./files/datatypes_conf.xml $GALAXY_CONFIG_DIR/datatypes_conf.xml


RUN $GALAXY_VIRTUAL_ENV/bin/python -m pip install --upgrade pip \
    && install-tools $GALAXY_ROOT/tools.yaml \
    && /tool_deps/_conda/bin/conda clean --tarballs \
    && mkdir -p /export$GALAXY_ROOT/tested_TF_archives \
    && chown -R galaxy:galaxy  /export$GALAXY_ROOT/tested_TF_archives \
    && mkdir /export/$GALAXY_ROOT/tested_TF_reports \
    && chown -R galaxy:galaxy /export$GALAXY_ROOT/tested_TF_reports \
    && chown -R galaxy:galaxy $GALAXY_ROOT/tools \
    && ansible localhost -m lineinfile -a "path=${GALAXY_CONFIG_FILE} regexp='^  master:' line='  master: true'" \
    && ansible localhost -m lineinfile -a "path=${GALAXY_CONFIG_FILE} regexp='^  watch-tools:' line='  watch_tools: true'" \
    && ansible localhost -m lineinfile -a "path=${GALAXY_CONFIG_FILE} regexp='^  #conda_auto_install:' line='  conda_auto_install: true'"

COPY ./files/base.css $GALAXY_ROOT/static/dist
COPY ./files/tool_conf.xml $GALAXY_CONFIG_DIR/tool_conf.xml
COPY ./files/welcome.html /etc/galaxy/web/welcome.html
COPY ./files/TFtools/ $GALAXY_ROOT/tools/TFtools/
COPY ./files/tool_conf.xml $GALAXY_ROOT/config/tool_conf.xml
COPY ./files/datatypes_conf.xml /galaxy-central/config/datatypes_conf.xml



