#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import g

HEADER = ("H", "F", "R", "P", "M", "L", "Re", "I", "1G", "5G", "10G")

def output_summary(ir, sortby_list, filterby_list):
    print "%30s %8s %3s %3s %5s %3s %3s %3s %3s %3s %3s" % HEADER
    values = []
    for host, m in ir.iteritems():
        value = {
            "H": host,
            "F": m["mem_free"],
            "R": m["redis_count"],
            "P": m["proxy_count"],
            "M": g.machine_room(host), 
            "L": g.logic_machine_room(host),
            "Re": g.region(host), 
            "I": g.idc(host),
            "1G": m["remains"]["mem_1G"], 
            "5G": m["remains"]["mem_5G"], 
            "10G": m["remains"]["mem_10G"]
            }
        values.append(value)

    for f in filterby_list:
        values = [m for m in values if m[f[0]]==f[1]]

    for t in sortby_list[::-1]:
        values = sorted(values, key=lambda m: m[t], reverse=True)

    for m in values:
        host = m["H"]
        args = (host, m["F"],m["R"], m["P"], m["M"], m["L"], m["Re"], m["I"], m["1G"], m["5G"], m["10G"])
        print "%30s %8.1f %3d %3d %5s %3s %3s %3s %3d %3d %3d" % args
