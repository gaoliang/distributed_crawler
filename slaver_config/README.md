# build images
docker build . -t slave

# run and test supervisor auto update
注意替换路径

    docker run -p 222:22 -p 80 -p 9001 -v ~/Projects/distributed_crawler/slaver_config/supervisor_config/:/etc/supervisor/conf.d/ -v ~/Projects/distributed_crawler/slaver_config/spiders/:/app/spider_cli/spiders -it --rm  --link redis:redis --link mongodb:mongodb slaver
   
之后在supervisor_config文件夹中的所有改动都会导致supervisor的update命令执行，