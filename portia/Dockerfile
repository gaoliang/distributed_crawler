FROM ubuntu:14.04
WORKDIR /app/slyd

RUN sed -i 's/http:\/\/archive.ubuntu.com\/ubuntu\//http:\/\/cn.archive.ubuntu.com\/ubuntu\//g' /etc/apt/sources.list
COPY provision.sh /app/provision.sh
COPY slybot/requirements.txt /app/slybot/requirements.txt
COPY slyd/requirements.txt /app/slyd/requirements.txt
COPY portia_server/requirements.txt /app/portia_server/requirements.txt

RUN /app/provision.sh install_deps  && \
    /app/provision.sh install_splash && \
    pip install -r /app/slybot/requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple && \
    pip install -r /app/slyd/requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple && \
    pip install -r /app/portia_server/requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple && \
    /app/provision.sh cleanup

RUN mkdir -p /var/run/sshd
RUN mkdir -p /var/log/supervisor
COPY supervisor/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ADD nginx /etc/nginx
ADD . /app
RUN pip install -e /app/slyd && \
    pip install -e /app/slybot
#RUN python /app/portia_server/manage.py migrate

EXPOSE 9001
ENTRYPOINT ["/app/docker/entry"]
