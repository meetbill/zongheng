#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import subprocess
import g, service, machine, alloc

def should_ignore(m, mem, alloced_servers):
    if "test" in m["host"] or "cache" in m["host"] or "ndb" in m["host"] or m["mem_free"] < mem:
        return True

    if m["host"] in [s["host"] for s in alloced_servers]:
        return True

    if m["proxy_count"] > 8:
        return True

    return False

def predicates_functor(mem):
    return [
        (lambda m: m["remains"]["mem_1G"] > 3 and m["remains"]["mem_5G"] > 3 and m["remains"]["mem_10G"] > 3, 
         lambda m: m["mem_free"]),

        (lambda m: m["remains"]["mem_1G"] > 2 and m["remains"]["mem_5G"] > 2 and m["remains"]["mem_10G"] > 2, 
         lambda m: m["mem_free"]),

        (lambda m: m["remains"]["mem_1G"] > 1 and m["remains"]["mem_5G"] > 1 and m["remains"]["mem_10G"] > 1, 
         lambda m: m["mem_free"]),

        (lambda m: m["remains"]["mem_1G"] > 0 and m["remains"]["mem_5G"] > 0 and m["remains"]["mem_10G"] > 0, 
         lambda m: m["mem_free"]),

        (lambda m: m["remains"]["mem_1G"] >= 0 and m["remains"]["mem_5G"] >= 0 and m["remains"]["mem_10G"] >= 0, 
         lambda m: m["mem_free"]),

        (lambda m: m["remains"][g.get_plan_field(mem)] > 0,
         lambda m: m["remains"][g.get_plan_field(mem)]),

        (lambda m: m["remains"][g.get_plan_field(mem)] >= 0,
         lambda m: m["remains"][g.get_plan_field(mem)]),

        (lambda m: True, lambda m: m["mem_free"]),
        ]

def alloc_one_redis(ir, pid, mem, region, alloced_servers, exclude_mrs):
    predicates = predicates_functor(mem)

    for predicate in predicates:
        values = [m for m in ir.values() if not should_ignore(m, mem, alloced_servers)]

        # filter hosts by pid?
        if pid:
            values = [m for m in values if not g.dirname_contains(m["dirname_list"], pid)]

        values = [m for m in values if g.region(m["host"]) == region]
        values = [m for m in values if g.machine_room(m["host"]) not in exclude_mrs]

        values = [m for m in values if predicate[0](m)]
        trip = sorted(values, key=predicate[1], reverse=True)

        if len(trip) == 0:
            continue

        host = trip[0]["host"]
        port = alloc.alloc_redis_port(host, ir)
        return {"host": host, "port": port}
    raise alloc.ServerAllocFail()
