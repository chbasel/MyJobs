from ubuntu:trusty

env DEBIAN_FRONTEND=noninteractive

run apt-get update && \
    apt-get --yes install wget curl software-properties-common apt-transport-https && \
    add-apt-repository -ys 'deb https://deb.nodesource.com/node_5.x trusty main' && \
    curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
    apt-get update && apt-get --yes build-dep libgeos-dev && \
    apt-get --yes install python-setuptools python-dev apache2 python-pip \
        mysql-client libxml2 libxml2-dev libxslt-dev libmysqlclient-dev \
        phantomjs python-ipdb strace nodejs libgeos-dev && \
    apt-get --yes install git-core inotify-tools

add requirements.txt /requirements.txt
run pip install -r requirements.txt
run pip install django-debug-toolbar sphinx

run adduser dev

run mkdir -p /var/log/directseo /var/log/myjobs /home/web/myjobslogs
run touch /var/log/directseo/dseo.log /home/web/myjobslogs/logfile
run ln -s /var/log /log

volume /MyJobs
volume /deployment

env DEVSERVER_HTTPS=1
