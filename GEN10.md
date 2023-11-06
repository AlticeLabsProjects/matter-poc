https://wiki.rdkcentral.com/display/ASP/Quickstart%3A+Building%2C+Installing+and+Running+DAC+apps#Quickstart:Building,InstallingandRunningDACapps-SetupSDKandbuildyourfirstDACapp

https://docs.yoctoproject.org/ref-manual/system-requirements.html#ubuntu-and-debian

## Instalação do BundleGen

git clone https://github.com/rdkcentral/BundleGen.git

cd BundleGen/

sudo apt update
sudo apt upgrade
sudo apt install python3.7
sudo apt install -y make git go-md2man

wget https://dl.google.com/go/go1.17.13.linux-amd64.tar.gz
tar -xvf go1.17.13.linux-amd64.tar.gz 
sudo mv go /usr/local
rm -rf /usr/local/go
sudo rm -rf /usr/local/go
sudo mv go /usr/local
make
make clean
make
go mod vendor
make
sudo make install
. /etc/os-release

sudo sh -c "echo 'deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/x${NAME}_${VERSION_ID}/ /' > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list"
wget -nv https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/x${NAME}_${VERSION_ID}/Release.key -O- | sudo apt-key add -
sudo apt update && sudo apt install skopeo

## Instalação do Bitbake

### Iniciar o Build Environment

MACHINE=raspberrypi3-rdk-broadband source ./oe-init-build-env

## Instalação do Poky SDK

wget https://downloads.yoctoproject.org/releases/yocto/yocto-4.2.3/buildtools/x86_64-buildtools-nativesdk-standalone-4.2.3.sh

chmod +x x86_64-buildtools-nativesdk-standalone-4.2.3.sh

./x86_64-buildtools-nativesdk-standalone-4.2.3.sh

source /opt/poky/4.2.3/environment-setup-x86_64-pokysdk-linux

install-buildtools --without-extended-buildtools --base-url https://downloads.yoctoproject.org/releases/yocto --release yocto-4.2.3 --installer-version 4.2.3
