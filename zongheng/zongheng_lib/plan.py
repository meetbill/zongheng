#!/usr/bin/env python

import g

if __name__ == "__main__":
    client = g.mongo_client()
    db = client.cap
    db.plans.drop()

    # 48G  45
    # 64G  250
    # 96G  6
    # 128G 100

    # 1G 2000
    # 5G 1500
    # 10G 1500

    plan = {
        "name": "plan_48G_std",
        "mem_1G": 5,
        "mem_5G": 2,
        "mem_10G": 2,
        }
    db.plans.insert(plan)

    plan = {
        "name": "plan_64G_std",
        "mem_1G": 5,
        "mem_5G": 3,
        "mem_10G": 3,
        }
    db.plans.insert(plan)

    plan = {
        "name": "plan_96G_std",
        "mem_1G": 5,
        "mem_5G": 5,
        "mem_10G": 5,
        }
    db.plans.insert(plan)

    plan = {
        "name": "plan_128G_std",
        "mem_1G": 5,
        "mem_5G": 6,
        "mem_10G": 6,
        }
    db.plans.insert(plan)
