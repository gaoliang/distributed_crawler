FROM ubuntu:16.04

WORKDIR /app/spider_cli

RUN sed -i 's/http:\/\/archive.ubuntu.com\/ubuntu\//http:\/\/cn.archive.ubuntu.com\/ubuntu\//g' /etc/apt/sources.list
RUN mkdir /app/spider_cli/s
RUN apt-get update && apt-get install -y openssh-server \
                                         apache2 \
                                         supervisor \
                                         openssl \
                                         python-dev \
                                         python-lxml \
                                         build-essential libssl-dev libffi-dev \
                                         libxml2-dev libxslt1-dev zlib1g-dev
RUN mkdir -p /var/lock/apache2 /var/run/apache2 /var/run/sshd /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN apt-get install python-pip -y
RUN pip install --upgrade pip
COPY requirements.txt /app/spider_cli/requirements.txt
RUN pip install -r /app/spider_cli/requirements.txt

EXPOSE 22 80 9001
CMD ["/usr/bin/supervisord"]