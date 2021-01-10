#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import subprocess
import g, service, machine

def update_remains(m, plan):
    m["remains"] = plan

    for k, ss in m["services"].iteritems():
        if m["remains"].get(k) is not None:
            m["remains"][k] -= len(ss)
        
def generate_ir(service_list, machine_list):
    mdict = {}
    service_hosts = [s["host"] for s in service_list]
    for m in machine_list:
        if m.get("_id"):
            del m["_id"]
        mdict[m["host"]] = m
        if m["host"] not in service_hosts:
            service_list.append({"host": m["host"]})

    plan_dict = {}
    client = g.mongo_client()
    db = client.cap

    stats = {}
    for service in service_list:
        if service.get("_id"):
            del service["_id"]
        # machine level info
        host = service["host"]
        if stats.get(host) is None:
            if mdict.get(host) is None:
                continue

            minfo = mdict[host]
            stats[host] = {"host": host, 
                           "mem_free": minfo["mem_total"]*0.65 - minfo["mem_used"],
                           "mem_free_real": minfo["mem_total"] - minfo["mem_used"],
                           "mem_total": minfo["mem_total"],
                           "dirname_list": [],
                           "redis_count": 0,
                           "redis_mem": 0,
                           "proxy_count": 0}

        m = stats[host]
        if m.get("services") is None:
            m["services"] = {}

        if m.get("ports") is None:
            m["ports"] = []

        if service.get("port") is not None:
            m["ports"].append(service["port"])

        dirname = service.get("dirname")
        if dirname is None: dirname = ""
        m["dirname_list"].append(dirname)
        if dirname.startswith("redis-"):
            mem = service["mem_used"]
            m["redis_count"] += 1
            m["redis_mem"] += mem
            k = g.get_plan_field(service["mem_used"])
            if m["services"].get(k) is None:
                m["services"][k] = []
            m["services"][k].append(service)
        elif dirname.startswith("redisproxy-"):
            m["proxy_count"] += 1

        # update remainds
        plan_name = mdict[host]["plan"]
        if plan_dict.get(plan_name) is None:
            plan = db.plans.find_one({"name": plan_name})
            del plan["_id"]
            del plan["name"]
            plan_dict[plan_name] = plan
        plan = plan_dict[plan_name].copy()
        update_remains(m, plan)
    return stats

### port alloc ###

REDIS_PORT_RANGE = (9100, 9999)
PROXY_PORT_RANGE = (7000, 7999)

class ServerAllocFail(Exception): pass
class NoPortAvaliable(Exception): pass

def alloc_redis_port(host, ir):
    for p in xrange(REDIS_PORT_RANGE[0], REDIS_PORT_RANGE[1]):
        if p in ir[host]["ports"]:
            continue
        # pipe stdout to hide output
        if subprocess.call(["portease", host, str(p)], stdout=subprocess.PIPE) == 1:
            return p
    raise NoPortAvaliableException()

def alloc_proxy_uni_port(ms):
    """
    所有proxy同一个端口
    """
    for p in xrange(PROXY_PORT_RANGE[0], PROXY_PORT_RANGE[1]):
        used = False
        for m in ms:
            host = m["host"]
            # pipe stdout to hide output
            if subprocess.call(["portease", host, str(p)], stdout=subprocess.PIPE) == 0:
                used = True
                break
        if not used:
            return p
    raise NoPortAvaliableException()
