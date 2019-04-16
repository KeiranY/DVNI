# This Vagrantfile pulls a preconfigured Containernet VM
# in the future vagrant + ansible configurations from containernet will be added to stay up-to-date

Vagrant.configure("2") do |config|
  config.vm.box = "containernet"
  config.ssh.username = 'root'

  # Add a host only network
  config.vm.network "private_network", ip: "10.10.0.1/16"

  # Run config
  config.vm.provision "shell", path: "config.sh"

  # Assign 2GB ram
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
  end
end