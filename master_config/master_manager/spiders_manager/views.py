# coding=utf-8
import json
import logging
import re
import configparser
import bson
import requests
import concurrent.futures
from django.shortcuts import render
from collections import defaultdict, OrderedDict
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from models.instance import instances_collection
from models.machine import machine_collection
from models.spider import spider_collection
from net_utils import TimeoutServerProxy
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from pathlib import Path

LOG = logging.getLogger(__name__)


@csrf_exempt
def index(request):
    """爬虫管理主界面"""
    spiders = [i["name"] for i in spider_collection.find()]

    machine = ["{}:{}".format(i["hostname"], i['port']) for i in machine_collection.find()]
    context = get_index_template_data()
    context['spiders'] = spiders
    context['machines'] = machine
    return render(request, 'index.html', context=context)


@csrf_exempt
def spider_status(request):
    """爬虫状态ajax请求"""
    machines = spider_collection.find_one({'name': request.POST['name']})['machines']
    instances = instances_collection.find({'name': request.POST['name']})
    return render(request, "spider_status.html",
                  context={"machines": machines, 'name': request.POST['name']})


@csrf_exempt
def add_slaver(request):
    """
    添加新的slaver服务器的ajax请求处理函数
    """
    machine_doc = machine_collection.MachineDoc()
    machine_doc['hostname'] = request.POST['hostname']
    machine_doc['port'] = request.POST['port']
    machine_doc.save()
    return JsonResponse({'success': True})


@csrf_exempt
def add_spider(request):
    """
    添加新的爬虫项目到系统的ajax处理函数
    """
    upload_file = request.FILES['zip_file'].file
    filename = request.FILES['zip_file'].name
    if spider_collection.find_one({'name': filename.split('.')[0]}):
        return JsonResponse({"success": False, 'reason': "爬虫名字已存在"})
    spider = spider_collection.SpiderDoc()
    spider['filename'] = filename
    try:
        spider['file'] = bson.binary.Binary(upload_file.getvalue())
    except:
        return JsonResponse({'success': False, 'reason': "未上传爬虫文件"})
    spider['name'] = filename.split('.')[0]

    spider['anti_ban'] = request.POST.getlist('anti_ban')
    spider['redis_address'] = request.POST['redis_address']
    spider['mongo_address'] = request.POST['mongo_address']

    spider.save()
    gen_conf(spider)
    return JsonResponse({'success': True})


@csrf_exempt
def deploy_spider(request):
    """
    部署爬虫到指定服务器的ajax请求处理函数
    """
    ip = request.POST['ip']
    hostname = ip.split(':')[0]
    port = ip.split(':')[1]
    spider = spider_collection.SpiderDoc.find_one({'name': request.POST['name']})
    custom_settings = gen_conf(spider)
    custom_settings = gen_conf(spider)

    trans_file(hostname, port, filename=spider['filename'], file=BytesIO(spider['file']),
               custom_settings=custom_settings)
    if ip in spider['machines']:
        return JsonResponse({"success": False})
    spider['machines'].append(ip)
    spider.save()
    return JsonResponse({"success": True})


def run_instance(request):
    pass


@csrf_exempt
def ajax_machines(request):
    """
    ajax获取可用的服务器列表 
    """
    hostnames = ["{}:{}".format(i["hostname"], str(i['port'])) for i in machine_collection.find()]
    return JsonResponse({"ips": hostnames})


def trans_file(hostname, port, file, filename, custom_settings, spider_type='scrapy', ):
    """
    传输爬虫文件到服务器
    :param hostname: 服务器地址
    :param port: 服务器端口号
    :param file: 文件，以zip格式压缩打包，注意根目录下一定有scrapy.cfg文件。
    :param spider_type: 爬虫类型，两个值可选 "scrapy":scrapy原生爬虫，"portia":由portia生成的爬虫
    :return: 返回json，格式为 {"success":True or False}
    """
    files = {'file': (filename, file)}
    r = requests.post("http://{}:{}/api/upload".format(hostname, port), files=files,
                      data={'type': spider_type, "custom_settings": custom_settings})
    print r.text
    result = json.loads(r.text)
    print result


def _get_supervisor(hostname, port=9001):
    """
    获取指定hostname的ServerProxy对象
    :param hostname: 服务器地址
    :param port: 服务器端口号
    :return: 
    """
    url = "http://{}:{}".format(hostname, port)
    supervisor = TimeoutServerProxy(url, verbose=False, timeout=10)
    return supervisor


def _get_server_data(hostname, metadata, port=9001):
    """
    获取服务器的supervisor信息
    :param hostname: 服务器地址
    :param metadata: 元数据
    :param port: 端口号
    :return: 包含服务器信息的字典
    """
    supervisor = _get_supervisor(hostname, port)
    try:
        processes = supervisor.supervisor.getAllProcessInfo()
        server = {}
        pids = []
        for process in processes:
            if process["pid"]:
                pids.append(process["pid"])
            group_name = process['group']
            group = server.setdefault(group_name,
                                      {"processes": [],
                                       "total_processes": 0,
                                       "running_processes": 0})
            process["can_be_stopped"] = process["statename"] in {"RUNNING"}
            process["can_be_restarted"] = process["statename"] in {"RUNNING"}
            process["can_be_started"] = \
                process["statename"] in {"STOPPED", "EXITED"}
            if process["statename"] in {"RUNNING"}:
                group['running_processes'] += 1
            else:
                group['has_not_running_processes'] = True
            group['total_processes'] += 1
            group['processes'].append(process)

            if group['total_processes'] == 1:
                group_tags = set()
                for server_regex, group_regex, tags in metadata:
                    group_match = group_regex.match(group_name)
                    server_match = server_regex.match(hostname)
                    if group_match and server_match:
                        group_tags.update(tags)
                group['tags'] = list(sorted(group_tags))
    finally:
        supervisor("close")()
    return server


def _get_data(metadata):
    # hostname -> group -> process
    services_by_host = OrderedDict()
    # servers = settings.SUPERVISORS
    servers = list(machine_collection.find())
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        for server in servers:
            hostname = server['hostname']
            port = server['port']
            try:
                server_data = executor.submit(_get_server_data, hostname, metadata, port)
                services_by_host[hostname + "_" + str(port)] = server_data
            except Exception as e:
                print "connect error on {}".format(server)
        for server in servers:
            hostname = server['hostname']
            port = server['port']
            try:
                services_by_host[hostname + "_" + str(port)] = services_by_host[hostname + "_" + str(port)].result()
            except:
                del services_by_host[hostname + "_" + str(port)]
    return services_by_host


@csrf_exempt
def get_data(request):
    """
    处理获取服务器信息的请求
    """
    data = _get_data([])
    return JsonResponse(data)


def get_index_template_data():
    """
    获取主页的context数据。
    """
    metadata, tags_config, taggroups_dict = _get_metadata_conf()
    services_by_host = _get_data(metadata)

    all_tags = set()
    for server_data in services_by_host.values():
        for group in server_data.values():
            all_tags.update(group['tags'])

    tags_by_group = defaultdict(set)
    for tag_name in all_tags:
        tag = tags_config[tag_name]
        tags_by_group[tag.taggroup].add(tag_name)
    taggroups = []
    for name, tags in sorted(tags_by_group.items()):
        taggroups.append((taggroups_dict[name].label, sorted(tags)))

    # sort everything
    data = []
    for server, groups in sorted(services_by_host.items()):
        data.append((server, sorted(groups.items())))

    context = {
        "data": data,
        "taggroups": taggroups,
        'tags_config': tags_config,
        "SITE_ROOT": settings.SITE_ROOT,
    }
    return context


@csrf_exempt
def action(request):
    """
    处理对服务器任务的调度信息。
    """
    server = request.POST['server']
    supervisor = _get_supervisor(server.split('_')[0], server.split('_')[1])
    try:
        if 'action_start_all' in request.POST:
            supervisor.supervisor.startAllProcesses()
            return HttpResponse(json.dumps("ok"),
                                content_type='application/json')
        elif 'action_stop_all' in request.POST:
            supervisor.supervisor.stopAllProcesses()
            return HttpResponse(json.dumps("ok"),
                                content_type='application/json')
        program = "{}:{}".format(request.POST['group'], request.POST['program'])
        if 'action_start' in request.POST:
            supervisor.supervisor.startProcess(program)
        elif 'action_stop' in request.POST:
            supervisor.supervisor.stopProcess(program)
        elif 'action_restart' in request.POST:
            supervisor.supervisor.stopProcess(program)
            supervisor.supervisor.startProcess(program)

    finally:
        supervisor("close")()
    return redirect(settings.SITE_ROOT)


@csrf_exempt
def get_program_logs(request):
    """
    获取指定服务器的任务信息
    """
    logs = "Logs for program {}:{} in server {}".format(
        request.GET['group'], request.GET['program'], request.GET['server'])
    stream = request.GET['stream']
    assert stream in {'stdout', 'stderr', 'applog'}

    full_name = "{}:{}".format(request.GET['group'],
                               request.GET['program'])
    if stream == 'stdout':
        supervisor = _get_supervisor(request.GET['server'].split('_')[0], request.GET['server'].split('_')[1])
        try:
            logs, _offeset, _overflow = \
                supervisor.supervisor.tailProcessStdoutLog(
                    full_name, -100000, 100000)
        finally:
            supervisor("close")()
    elif stream == 'stderr':
        supervisor = _get_supervisor(request.GET['server'].split('_')[0], request.GET['server'].split('_')[1])
        try:
            logs, _offeset, _overflow = \
                supervisor.supervisor.tailProcessStderrLog(
                    full_name, -100000, 100000)
        finally:
            supervisor("close")()
    elif stream == 'applog':
        pass
    else:
        raise AssertionError
    return HttpResponse(logs, content_type='text/plain')


class TagConfig:  # pylint: disable=R0903
    enabled_by_default = True
    taggroup = 'other'


class TagGroup:  # pylint: disable=R0903
    label = ''


def _get_metadata_conf():
    mappings = []
    tags_config = defaultdict(TagConfig)
    taggroups = defaultdict(TagGroup)

    metadata_dir = getattr(settings, "METADATA_DIR", None)
    if not metadata_dir:
        return mappings, tags_config, taggroups

    for fname in Path(metadata_dir).iterdir():
        config = configparser.ConfigParser()
        config.read(str(fname))

        for section in config.sections():

            if section.startswith("meta:"):
                group_regex = re.compile(config[section].get("group", '.*'))
                server_regex = re.compile(config[section].get("server", '.*'))
                tags = config[section].get("tags")
                if tags is None:
                    tags = frozenset()
                else:
                    tags = {tag.strip() for tag in tags.split(',')}
                mappings.append((server_regex, group_regex, tags))

            elif section.startswith("tag:"):
                _, _, tag_name = section.partition("tag:")

                enabled = config[section].getboolean("enabled_by_default", True)
                tags_config[tag_name].enabled_by_default = enabled

                taggroup = config[section].get("taggroup", 'other')
                tags_config[tag_name].taggroup = taggroup

            elif section.startswith("taggroup:"):
                _, _, taggroup_name = section.partition("taggroup:")
                label = config[section].get("label", '')
                taggroups[taggroup_name].label = label

    return mappings, tags_config, taggroups


def del_deployed_spider(request):
    name = request.POST['name']
    machines = spider_collection.find_one({"name": name})['machines']
    for machine in machines:
        r = requests.post("http://{}/api/delete".format(machine), data={'name': name})
        print r.text
    spider = spider_collection.SpiderDoc.find_one({"name": name})
    spider['machines'] = []
    spider.save()
    return JsonResponse({'success': True})


def del_spider(request):
    name = request.POST['name']
    machines = spider_collection.find_one({"name": name})['machines']
    for machine in machines:
        r = requests.post("http://{}/api/delete".format(machine), data={'name': name})
        print r.text
    spider_collection.remove({"name": name})
    return JsonResponse({'success': True})


def normal_scrapy_to_distributed(scrapy_files):
    pass


def gen_conf(spider_info_dict):
    conf_template = """[spider_custom_settings]
enable_cookies={enable_cookies}
download_delay = {download_delay}
random_ua = {random_ua}

;[mongo_settings]
;mongo_host = {mongo_host}
;mongo_port = {mongo_port}

[redis_setting]
redis_host = {redis_host}
redis_port = {redis_port}

[splash_setting]
enable_splash = {enable_splash}
splash_url = http://127.0.0.1:8050

"""
    conf_dict = {}
    conf_dict['enable_cookies'] = "false" if "disable_cookie" in spider_info_dict['anti_ban'] else "true"
    conf_dict['download_delay'] = 2 if "request_delay" in spider_info_dict['anti_ban'] else 0.25
    conf_dict['enable_splash'] = "true" if "enable_js" in spider_info_dict['anti_ban'] else "false"
    conf_dict['random_ua'] = "true" if "random_ua" in spider_info_dict['anti_ban'] else "false"
    conf_dict['mongo_host'] = spider_info_dict['mongo_address'].split(':')[0]
    conf_dict['mongo_port'] = spider_info_dict['mongo_address'].split(':')[1]
    conf_dict['redis_host'] = spider_info_dict['redis_address'].split(':')[0]
    conf_dict['redis_port'] = spider_info_dict['redis_address'].split(':')[1]
    return conf_template.format(**conf_dict)
