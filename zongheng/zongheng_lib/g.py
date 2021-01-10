#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import pymongo as mongo

def pick_std_plan(mem):
    n = int(mem)
    if n < 50000:
        return "plan_48G_std"
    elif n < 70000:
        return "plan_64G_std"
    elif n < 100000:
        return "plan_96G_std"
    elif n < 130000:
        return "plan_128G_std"
    elif n < 200000:
        return "plan_128G_std"

def mongo_client():
    client = mongo.MongoClient("127.0.0.1", 27017)
    return client

def get_plan_field(mem):
    if mem <= 1000:
        return "mem_1G"
    elif mem <= 5000:
        return "mem_5G"
    else:
        return "mem_10G"

def cap_to_gb(cap):
    n = float(cap[:-1])
    if cap.endswith("M"):
        n /= 1000
    elif cap.endswith("K"):
        n /= 1000*1000
    return int(n)

def cap_to_mb(cap):
    n = float(cap[:-1])
    if cap.endswith("G"):
        n *= 1000
    elif cap.endswith("K"):
        n /= 1000
    return int(n)

IdcMap = {
    "bjxx":  "bj",
    "njxx":  "nj",
    "gzxx":  "gz",
}

RegionMap = {
    "bjxx":  "bj",
    "njxx":  "nj",
    "gzxx":  "gz",
}

LogicMachineRoomMap = {
    "bjxx":  "bj",
    "njxx":  "nj",
    "gzxx":  "gz",
}

def machine_room(host):
    return host.split(".")[-1]

def logic_machine_room(host):
    mr = machine_room(host)
    return LogicMachineRoomMap[mr]

def region(host):
    mr = machine_room(host)
    return RegionMap[mr]

def idc(host):
    mr = machine_room(host)
    return IdcMap[mr]

def ip2hostname(ip):
    try:
        tup = socket.gethostbyaddr(ip)
        return tup[0]
    except socket.gaierror, err:
        return "unknown ip" + ip

def dirname_contains(dir_list, pid):
    for d in dir_list:
        if pid in d:
            return True
    return False

