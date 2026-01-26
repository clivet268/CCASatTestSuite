sudo apt-get update -y
sudo apt-get install bison flex libncurses-dev libelf-dev elfutils libssl-dev bc -y
sudo cp /boot/config-$(uname -r) .config
sudo find scripts -name "*.sh" -execdir chmod u+x {} +
yes "" | sudo make -j$(nproc) bzImage
sudo make -j$(nproc) olddefconfig
sudo make -j$(nproc)
sudo make -j$(nproc) modules_install
sudo make install
