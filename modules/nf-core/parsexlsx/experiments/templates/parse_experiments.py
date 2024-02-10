#!/usr/bin/env python
#-*- coding: utf-8 -*-
#filename: parse_experiments.py

import sys
import numpy as np
import pandas as pd
import yaml
import platform

samplesheet = "${xlsx}"

df = pd.read_excel(samplesheet, sheet_name=u'サンプルシート', header=None, engine='openpyxl', skiprows=1, usecols=[16, 17], na_values='', keep_default_na=False).loc[0:4].fillna('NoData')

sequencer = df.loc[0,17]
rrna_removal = df.loc[1,17]
library_kit = df.loc[2,17]

experiments_info = {}
experiments_info['EXPERIMENTS_INFORMATION'] = {
    "analysis": "${analysis}",
    "sequencer": sequencer,
    "rrna_removal": rrna_removal,
    "library_preparation_kit": library_kit
}

# write customer information to yaml.
with open("experimentsinfo.yml", "w") as f:
    yaml.dump(experiments_info, f, default_flow_style=False)

# write python and libraries version to yaml.
versions_this_module = {}
versions_this_module["${task.process}"] = {
    "python": platform.python_version(),
    "pandas": pd.__version__,
    "yaml": yaml.__version__,
}

with open("versions.yml", "w") as f:
    yaml.dump(versions_this_module, f, default_flow_style=False)