sudo apt-get update -y
sudo apt-get install bison flex libncurses-dev libelf-dev elfutils libssl-dev bc p7zip-full -y
wget -c https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.14.tar.xz
7z x linux-6.14.tar.xz
7z x linux-6.14.tar
cd linux-6.14/
sudo cp /boot/config-$(uname -r) .config
sudo find scripts -name "*.sh" -execdir chmod u+x {} +
yes "" | sudo make -j$(nproc) bzImage
sudo make -j$(nproc) olddefconfig
sudo make -j$(nproc)
sudo make -j$(nproc) modules_install
sudo make install
