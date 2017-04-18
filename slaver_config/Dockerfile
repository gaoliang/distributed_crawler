FROM ubuntu:16.04

WORKDIR /app/spider_cli
RUN mkdir /app/spider_cli/spiders
RUN sed -i 's/http:\/\/archive.ubuntu.com\/ubuntu\//http:\/\/mirrors.njupt.edu.cn\/ubuntu\//g' /etc/apt/sources.list
RUN mkdir -p  /var/run/sshd /var/log/supervisor /app/spider_cli/templates /var/log/supervisor
RUN apt-get update && apt-get install -y openssh-server \
                                         supervisor \
                                         openssl \
                                         nginx \
                                         python-dev \
                                         python-lxml \
                                         build-essential libssl-dev libffi-dev \
                                         libxml2-dev libxslt1-dev zlib1g-dev python-pip
########## for ssh
RUN echo 'root:root' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
ENV PYTHONPATH $PYTHONPATH:/app/spider_cli/spiders

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
###########
RUN echo "export VISIBLE=now" >> /etc/profile
COPY requirements.txt /app/spider_cli/requirements.txt
COPY spider_base_server.py /app/spider_cli/spider_base_server.py
COPY templates/upload.html /app/spider_cli/templates/upload.html
COPY supervisor_config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN pip install -r /app/spider_cli/requirements.txt -i https://mirrors.njupt.edu.cn/nexus/repository/pypi/simple
ADD nginx /etc/nginx
ADD tools /usr/local/lib/python2.7/dist-packages/
RUN rm -v /etc/nginx/sites-available/default
EXPOSE 22 80
CMD ["/usr/bin/supervisord"]
