# build images
docker build . -t slave

# test
注意替换路径,此处挂载mongodb和redis的目的是在单机测试爬虫访问redis和mongodb服务器。实际部署中的redis和mongodb地址应该写在对应爬虫的配置文件中

    docker run -p 222:22 -p 8888:80  -v ~/Projects/distributed_crawler/slaver_config/supervisor_config/:/etc/supervisor/conf.d/ -v ~/Projects/distributed_crawler/slaver_config/spiders/:/app/spider_cli/spiders -it --rm  --link redis:redis --link mongodb:mongodb slaver


# deploy 

    docker run  [-p 8888:80] slaver
    
转发端口号可自定义。