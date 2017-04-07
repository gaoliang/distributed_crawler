#build images
docker build . -t slave

#run and test supervisor auto update
 注意替换路径

    docker run -i -t -p 220:22 -p 880:80 -v /path/to/distributed_crawler/slaver_config/:/etc/supervisor/conf.d/ mysupervisord
   
  之后在slaver_config文件夹中的所有改动都会导致supervisor的update命令执行，