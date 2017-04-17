# build images
docker build . -t slave

# 预先安装并运行splash的docker容器

    docker run -p 8050:8050 --name splash scrapinghub/splash

# test
注意替换路径,此处挂载mongodb和redis的目的是在单机测试爬虫访问redis和mongodb服务器。实际部署中的redis和mongodb地址应该写在对应爬虫的配置文件中

    docker run -p 222:22 -p 8888:80  -v ~/Projects/distributed_crawler/slaver_config/supervisor_config/:/etc/supervisor/conf.d/ -v ~/Projects/distributed_crawler/slaver_config/spiders/:/app/spider_cli/spiders -it --rm  --link redis:redis --link mongodb:mongodb --link splash:splash  slaver


# deploy 

    docker run  [-p 8888:80] --link splash:splash slaver
    如果需要在单机同时部署redis服务和slaver服务，应该使用如下命令链接redis，并在爬虫设置中设置爬虫的redis服务器的hostname为redis
    docker run -p 6379:6379 --name redis redis
    docker run  [-p 8888:80] --link splash:splash --link redis:redis slaver
     
    
转发端口号可自定义,以方便实现单机多容器的测试运行。