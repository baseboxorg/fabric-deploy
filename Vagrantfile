VAGRANTFILE_API_VERSION = "2"

path = "#{File.dirname(__FILE__)}"

require 'yaml'
require path + '/scripts/projects.rb'

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  Projects.configure(config, YAML::load(File.read(path + '/Projects.yaml')))
end