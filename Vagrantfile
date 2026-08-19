# set up the default terminal
ENV["TERM"]="linux"

# set minimum version for Vagrant
Vagrant.require_version ">= 2.2.10"
Vagrant.configure("2") do |config|
  config.vm.provision "shell",
    inline: "sudo zypper update -y && sudo zypper install -y apparmor-parser"
  
  # Set the image for the vagrant box
  config.vm.box = "opensuse/Leap-15.6.x86_64"
  # Set the image version
  config.vm.box_version = "15.6.13.356"

  # Forward the ports from the guest VM to the local host machine
  # Forward more ports, as needed
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 6111, host: 6111
  config.vm.network "forwarded_port", guest: 6112, host: 6112

  # Set the static IP for the vagrant box
  # Use 192.168.56.0/21 — the default host-only range allowed by VirtualBox 7.x
  # (older 6.1.x accepts it too, so this works on both Vagrant 2.2.10+/VBox 6.1.x
  # and Vagrant 2.4.x/VBox 7.1.x without editing /etc/vbox/networks.conf).
  config.vm.network "private_network", ip: "192.168.56.4"
  
  # Configure the parameters for VirtualBox provider
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
    vb.cpus = 4
    vb.customize ["modifyvm", :id, "--ioapic", "on"]
  end
end
