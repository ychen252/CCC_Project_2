#!/bin/bash

# apply the instances, render the templates
#. ./unimelb-comp90024-2020-grp-47-openrc.sh; ansible-playbook --ask-become-pass create_instance.yml

# proxy configuration
#ansible-playbook -i inventory.ini -u ubuntu --key-file=./key proxy_configuration.yml

# install docker on the remote servers
#ansible-playbook -i inventory.ini -u ubuntu --key-file=./key docker_configuration.yml

# setup couchdb cluster on database servers
ansible-playbook -i inventory.ini -u ubuntu --key-file=./key couchdb_configuration.yml

# setup the web server and load the data
#ansible-playbook -i inventory.ini -u ubuntu --key-file=./key web_deployment.yml
