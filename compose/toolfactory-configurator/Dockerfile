
# container with planemo with a galaxy dist for it to use - need to use the one in the galaxy-server container really
# runs an rpyc server in a totally insecure way.
# planemo does not play nicely when run as a tool....
ARG DOCKER_REGISTRY=quay.io
ARG DOCKER_REGISTRY_USERNAME=bgruening
ARG IMAGE_TAG=latest
FROM $DOCKER_REGISTRY/$DOCKER_REGISTRY_USERNAME/galaxy-container-base:$IMAGE_TAG as final


ARG GALAXY_RELEASE="release_21.01"
ARG GALAXY_REPO="https://github.com/galaxyproject/galaxy"
ARG GALAXY_ROOT="/galaxy-central"

ENV DEBIAN_FRONTEND noninteractive

ENV GALAXY_USER=galaxy \
    GALAXY_GROUP=galaxy \
    GALAXY_UID=1450 \
    GALAXY_GID=1450 \
    GALAXY_HOME=/home/galaxy \
    GALAXY_ROOT=/galaxy-central \
    PLANEMO_ROOT=/planemo

RUN groupadd -r $GALAXY_USER -g $GALAXY_GID \
    && useradd -u $GALAXY_UID -r -g $GALAXY_USER -d $GALAXY_HOME -c "Galaxy user" --shell /bin/bash $GALAXY_USER \
    && mkdir -p $GALAXY_HOME \
    && mkdir -p $PLANEMO_ROOT \
    && mkdir -p $PLANEMO_ROOT/work \
    && mkdir -p /tools \
    && mkdir -p /config \
    && mkdir -p /workflows \
    && apt update && apt install python3 python-dev git python3-pip python3-wheel python3-venv git nano curl sudo rsync -y \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3 9 \
    && mkdir -p "$GALAXY_ROOT" \
    && curl -L -s $GALAXY_REPO/archive/$GALAXY_RELEASE.tar.gz | tar xzf - --strip-components=1 -C $GALAXY_ROOT


COPY ./files/TFtools /tools/TFtools

RUN python3 -m venv $GALAXY_ROOT/.venv \
&& python3 -m venv /venv \
&& . /venv/bin/activate \
&& pip3 install -U pip \
&& pip3 install planemo bioblend ephemeris parsec requests wheel rpyc \
&& mkdir -p /export/galaxy/config \
&& touch /export/galaxy/config/reload_uwsgi.touchme \
&& export HOME="$PLANEMO_ROOT" \
&& planemo conda_init --conda_prefix $PLANEMO_ROOT/con \
&& planemo test --conda_prefix "$PLANEMO_ROOT/con" --galaxy_root $GALAXY_ROOT "/tools/TFtools/planemo_lint_python/planemo_lint_python.xml" \
&& apt-get clean && apt-get purge \
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY ./start.sh /usr/local/bin/start_tf_config.sh
COPY ./files/waitforquiet.py /usr/local/bin/waitforquiet.py
COPY ./files/planemo_rpyc.py /usr/local/bin/planemo_rpyc.py
COPY ./files/TFtools.yml /config/TFtools.yml
COPY ./files/TF_demo_history_May_21.tar.gz /config/TF_demo_history_May_21.tar.gz
COPY ./files/TF-Demo-data-May-16.tar.gz /config/TF-Demo-data-May-16.tar.gz
COPY ./files/TF_demo_make_tools_May_21.ga /workflows/TF_demo_make_tools_May_21.ga
COPY ./files/TF_demo_make_test_tools_May_21.ga /workflows/TF_demo_make_test_tools_May_21.ga
COPY ./files/install-history.py /usr/local/bin/install-history.py
COPY ./files/datatypes_conf.xml /config/
COPY ./files/tool_conf.xml /config/
COPY ./files/base.css /config/
COPY ./files/toolfactory/welcome.html /config/welcome.html
# not a typo - for the planemo galaxy in this container!
COPY ./files/datatypes_conf.xml $GALAXY_ROOT/config/
RUN chown -R galaxy:galaxy /tools /config

ENTRYPOINT /usr/local/bin/start_tf_config.sh
