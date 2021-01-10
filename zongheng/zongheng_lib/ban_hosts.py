#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import g, service, machine
import optparse, sys

if __name__ == "__main__":
    parser = optparse.OptionParser(usage="usage: %prog -f <file>")
    parser.add_option("-f", "--file", type="string", help="host list file to be updated")
    parser.add_option("-a", "--add-file", type="string", help="host list file to be added")
    parser.add_option("-l", "--list", action="store_true", help="list hosts banned")

    (options, args) = parser.parse_args()

    if options.file is None and options.list is None and options.add_file is None:
        parser.print_help()
        sys.exit(1)

    if options.file:
        filename = options.file
        client = g.mongo_client()
        db = client.cap
        db.banned_machines.drop()

        for line in open(filename, "r"):
            host = line.strip()
            if host == "":
                continue
            db.banned_machines.insert({"host": host})

    if options.add_file:
        filename = options.add_file
        client = g.mongo_client()
        db = client.cap

        for line in open(filename, "r"):
            host = line.strip()
            if host == "":
                continue
            db.banned_machines.insert({"host": host})

    if options.list:
        hosts = machine.load_banned_machine_list()
        for h in hosts:
            print h
