#!/usr/bin/env python
#-*- coding: utf-8 -*-
#filename: parse_customer.py

import sys
import numpy as np
import pandas as pd
import yaml
import platform

samplesheet = "${xlsx}"

df = pd.read_excel(samplesheet, sheet_name=u'サンプルシート', header=None, engine='openpyxl', skiprows=1, usecols=[1,2], na_values='', keep_default_na=False).loc[0:1]

customer_name = df.loc[0,2]
customer_inst = df.loc[1,2]

customer_info = {}
customer_info['CUSTOMER_INFORMATION'] = {
    "customer_name": customer_name,
    "customer_inst": customer_inst
}

# write customer information to yaml.
with open("customerinfo.yml", "w") as f:
    yaml.dump(customer_info, f, default_flow_style=False)

# write python and libraries version to yaml.
versions_this_module = {}
versions_this_module["${task.process}"] = {
    "python": platform.python_version(),
    "pandas": pd.__version__,
    "yaml": yaml.__version__,
}

with open("versions.yml", "w") as f:
    yaml.dump(versions_this_module, f, default_flow_style=False)