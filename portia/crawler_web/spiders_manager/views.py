# coding=utf-8
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

# from instance import instances_collection
from models.instance import instances_collection
from models.machine import machine_collection


def ip_check(ip):
  """
  检查ip地址合法性
  """
  q = ip.split('.')
  return len(q) == 4 and len(filter(lambda x: x >= 0 and x <= 255, map(int, filter(lambda x: x.isdigit(), q)))) == 4


def create_spider(request):
  spiders = set([i['name'] for i in instances_collection.find()])
  return render(request, 'index.html', context={'spiders': spiders})


@csrf_exempt
def spider_status(request):
  instances = instances_collection.find({'name': request.POST['name']})
  return render(request, "spider_status.html", context={'instances': instances})


@csrf_exempt
def add_slaver(request):
  if machine_collection.find_one({"ip": request.POST['ip']}):
    return JsonResponse({'success': False, 'reason': u'该服务器已存在'})
  if not ip_check(request.POST['ip']):
    return JsonResponse({'success': False, 'reason': u'ip地址不合法'})
  machine_doc = machine_collection.MachineDoc()
  machine_doc['ip'] = '127.0.0.1'
  machine_doc.save()
  return JsonResponse({'success': True})
  pass


@csrf_exempt
def add_spider(request):
  print request.POST
  return JsonResponse({'status': 'ok'})


def trans_file(ip, file, place):
  """
  :param ip: 目标服务器ip
  :param file: 需要传输的文件
  :param place: 目标服务器的存放位置
  :return: 是否传输成功
  """
  pass


def run_cmd(ip, cmd):
    """
    :param ip: 目标服务器ip
    :param cmd: 目标服务器ip执行的命令
    :return: 执行的反馈
    """
