#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import subprocess
import g, service, machine, alloc

def should_ignore(m, alloced_servers):
    if "test" in m["host"] or "cache" in m["host"] or "ndb" in m["host"]:
        return True

    if m["host"] in [s["host"] for s in alloced_servers]:
        return True

    if m["proxy_count"] > 8:
        return True

    return False

def predicates_functor():
    return [
        (lambda m: m["proxy_count"] < 1, None),
        (lambda m: m["proxy_count"] < 2, None),
        (lambda m: m["proxy_count"] < 3, None),
        (lambda m: m["proxy_count"] < 4, None),
        (lambda m: m["proxy_count"] < 5, None),
        (lambda m: m["proxy_count"] < 6, None),
        (lambda m: m["proxy_count"] < 7, None),
        (lambda m: m["proxy_count"] < 8, None),
        (lambda m: m["proxy_count"] < 9, None),
        ]

def alloc_one_proxy(ir, pid, region, alloced_servers, port):
    predicates = predicates_functor()

    for predicate in predicates:
        values = [m for m in ir.values() if not should_ignore(m, alloced_servers)]
        values = [m for m in values if not g.dirname_contains(m["dirname_list"], pid)]
        values = [m for m in values if g.region(m["host"]) == region]
        values = [m for m in values if predicate[0](m)]

        if port:
            for m in values:
                if subprocess.call(["portease", m["host"], str(port)], stdout=subprocess.PIPE) == 1:
                    return {"host": m["host"]}
            continue

        if len(values) == 0:
            continue

        m = values[0]
        return {"host": m["host"]}
    raise alloc.ServerAllocFail()

