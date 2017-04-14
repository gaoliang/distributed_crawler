# coding=utf-8
import json

import bson
import requests
from django.http import JsonResponse
from django.shortcuts import render
# Create your views here.
from django.views.decorators.csrf import csrf_exempt

# from instance import instances_collection
from io import BytesIO

from models.instance import instances_collection
from models.machine import machine_collection
from models.spider import spider_collection


def ip_check(ip):
    """
    检查ip地址合法性
    """
    q = ip.split('.')
    return len(q) == 4 and len(filter(lambda x: x >= 0 and x <= 255, map(int, filter(lambda x: x.isdigit(), q)))) == 4


def create_spider(request):
    spiders = [i["name"] for i in spider_collection.find()]
    machine = [i["ip"] for i in machine_collection.find()]
    return render(request, 'index.html', context={'spiders': spiders, 'machines': machine})


@csrf_exempt
def spider_status(request):
    machines = spider_collection.find_one({'name': request.POST['name']})['machines']
    print machines
    instances = instances_collection.find({'name': request.POST['name']})
    return render(request, "spider_status.html",
                  context={'instances': instances, "machines": machines, 'name': request.POST['name']})


@csrf_exempt
def add_slaver(request):
    if machine_collection.find_one({"ip": request.POST['ip']}):
        return JsonResponse({'success': False, 'reason': u'该服务器已存在'})
    if not ip_check(request.POST['ip']):
        return JsonResponse({'success': False, 'reason': u'ip地址不合法'})
    machine_doc = machine_collection.MachineDoc()
    machine_doc['ip'] = request.POST['ip']
    machine_doc['username'] = request.POST['username']
    machine_doc['password'] = request.POST['password']
    machine_doc.save()
    return JsonResponse({'success': True})
    pass


@csrf_exempt
def add_spider(request):
    upload_file = request.FILES['zip_file'].file
    if spider_collection.find_one({'name': request.POST['name']}):
        return JsonResponse({"success": False, 'reason': "爬虫名字已存在"})
    spider = spider_collection.SpiderDoc()
    try:
        spider['file'] = bson.binary.Binary(upload_file.getvalue())
    except:
        return JsonResponse({'success': False, 'reason': "未上传爬虫文件"})
    spider['name'] = request.POST['name']
    spider.save()
    return JsonResponse({'success': True})


def deploy_spider(request):
    ip = request.POST['ip']
    name = request.POST['name']
    machine = machine_collection.MachineDoc.find_one({"ip": ip})
    spider = spider_collection.SpiderDoc.find_one({'name': request.POST['name']})
    try:
        trans_file(ip, machine['username'], BytesIO(spider['file']), "test/{}.zip".format(name), machine['password'])
    except Exception as e:
        print ('*** Caught exception: %s: %s' % (e.__class__, e))
        return JsonResponse({"success": False})
    spider['machines'].append(ip)
    spider.save()
    return JsonResponse({"success": True})


def run_instance(request):
    pass


@csrf_exempt
def ajax_machines(requests):
    ips = [i["ip"] for i in machine_collection.find()]
    return JsonResponse({"ips": ips})


def trans_file(ip, port, file,spider_type='scrapy'):
    files = {'file': file}
    r = requests.post("http://{}:{}".format(ip, port), files=files, data={'type': spider_type})
    result = json.loads(r.text)
    print result
