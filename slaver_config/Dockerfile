FROM ubuntu:16.04

WORKDIR /app/spider_cli
RUN echo "root:root" | chpasswd
RUN mkdir /app/spider_cli/spiders
RUN sed -i 's/http:\/\/archive.ubuntu.com\/ubuntu\//http:\/\/mirrors.njupt.edu.cn\/ubuntu\//g' /etc/apt/sources.list
RUN mkdir -p  /var/run/sshd /var/log/supervisor /app/spider_cli/templates /var/log/supervisor
RUN apt-get update && apt-get install -y openssh-server \
                                         supervisor \
                                         openssl \
                                         python-dev \
                                         python-lxml \
                                         build-essential libssl-dev libffi-dev \
                                         libxml2-dev libxslt1-dev zlib1g-dev
RUN apt-get install python-pip -y
COPY requirements.txt /app/spider_cli/requirements.txt
COPY spider_base_server.py /app/spider_cli/spider_base_server.py
COPY templates/upload.html /app/spider_cli/templates/upload.html
COPY supervisor_config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN pip install -r /app/spider_cli/requirements.txt -i https://mirrors.njupt.edu.cn/nexus/repository/pypi/simple


EXPOSE 22 80 9001 8080
CMD ["/usr/bin/supervisord"]
