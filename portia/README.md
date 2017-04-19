Portia 可视化智能爬虫生成系统
======

Portia is a tool that allows you to visually scrape websites without any programming knowledge required. With Portia you can annotate a web page to identify the data you wish to extract, and Portia will understand based on these annotations how to scrape data from similar pages.


# Build Portia

     curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
     sudo apt-get install -y nodejs

     [workdir] portia/portiaui
     npm install -g bower
     npm install -g ember-cli@2.12
     npm install && bower install
     cd node_modules/ember-cli && npm install && cd ../../
     ember build
     cd ..
     docker build . -t portia

# Run Portia

      docker run -i -t --rm -p 9001:9001 –d portia
 
# Documentation

Documentation can be found [here](http://portia.readthedocs.org/en/latest/index.html). Source files can be found in the ``docs`` directory.

