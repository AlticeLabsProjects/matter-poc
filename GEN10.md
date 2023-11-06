https://docs.yoctoproject.org/ref-manual/system-requirements.html#ubuntu-and-debian

## Instalação do Poky SDK

wget https://downloads.yoctoproject.org/releases/yocto/yocto-4.2.3/buildtools/x86_64-buildtools-nativesdk-standalone-4.2.3.sh

chmod +x x86_64-buildtools-nativesdk-standalone-4.2.3.sh

./x86_64-buildtools-nativesdk-standalone-4.2.3.sh

source /opt/poky/4.2.3/environment-setup-x86_64-pokysdk-linux

install-buildtools --without-extended-buildtools --base-url https://downloads.yoctoproject.org/releases/yocto --release yocto-4.2.3 --installer-version 4.2.3
