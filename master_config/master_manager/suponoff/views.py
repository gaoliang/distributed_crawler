#!/usr/bin/envpython3
import json
import logging
import re
import socket
from collections import defaultdict, OrderedDict

import configparser
import xmlrpclib

import concurrent.futures
from spiders_manager.models.machine import machine_collection
from net_utils import TimeoutServerProxy

try:  # django>=1.8
    from django.template.context_processors import csrf
except ImportError:  # django==1.7
    from django.core.context_processors import csrf
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render_to_response
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
from pathlib import Path

# from pprint import pformat


LOG = logging.getLogger(__name__)


def _get_supervisor(hostname, port=9001):
    url = "http://{}:{}".format(hostname, port)
    supervisor = TimeoutServerProxy(url, verbose=False,timeout=10)
    return supervisor


def _get_server_data(hostname, metadata, port=9001):
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


def get_data(request):
    data = _get_data([])
    return JsonResponse(data)


def get_index_template_data():
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


@ensure_csrf_cookie
def home(request, template_name="suponoff/index.html"):
    context = get_index_template_data()
    context.update(csrf(request))
    resp = render_to_response(template_name, context)
    return resp


def action(request):
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


def get_program_logs(request):
    logs = "Logs for program {}:{} in server {}".format(
        request.GET['group'], request.GET['program'], request.GET['server'])
    stream = request.GET['stream']
    assert stream in {'stdout', 'stderr', 'applog'}

    full_name = "{}:{}".format(request.GET['group'],
                               request.GET['program'])
    if stream == 'stdout':
        supervisor = _get_supervisor(request.GET['server'].split('_')[0],request.GET['server'].split('_')[1])
        try:
            logs, _offeset, _overflow = \
                supervisor.supervisor.tailProcessStdoutLog(
                    full_name, -100000, 100000)
        finally:
            supervisor("close")()
    elif stream == 'stderr':
        supervisor = _get_supervisor(request.GET['server'].split('_')[0],request.GET['server'].split('_')[1])
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
