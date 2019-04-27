# This Vagrantfile pulls a preconfigured Containernet VM
# in the future vagrant + ansible configurations from containernet will be added to stay up-to-date

Vagrant.configure("2") do |config|
  config.vm.box = "KcY/containernet"
  config.vm.base_mac = "029CD253C1D1"

  config.ssh.username = 'root'
  config.vm.network "forwarded_port", guest: 22, host: 2222, host_ip: "127.0.0.1", id: 'ssh'

  # Add a host only network
  config.vm.network "private_network", ip: "10.10.0.2"

  # Run config
  config.vm.provision "shell", path: "config.sh"

  # Assign 2GB ram
  config.vm.provider "virtualbox" do |v|
    v.memory = 2048
    v.gui = true
    v.customize ["modifyvm", :id, "--uartmode1", "disconnected"]
  end
end
