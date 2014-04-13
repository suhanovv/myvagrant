from ftplib import FTP
import os
import subprocess
from myvagrant.config import Credentials, Config
from os.path import expanduser
import getpass



HOME_DIR = expanduser('~')
CONF_DIR = os.path.join(HOME_DIR, '.myvagrant')
VAGRANT_TPL_FILE = os.path.join(CONF_DIR, 'Vagrantfile')

VAGRANT_TPL = """
# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.box = "{BOX_NAME}"
    config.vm.hostname = "{HOST_NAME}.lo"
    config.vm.network "private_network", ip: "{IP}"

    config.vm.provider "virtualbox" do |v|
      v.customize ["setextradata", :id, "VBoxInternal2/SharedFoldersEnableSymlinksCreate/v-root", "1"]
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    end

    config.vm.synced_folder "{PROJECT_DIR}/repo", "/srv/www/{HOST_NAME}/repo", type: "nfs"

    config.vm.provision "ansible" do |ansible|
        ansible.playbook = "provision/playbook.yml"
        ansible.extra_vars = {
        	project_credentials: "{CREDENTIALS}",
        	is_api: {IS_API},
        	environment: "{ENVIRONMENT}"
        }
    end
end
"""


def is_python_project(project):
    credentials = Credentials().load()
    ftp = FTP('%(url)s' % {'url': credentials.get('dev_server_url')})
    ftp.login('%(username)s@%(project)s' % {'username': credentials.get('factory_user'), 'project': project},
              credentials.get('factory_pass'))
    ftp.cwd('/repo/dev')

    if 'manage.py' in ftp.nlst():
        return True

    return False


def git(*args):
    return subprocess.check_output(['git'] + list(args), stderr=open(os.devnull, 'wb'))


def check_first_run():
    if not os.path.exists(CONF_DIR):
        credentials = Credentials()
        config = Config()
        username = raw_input('Factory Username: ')
        password = getpass.getpass('Factory Pass: ')
        factory_url = raw_input('Factory url: ')
        factory_url = factory_url.split('//')[-1]
        dev_server_url = raw_input('Dev server url: ')
        dev_server_url = dev_server_url.split('//')[-1]

        os.makedirs(CONF_DIR)
        git("clone", "https://github.com/suhanovv/ailove-playbook/", "%s" % os.path.join(CONF_DIR, 'provisions'))
        credentials.save(factory_user=username, factory_pass=password, factory_url=factory_url, dev_server_url=dev_server_url)
        config.save(box_name='ailove-ubuntu-13', ip_range='192.168.10/100.2/100', projects_dir='/work/projects',
                    vagrant_tpl=VAGRANT_TPL_FILE)

        with open(VAGRANT_TPL_FILE, 'wb') as vagrantfile:
            vagrantfile.write(VAGRANT_TPL)