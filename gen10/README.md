# GEN10 OCI package creation process

In a fresh installed Ubuntu 18.04 Server machine, follow this steps to be able to create a OCI image and bundle to run in gen10.

## Burn [Raspberry PI 3 image](https://github.com/AlticeLabsProjects/matter-poc/raw/main/gen10/rdk-generic-broadband-image-raspberrypi-rdk-broadband.wic.bz2)

Burn the image with bmaptool do a SD on device sdX:
```sh
cd ~

sudo apt install bmap-tools

bzip2 -d rdk-generic-broadband-image-raspberrypi-rdk-broadband.wic.bz2

bmaptool copy --nobmap rdk-generic-broadband-image-raspberrypi-rdk-broadband.wic /dev/sdX
```

_Note: Using a virtual machine, the sd device may not be available. In this case, use an alternative method_ 

## Dunfell installation

Install all the dependencies:
```sh
cd ~

sudo apt install gawk wget git diffstat unzip texinfo gcc build-essential chrpath socat cpio python3 python3-pip python3-pexpect xz-utils debianutils iputils-ping python3-git python3-jinja2 libegl1-mesa libsdl1.2-dev python3-subunit mesa-common-dev zstd liblz4-tool file locales
```

Create and set the locale:
```sh
sudo locale-gen en_US.UTF-8
```

Clone dunfell and all meta dependencies:
```sh
git clone -b dunfell git://git.yoctoproject.org/poky.git dunfell

cd dunfell

git clone -b dunfell git://git.yoctoproject.org/meta-raspberrypi
git clone -b dunfell git://git.yoctoproject.org/meta-virtualization
git clone -b dunfell git://git.openembedded.org/meta-openembedded
git clone -b dunfell https://github.com/meta-qt5/meta-qt5.git
git clone https://github.com/stagingrdkm/meta-dac-sdk.git
git clone https://github.com/Agilent/meta-coverity.git
```

Remove unused recipes to acceletate the build process:
```sh
cd meta-dac-sdk/recipes-example

rm -r cobalt
rm -r netflix
rm -r amazon-prime
rm -r flutter-example

cd ..

rm -rf meta-dac-sdk/recipes-browser
rm -rf meta-dac-sdk/recipes-extended

cd ..
```

Build the meta dependencies:
```sh
source oe-init-build-env

bitbake-layers add-layer ../meta-openembedded/meta-oe
bitbake-layers add-layer ../meta-openembedded/meta-python
bitbake-layers add-layer ../meta-openembedded/meta-filesystems
bitbake-layers add-layer ../meta-openembedded/meta-networking
bitbake-layers add-layer ../meta-raspberrypi
bitbake-layers add-layer ../meta-dac-sdk
bitbake-layers add-layer ../meta-virtualization
bitbake-layers add-layer ../meta-qt5
```

Set raspberry pi 3 as build playform:
```sh
cd ../meta-coverity/classes
cp coverity.bbclass ../../meta-dac-sdk/classes
cd ..
cp -r lib ../meta-dac-sdk
echo 'MACHINE="raspberrypi3"' >> conf/local.conf
echo 'DISTRO_FEATURES:append = "virtualization"' >> conf/local.conf
```

Remove .git information and create a backup for a fresh start:
```sh
cd ~
find dunfell -type d -name .git -exec rm -rf {} \;
tar vcfz dunfell-fresh-install.tar.gz dunfell
```

## Hello World example

```sh
cd ~

wget "https://wiki.rdkcentral.com/download/attachments/254380290/helloworld-test.tgz?version=2&modificationDate=1679780515000&api=v2&download=true" -O helloworld-test.tar.gz

tar vxfz helloworld-test.tar.gz -C dunfell

cd dunfell
MACHINE=raspberrypi3-rdk-broadband source oe-init-build-env
bitbake dac-image-helloworld-test
```
