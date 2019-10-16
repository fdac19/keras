# docker-keras - Keras in Docker for reproducible deep learning

FROM tensorflow/tensorflow:1.14.0

MAINTAINER audrism  <audris@mockus.org>

# install debian packages
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -qq \
 && apt-get install --no-install-recommends -y \
    dbus \
    openssh-server \
    lsof sudo \
    libssl-dev \
    vim \
    git \
    wget curl lsb-release \
    tmux zip \
    # install essentials
    # requirements for numpy
    libopenblas-base \
    # requirements for keras
	libopenblas-dev \
	liblapack-dev \
	libtiff5-dev \
	zlib1g-dev \
	libsm6 libxext6 libfontconfig1 libxrender1 \
	r-recommended r-base-dev r-cran-car r-cran-rcolorbrewer r-cran-fastcluster \		
&& apt-get clean \
 && rm -rf /var/lib/apt/lists/*

#RUN pip3 --no-cache-dir install --upgrade pip
#RUN pip3 install tensorflow==1.14.0 
#ARG KERAS_VERSION=2.2.5
#ENV KERAS_BACKEND=tensorflow
#RUN pip3 --no-cache-dir install git+https://github.com/fchollet/keras.git@${KERAS_VERSION}

#ARG TENSORFLOW_VERSION=1.5.0
#ARG TENSORFLOW_DEVICE=cpu
#ARG TENSORFLOW_APPEND=
#RUN pip3 --no-cache-dir install https://storage.googleapis.com/tensorflow/linux/${TENSORFLOW_DEVICE}/tensorflow${TENSORFLOW_APPEND}-${TENSORFLOW_VERSION}-cp36-cp36m-linux_x86_64.whl


RUN pip --no-cache-dir install opencv-python
# Install OpenCV
#RUN git clone --depth 1 https://github.com/opencv/opencv.git /root/opencv && \
#	cd /root/opencv && mkdir build && cd build && \
#	cmake -DWITH_QT=ON -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON -DWITH_XINE=ON -DBUILD_EXAMPLES=ON .. && \
#	make -j"$(nproc)"  && make install && ldconfig && 	echo 'ln /dev/null /dev/raw1394' >> ~/.bashrc



RUN if [ ! -d /var/run/sshd ]; then mkdir /var/run/sshd; chmod 0755 /var/run/sshd; fi
COPY *.sh /bin/

ENV NB_USER jovyan
ENV NB_UID 1000
ENV HOME /home/$NB_USER
RUN useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && mkdir $HOME/.ssh && chown -R $NB_USER:users $HOME 
COPY *.py $HOME/ 
RUN cd $HOME && wget https://github.com/fchollet/deep-learning-models/releases/download/v0.2/resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5
RUN chown -R $NB_USER:users $HOME && chmod -R og-rwx $HOME/.ssh
