#!/bin/bash
# Workaround for cibuildwheel Docker images using CentOS 7 now that CentOS 7
# is gone.

sed -i s/mirror.centos.org/vault.centos.org/g /etc/yum.repos.d/*.repo
sed -i s/^#.*baseurl=http/baseurl=http/g /etc/yum.repos.d/*.repo
