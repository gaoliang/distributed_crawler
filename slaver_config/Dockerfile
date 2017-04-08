FROM ubuntu:16.04

WORKDIR /app/spider_cli
RUN mkdir /app/spider_cli/spiders
RUN sed -i 's/http:\/\/archive.ubuntu.com\/ubuntu\//http:\/\/cn.archive.ubuntu.com\/ubuntu\//g' /etc/apt/sources.list
RUN mkdir -p  /var/run/sshd /var/log/supervisor
RUN apt-get update && apt-get install -y openssh-server \
                                         supervisor \
                                         openssl \
                                         python-dev \
                                         python-lxml \
                                         build-essential libssl-dev libffi-dev \
                                         libxml2-dev libxslt1-dev zlib1g-dev
RUN apt-get install python-pip -y
RUN pip install --upgrade pip
COPY requirements.txt /app/spider_cli/requirements.txt
COPY spider_base_server.py /app/spider_cli/watcher.py
COPY watcher.py /app/spider_cli/watcher.py
RUN apt-get install python-pip -y
RUN pip install -r /app/spider_cli/requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple


EXPOSE 22 80 9001
CMD ["/usr/bin/supervisord"]
