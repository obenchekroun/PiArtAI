#!/bin/bash

INSTALL_DIR="$PWD"
echo Installing to "$INSTALL_DIR"

sudo apt-get update
sudo apt-get upgrade
sudo apt-get -y install tmux vim
sudo apt-get -y install cmake
sudo apt-get -y install python3-dev python3-venv python3-pip
sudo apt-get -y install python3-numpy python3-pil # for waveshare displays
sudo apt-get -y install imagemagick
sudo apt-get -y install git git-lfs
sudo apt-get -y install libopencv-dev  python3-opencv

cd "$INSTALL_DIR"
python3 -m venv .venv
. .venv/bin/activate

python3 -m pip install opencv_contrib_python
python3 -m pip install inky[rpi]==1.5.0
python3 -m pip install pillow
python3 -m pip install spidev # for waveshare display
  
# Following instructions taken directly from [OnnxStream repo](https://github.com/vitoplantamura/OnnxStream).

cd "$INSTALL_DIR"
git clone https://github.com/vitoplantamura/OnnxStream.git
cd OnnxStream/src
mkdir build
cd build
cmake ..
cmake --build . --config Release

cd "$INSTALL_DIR"
mkdir models
cd models
git clone --depth=1 https://huggingface.co/vitoplantamura/stable-diffusion-xl-turbo-1.0-anyshape-onnxstream
