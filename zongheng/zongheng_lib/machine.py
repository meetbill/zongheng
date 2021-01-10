#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import g

def show_machines():
    ml = load_machine_list()
    for m in ml:
        print m

def load_machine_list(skip_ban=True):
    client = g.mongo_client()
    db = client.cap
    cursor = db.machines.find()
    results = []
    ban_list = load_banned_machine_list()
    for s in cursor:
        if skip_ban:
            if s["host"] not in ban_list:
                results.append(s)
        else:
            results.append(s)
    return results

def save_machine_list(machines):
    client = g.mongo_client()
    db = client.cap
    db.machines.drop()
    db.machines.insert(machines)

def update_machine_memory(host, mem_used):
    client = g.mongo_client()
    db = client.cap
    db.machines.update({"host": host}, {"$inc": {"mem_used": mem_used}})

def load_banned_machine_list():
    client = g.mongo_client()
    db = client.cap
    cursor = db.banned_machines.find()
    results = []
    for s in cursor:
        results.append(s["host"])
    return results

def save_banned_machine_list(hosts):
    client = g.mongo_client()
    db = client.cap
    for host in hosts:
        db.banned_machines.insert({"host": host})

def remove_banned_machine_list(hosts):
    client = g.mongo_client()
    db = client.cap
    for host in hosts:
        db.banned_machines.remove({"host": host})

def add_banned_machine_list(hosts):
    save_banned_machine_list(hosts)

def update_machine_list(raw_file):
    """
    格式可变，目前格式是<host> <mem_total> <mem_used>
    """
    machines = []
    for line in open(raw_file, "r"):
        xs = line.strip().split(" ")
        host = g.ip2hostname(xs[0])
        host = host[:-10]
        machine_info = {
                "host": host,
                "mem_total": int(xs[1]), # in MB
                "mem_used": int(xs[2]),  # in MB
                "plan": g.pick_std_plan(xs[1]),
                "idc": g.idc(host),
                "logic_machine_room": g.logic_machine_room(host),
                "machine_room": g.machine_room(host),
            }
        machines.append(machine_info)
    save_machine_list(machines)
    return machines
