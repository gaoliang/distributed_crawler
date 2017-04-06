# coding=utf-8
import bson
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

# from instance import instances_collection
from models.instance import instances_collection
from models.machine import machine_collection
from models.spider import spider_collection
from slavers_control import trans_file, run_cmd


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
  return render(request, "spider_status.html", context={'instances': instances, "machines": machines})


@csrf_exempt
def add_slaver(request):
  if machine_collection.find_one({"ip": request.POST['ip']}):
    return JsonResponse({'success': False, 'reason': u'该服务器已存在'})
  if not ip_check(request.POST['ip']):
    return JsonResponse({'success': False, 'reason': u'ip地址不合法'})
  machine_doc = machine_collection.MachineDoc()
  machine_doc['ip'] = request.POST['ip']
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
  spider['machines'] = ['127.0.0.1', '192.168.168.168']
  spider.save()
  print trans_file(ip="115.159.88.44", user="ubuntu", passwd="HIGHLIGHT0111", file=upload_file,
                   place="test/sss.py")
  print run_cmd(ip="115.159.88.44", user="ubuntu", passwd="HIGHLIGHT0111", cmd="ls")
  return JsonResponse({'success': True})


def deploy_spider(request):
  # trans_file()
  pass


def run_instance(request):
  pass
