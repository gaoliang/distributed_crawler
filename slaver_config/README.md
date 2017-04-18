# 使用docker-compose 单机模拟分布式
    
    
    
    docker-compose scale slaver=4
    docker-compose up
    docker ps  -->可以查看端口转发情况


# 开发和测试环境和搭建 
    docker build . -t slave
    docker run  [-p 8888:80] --link splash:splash slaver
    如果需要在单机同时部署redis服务和slaver服务，应该使用如下命令链接redis，并在爬虫设置中设置爬虫的redis服务器的hostname为redis
    docker run -p 6379:6379 --name redis redis
    docker run  [-p 8888:80] --link splash:splash --link redis:redis slaver