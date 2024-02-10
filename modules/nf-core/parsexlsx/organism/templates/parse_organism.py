#!/usr/bin/env python
#-*- coding: utf-8 -*-
#filename: parse_samples.py

import sys
import numpy as np
import pandas as pd
import yaml
import platform

samplesheet = "${xlsx}"

df = pd.read_excel(samplesheet, sheet_name=u'サンプルシート', header=[0,1], engine='openpyxl', skiprows=7, na_values='', keep_default_na=False).dropna(how='all')

organism = df['生物種'].iloc[:,0][0]

# write sample information to yaml.
organism_info = {}
organism_info["ORGANISM_INFORMATION"] = {
    "organism_name": organism,
    "reference_name": "${params.genome}"
}

with open("organisminfo.yml", "w") as f:
    yaml.dump(organism_info, f, default_flow_style=False)

# write python and libraries version to yaml.
versions_this_module = {}
versions_this_module["${task.process}"] = {
    "python": platform.python_version(),
    "pandas": pd.__version__,
    "yaml": yaml.__version__,
}

with open("versions.yml", "w") as f:
    yaml.dump(versions_this_module, f, default_flow_style=False)