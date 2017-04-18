# test

env:

    docker run -p 8050:8050 --name splash -d scrapinghub/splash
    docker run -p 6379:6379 --name redis -d  redis
    docker run -p 27017:27017 --name mongo -d  mongo
    
master:
    
    workdir: master_config/master_manager
    pip install requirements.txt
    python manage.py runserver
    
slaver:

    workdir:slaver_config
    docker build . -t slaver
    docker run -p 80 -p 22 --rm -d --link splash:splash --link redis:redis --link mongo:mongo slaver
    # 上面的命令可以执行多次，模拟多个slaver的情况
    
    docker ps 查看端口映射情况
   
portia:
    
    cd portia/portiaui
    npm install && bower install
    cd node_modules/ember-cli && npm install && cd ../../
    ember build
    cd ..
    docker build . -t portia
    docker run -i -t --rm -p 9001:9001 portia
        