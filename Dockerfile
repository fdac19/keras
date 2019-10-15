# docker-keras - Keras in Docker for reproducible deep learning

FROM ubuntu
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
    curl lsb-release \
    tmux  zsh zip \
    # install essentials
    build-essential \
    cmake \
    g++ \
    # requirements for numpy
    libopenblas-base \
    # requirements for keras
		libopenblas-dev \
		liblapack-dev \
		libssl-dev \
		libtiff5-dev \
		libwebp-dev \
		libzmq3-dev \
		zlib1g-dev \
		qt5-default \
		libvtk6-dev \
		zlib1g-dev \
		libjpeg-dev \
		libwebp-dev \
		libpng-dev \
		libtiff5-dev \
		libopenexr-dev \
		libgdal-dev \
		libdc1394-22-dev \
		libavcodec-dev \
		libavformat-dev \
		libswscale-dev \
		libtheora-dev \
		libvorbis-dev \
		libxvidcore-dev \
		libx264-dev \
		r-recommended \
    r-base-dev \
	 r-cran-car \
	 r-cran-rcolorbrewer \
	 r-cran-fastcluster \		
 		python3-numpy \
		python3-pillow \
		python3-pandas \
		python3-sklearn \
		python3 python3-dev     python3-pip     python3-setuptools   \
		python3-virtualenv     python3-wheel     pkg-config python3-h5py  python3-yaml python3-pydot \
&& apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

ARG TENSORFLOW_VERSION=1.5.0
ARG TENSORFLOW_DEVICE=cpu
ARG TENSORFLOW_APPEND=
# RUN pip --no-cache-dir install https://storage.googleapis.com/tensorflow/linux/${TENSORFLOW_DEVICE}/tensorflow${TENSORFLOW_APPEND}-${TENSORFLOW_VERSION}-cp27-none-linux_x86_64.whl
RUN pip3 --no-cache-dir install https://storage.googleapis.com/tensorflow/linux/${TENSORFLOW_DEVICE}/tensorflow${TENSORFLOW_APPEND}-${TENSORFLOW_VERSION}-cp35-cp35m-linux_x86_64.whl

ARG KERAS_VERSION=2.2.5
ENV KERAS_BACKEND=tensorflow
RUN pip3 --no-cache-dir install --no-dependencies git+https://github.com/fchollet/keras.git@${KERAS_VERSION}

# Install OpenCV
RUN git clone --depth 1 https://github.com/opencv/opencv.git /root/opencv && \
	cd /root/opencv && \
	mkdir build && \
	cd build && \
	cmake -DWITH_QT=ON -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON -DWITH_XINE=ON -DBUILD_EXAMPLES=ON .. && \
	make -j"$(nproc)"  && \
	make install && \
	ldconfig && \
	echo 'ln /dev/null /dev/raw1394' >> ~/.bashrc


RUN pip install jupyter

RUN if [ ! -d /var/run/sshd ]; then mkdir /var/run/sshd; chmod 0755 /var/run/sshd; fi
COPY *.sh *.py *.h5 /bin/ 

ENV NB_USER jovyan
ENV NB_UID 1000
ENV HOME /home/$NB_USER
RUN useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && mkdir $HOME/.ssh && chown -R $NB_USER:users $HOME 
RUN chown -R $NB_USER:users $HOME && chmod -R og-rwx $HOME/.ssh
