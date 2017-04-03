# 说明

## 1. 开发环境搭建

### 1.1 安装开发依赖


安装mongodb redis python2.7

安装python依赖
```bash
pip install -r requirements/development.txt
```

### 1.2 使用virtualenv
------
### Build a local portia image

* 安装[Node.js](https://nodejs.org/en/download/package-manager/)和 [Bower](https://bower.io/#install-bower) 和 [ember-cli](https://ember-cli.com/)  


* Build
```bash
git clone https://github.com/scrapinghub/portia.git
cd portia/portiaui
npm install && bower install
cd node_modules/ember-cli && npm install && cd ../../
ember build && cd ..
docker build . -t portia
```
* Run
```bash
 docker run -i -t --rm -v ~/scrapinghub/data:/app/slyd/slyd/data/projects:rw -p 9001:9001 portia
<<<<<<< HEAD
```
=======
 ```

>>>>>>> 1d0735813c366ce1428e9cfaf99bce6ab8339aa0



------


* https://www.gitbook.com/book/piaosanlang/spiders
* https://scrapy-redis.readthedocs.io/en/stable/
* http://brucedone.com/archives/771
* https://github.com/scrapinghub/portia/ 一个可视化的scrapy工具
