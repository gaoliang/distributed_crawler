"""crawler_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from views import *

urlpatterns = [
  url(r'^admin/', admin.site.urls),
  url(r'^$', index),
  url(r'^spider_status', spider_status, name="spider_status"),
  url(r'^add_slaver', add_slaver, name='add_slaver'),
  url(r'^add_spider', add_spider, name='add_spider'),
  url(r'^ips', ajax_machines, name='ajax_machines'),
  url(r'^deploy_spider', deploy_spider, name="deploy_spider"),
  url(r'^action$', action, name='suponoff_action'),
  url(r'^data$', get_data, name='suponoff_data'),
  url(r'^data/program-logs$', get_program_logs,
      name='suponoff_program_logs'),
  url(r'^del_deployed_spider',del_deployed_spider,name='del_deployed_spider')
]
