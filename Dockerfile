FROM debian:stretch

MAINTAINER audrism  <audris@mockus.org> (using https://github.com/gw0/docker-keras py2-tf-cpu

# install debian packages
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -qq \
 && apt-get install --no-install-recommends -y \
    # install essentials
    git openssh-client \
    # install python 2
    python python-dev python-pip python-setuptools python-virtualenv python-wheel  pkg-config \
    # requirements for numpy
    libopenblas-base  python-numpy python-scipy \
    # requirements for keras
    python-h5py python-yaml python-pydot \
    dbus openssh-server lsof sudo vim wget curl lsb-release tmux zip \
    libsm6 libxext6 libfontconfig1 libxrender1 \
    r-recommended r-base-dev r-cran-car r-cran-rcolorbrewer r-cran-fastcluster \		
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# manually update numpy
RUN pip --no-cache-dir install -U numpy==1.13.3

ARG TENSORFLOW_VERSION=1.5.0
ARG TENSORFLOW_DEVICE=cpu
ARG TENSORFLOW_APPEND=
RUN pip --no-cache-dir install https://storage.googleapis.com/tensorflow/linux/${TENSORFLOW_DEVICE}/tensorflow${TENSORFLOW_APPEND}-${TENSORFLOW_VERSION}-cp27-none-linux_x86_64.whl

ARG KERAS_VERSION=2.1.4
ENV KERAS_BACKEND=tensorflow
RUN pip --no-cache-dir install --no-dependencies git+https://github.com/fchollet/keras.git@${KERAS_VERSION}


RUN pip --no-cache-dir install opencv-python jupyter pymongo


RUN if [ ! -d /var/run/sshd ]; then mkdir /var/run/sshd; chmod 0755 /var/run/sshd; fi
COPY *.sh /bin/

ENV NB_USER jovyan
ENV NB_UID 1000
ENV HOME /home/$NB_USER
RUN useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && mkdir $HOME/.ssh && chown -R $NB_USER:users $HOME 
COPY *.py $HOME/ 
COPY id_rsa_gcloud.pub $HOME/.ssh/authorized_keys
RUN cd $HOME && wget https://github.com/fchollet/deep-learning-models/releases/download/v0.2/resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5
RUN chown -R $NB_USER:users $HOME && chmod -R og-rwx $HOME/.ssh
