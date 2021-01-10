#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import re
from datetime import datetime
from bson.objectid import ObjectId

import g

def show_services():
    sl = load_service_list()
    for s in sl:
        print s

def load_service_list():
    client = g.mongo_client()
    db = client.cap
    cursor = db.services.find()
    results = []
    for s in cursor:
        results.append(s)
    return results

def save_service_list(services):
    client = g.mongo_client()
    db = client.cap
    db.services.drop()
    db.services.insert(services)

def take_service_list(services):
    client = g.mongo_client()
    db = client.cap
    commit_service_list(services)
    db.services.insert(services)

def commit_service_list(services):
    client = g.mongo_client()
    db = client.cap
    db.serviceslog.insert({"services": services, "time": datetime.now()})

def get_commitlog_by_dbid(dbid):
    client = g.mongo_client()
    db = client.cap
    log = db.serviceslog.find_one({"_id": ObjectId(dbid)})
    return log

def drop_commit(dbid):
    client = g.mongo_client()
    db = client.cap
    log = db.serviceslog.find_one({"_id": ObjectId(dbid)})
    for s in log["services"]:
        db.services.remove({"host": s["host"], "port": s["port"]})
    db.serviceslog.remove({"_id": ObjectId(dbid)})

def get_commit_list():
    client = g.mongo_client()
    db = client.cap
    logs = db.serviceslog.find()
    return logs

def new_redis_service(host, port, mem, pid):
    service = {}
    service["host"] = host
    if pid:
        service["dirname"] = "redis-%s-%d" % (pid, port)
    else:
        service["dirname"] = "redis-%d" % port
    service["mem_used"] = mem
    service["port"] = port
    return service

def new_proxy_service(host, pid, port):
    service = {}
    service["host"] = host
    service["dirname"] = "redisproxy-%s" % pid
    service["port"] = port
    return service

def drop_results(dbid):
    client = g.mongo_client()
    db = client.cap
    db.results_log.drop()
    db.results_log.insert(results)
    
def update_service_list(raw_file):
    """
    格式可变，目前格式是<ip> <dirname> <port> <datasize> <memused> <memused_human> <memrss> <mem> <human> <role> <version> <dirname_again>
    192.168.1.1 redis-chunfeng-shard9 9911 1.8G 680351624 648.83M 696057856 680349280 648.83M slave 2.4.17 redis-chunfeng-shard9
    """
    services = []
    for line in open(raw_file, "r"):
        xs = re.split("\s+", line.strip())
        host = g.ip2hostname(xs[0])
        if len(xs) < 3:
            continue

        service = {}
        
        service["host"] = host[:-10]
        service["port"] = int(xs[2])
        dirname = service["dirname"] = xs[1]
        if not dirname.startswith("redis-") and not dirname.startswith("redisproxy-"):
            continue
        if dirname.startswith("redis-"):
            service["port"] = int(xs[2])
            service["data_size"] = g.cap_to_mb(xs[3])
            service["mem_used"] = int(float(xs[6])/1000/1000)
            service["role"] = xs[9]
            service["version"] = xs[10]
            ds = dirname.split("-shard")
            if len(ds) == 2:
                suf = ds[1].strip()
                if len(suf.split("-")) == 2:
                    suf = suf.split("-")[0]
                service["shard_num"] = int(suf)
            else:
                service["shard_num"] = 999

        services.append(service)
    save_service_list(services)

    # drop commits
    client = g.mongo_client()
    db = client.cap
    db.serviceslog.drop()
    return services

def get_services_by_host(host):
    sl = load_service_list()
    return [s for s in sl if s["host"] == host]

def get_apps_by_host(host):
    host = host.strip()
    sl = get_services_by_host(host)
    app_set = set()
    for s in [s["dirname"] for s in sl]:
        if s.startswith("redis-"):
            app_set.add(re.split("-shard", s[6:])[0])
        elif s.startswith("redisproxy-"):
            app_set.add(s[11:])
    return app_set

if __name__ == "__main__":
    app_set = set()
    for line in open("/home/users/meetbill/tmp.jx", "r"):
        for app in get_apps_by_host(line):
            app_set.add(app)
    for app in app_set:
        print app
