
# container with planemo
# runs an rpyc server in a secure-ish way.
# planemo does not play nicely when run as a tool....
FROM buildpack-deps:20.04 as final

MAINTAINER ross.lazarus@gmail.com

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
    && mkdir -p /files \
    && apt update && apt install python3 python-dev git python3-pip python3-wheel python3-venv git nano curl sudo rsync -y \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3 9 \
    && mkdir -p "$GALAXY_ROOT"

RUN python3 -m venv /venv \
    && . /venv/bin/activate \
    && pip3 install -U pip \
    && pip3 install planemo bioblend ephemeris parsec requests wheel rpyc \
    && mkdir -p $GALAXY_ROOT \
    && mkdir -p $GALAXY_ROOT/config \
    && export HOME="$PLANEMO_ROOT" \
    && planemo conda_init --conda_prefix $PLANEMO_ROOT/con \
    && apt-get clean && apt-get purge \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY ./files/start_TF_config.sh /usr/local/bin/start_TF_config.sh
COPY ./files/waitforquiet.py /usr/local/bin/waitforquiet.py
COPY ./files/planemo_rpyc.py /usr/local/bin/planemo_rpyc.py
COPY ./files/TF_demo_history.tar.gz /files/TF_demo_history.tar.gz
COPY ./files/TF-Demo-data-May-16.tar.gz /files/TF-Demo-data-May-16.tar.gz
COPY ./files/TF_demo_make_tools.ga /files/TF_demo_make_tools.ga
COPY ./files/TF_demo_make_test_tools.ga /files/TF_demo_make_test_tools.ga
COPY ./files/install-history.py /usr/local/bin/install-history.py


ENTRYPOINT /usr/bin/bash /usr/local/bin/start_TF_config.sh
