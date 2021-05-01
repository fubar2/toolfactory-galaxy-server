ARG DOCKER_REGISTRY=quay.io
ARG DOCKER_REGISTRY_USERNAME=fubar2
ARG IMAGE_TAG=latest

#FROM quay.io/cybozu/ubuntu-minimal:focal-20210217 as build_base
FROM buildpack-deps:20.04 as build_base
#was rate limited by docker for me :(
ENV DEBIAN_FRONTEND=noninteractive
ENV EXPORT_DIR=/export \
    GALAXY_ROOT=/galaxy \
    HTCONDOR_ROOT=/opt/htcondor

ENV GALAXY_STATIC_DIR=$GALAXY_ROOT/static \
    GALAXY_EXPORT=$EXPORT_DIR/galaxy \
    GALAXY_CONFIG_DIR=$GALAXY_ROOT/config \
    GALAXY_CONFIG_TOOL_DEPENDENCY_DIR=/tool_deps \
    GALAXY_CONFIG_TOOL_PATH=$GALAXY_ROOT/tools \
    GALAXY_CONFIG_TOOL_DATA_PATH=$GALAXY_ROOT/tool-data \
    GALAXY_VIRTUAL_ENV=$GALAXY_ROOT/.venv \
    GALAXY_DATABASE_PATH=$GALAXY_ROOT/database

ENV GALAXY_USER=galaxy \
    GALAXY_GROUP=galaxy \
    GALAXY_UID=1450 \
    GALAXY_GID=1450 \
    GALAXY_HOME=/home/galaxy

ENV GALAXY_CONDA_PREFIX=$GALAXY_CONFIG_TOOL_DEPENDENCY_DIR/_conda
ENV MINICONDA_VERSION=py38_4.9.2

RUN groupadd -r $GALAXY_USER -g $GALAXY_GID \
    && useradd -u $GALAXY_UID -r -g $GALAXY_USER -d $GALAXY_HOME -c "Galaxy user" --shell /bin/bash $GALAXY_USER \
    && mkdir $GALAXY_HOME \
    && chown -R $GALAXY_USER:$GALAXY_USER $GALAXY_HOME


FROM build_base as build_miniconda
COPY ./files/common_cleanup.sh /usr/bin/common_cleanup.sh
### apt update && apt install --no-install-recommends curl libcurl4-openssl-dev libssl-dev python3-dev python3-pip wget nano git -y \

RUN curl -s -L "https://repo.anaconda.com/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh" > /home/$GALAXY_USER/miniconda.sh
RUN /bin/bash  /home/$GALAXY_USER/miniconda.sh -b -p $GALAXY_CONDA_PREFIX \
    && rm  /home/$GALAXY_USER/miniconda.sh \
    && ln -s $GALAXY_CONDA_PREFIX/etc/profile.d/conda.sh /etc/profile.d/conda.sh \
    && echo ". $GALAXY_CONDA_PREFIX/etc/profile.d/conda.sh" >> $GALAXY_HOME/.bashrc \
    && echo "conda activate base" >> $GALAXY_HOME/.bashrc \
    && export PATH=$GALAXY_CONDA_PREFIX/bin/:$PATH \
    && conda config --add channels defaults \
    && conda config --add channels bioconda \
    && conda config --add channels conda-forge \
    && conda install virtualenv pip ephemeris \
    && conda clean --packages -t -i \
    && /usr/bin/common_cleanup.sh

FROM build_base as build_galaxy

ARG GALAXY_RELEASE=release_20.09
ARG GALAXY_REPO=https://github.com/galaxyproject/galaxy


# Install Galaxy
RUN apt update && apt install --no-install-recommends libcurl4-openssl-dev libssl-dev python3-dev python3-pip git wget nano curl -y \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3 9 \
    && mkdir "${GALAXY_ROOT}" \
    && curl -L -s $GALAXY_REPO/archive/$GALAXY_RELEASE.tar.gz | tar xzf - --strip-components=1 -C $GALAXY_ROOT \
    && cd $GALAXY_ROOT \
    && ./scripts/common_startup.sh \
    && . $GALAXY_ROOT/.venv/bin/activate \
    && pip3 install -U pip \
    && pip3 install drmaa psycopg2 pycurl pykube watchdog \
    && pip3 install importlib-metadata importlib-resources pathlib2 ruamel.yaml.clib typing zipp \
    && deactivate \
    && rm -rf .ci .circleci .coveragerc .gitignore .travis.yml CITATION CODE_OF_CONDUCT.md CONTRIBUTING.md CONTRIBUTORS.md \
              LICENSE.txt Makefile README.rst SECURITY_POLICY.md pytest.ini tox.ini \
              client contrib doc config/plugins lib/galaxy_test test test-data \
              .venv/lib/node_modules .venv/src/node-v10.15.3-linux-x64 \
              .venv/include/node .venv/bin/node .venv/bin/nodeenv
    #&& /usr/bin/common_cleanup.sh

COPY ./files/common_cleanup.sh /usr/bin/common_cleanup.sh
COPY ./files/tool_conf.xml  $GALAXY_ROOT/config/tool_conf.xml
COPY ./files/tool_sheds_conf.xml $GALAXY_ROOT/config/tool_sheds_conf.xml
#COPY ./files/job_conf.xml  $GALAXY_ROOT/config/job_conf.xml # changed template to suit our needs
COPY ./files/datatypes_conf.xml $GALAXY_ROOT/config/datatypes_conf.xml
COPY ./files/toolfactory $GALAXY_ROOT/tools/toolfactory
COPY ./files/welcome.html $GALAXY_ROOT/static/welcome.html

# --- Final image ---

FROM quay.io/bgruening/galaxy-cluster-base:latest as final
COPY ./files/common_cleanup.sh /usr/bin/common_cleanup.sh
COPY ./files/create_galaxy_user.py /usr/local/bin/create_galaxy_user.py


ENV EXPORT_DIR=/export \
    GALAXY_ROOT=/galaxy \
    GALAXY_PYTHON=/usr/bin/python3 \
    HTCONDOR_ROOT=/opt/htcondor

ENV GALAXY_RELEASE=${GALAXY_RELEASE:-release_20.09} \
    GALAXY_REPO=${GALAXY_REPO:-https://github.com/galaxyproject/galaxy} \
    GALAXY_STATIC_DIR=$GALAXY_ROOT/static \
    GALAXY_EXPORT=$EXPORT_DIR/galaxy \
    GALAXY_CONFIG_DIR=$GALAXY_ROOT/config \
    GALAXY_CONFIG_TOOL_DEPENDENCY_DIR=/tool_deps \
    GALAXY_CONFIG_TOOL_PATH=$GALAXY_ROOT/tools \
    GALAXY_CONFIG_TOOL_DATA_PATH=$GALAXY_ROOT/tool-data \
    GALAXY_VIRTUAL_ENV=$GALAXY_ROOT/.venv \
    GALAXY_DATABASE_PATH=$GALAXY_ROOT/database

ENV GALAXY_USER=galaxy \
    GALAXY_GROUP=galaxy \
    GALAXY_UID=1450 \
    GALAXY_GID=1450 \
    GALAXY_HOME=/home/galaxy

ENV GALAXY_CONFIG_FILE=$GALAXY_CONFIG_DIR/galaxy.yml

# Set permissions
RUN groupadd -r $GALAXY_USER -g $GALAXY_GID \
    && useradd -u $GALAXY_UID -r -g $GALAXY_USER -d $GALAXY_HOME -c "Galaxy user" --shell /bin/bash $GALAXY_USER \
    && /usr/bin/common_cleanup.sh

# Install remaining dependencies
RUN apt update && apt install --no-install-recommends curl gcc gnupg2 libgomp1 liblzma-dev libbz2-dev libpq-dev \
 libcurl4-openssl-dev libssl-dev apt-utils openssl netbase apt-transport-https libreadline8  \
 software-properties-common ca-certificates\
 mercurial make netcat python3-dev python3-setuptools python3-pip \
 git nano wget locales tzdata -y \
# Cython and wheel are needed to later install pysam..
&& pip3 install Cython wheel watchdog planemo ephemeris galaxyxml lxml bioblend parsec tzdata \
&& pip3 install pysam \
&& dpkg-reconfigure -f noninteractive tzdata \
&& locale-gen en_US.UTF-8 \
&& update-locale LANG=en_US.UTF-8 \
&& curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - \
&& add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
&& apt-get -y update  \
&& apt install -y docker-ce-cli \
&& /usr/bin/common_cleanup.sh

# GALAXY_USER should be able to run docker without root permissions
RUN usermod -aG docker $GALAXY_USER

# Make Python3 standard
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 9

COPY --chown=$GALAXY_USER:$GALAXY_USER --from=build_galaxy ${GALAXY_ROOT} ${GALAXY_ROOT}
COPY --chown=$GALAXY_USER:$GALAXY_USER --from=build_miniconda ${GALAXY_CONFIG_TOOL_DEPENDENCY_DIR} ${GALAXY_CONFIG_TOOL_DEPENDENCY_DIR}
COPY --chown=$GALAXY_USER:$GALAXY_USER --from=build_miniconda ${GALAXY_HOME} ${GALAXY_HOME}
COPY --chown=$GALAXY_USER:$GALAXY_USER --from=build_miniconda /etc/profile.d/conda.sh /etc/profile.d/conda.sh

COPY ./files/start.sh /usr/bin/start.sh

EXPOSE 8080

ENTRYPOINT "/usr/bin/start.sh"
