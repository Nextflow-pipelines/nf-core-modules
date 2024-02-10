#!/usr/bin/env python
#-*- coding: utf-8 -*-
#filename: parse_samples.py

import sys
import numpy as np
import pandas as pd
import yaml
import platform

samplesheet = "${xlsx}"

combi = pd.read_excel(samplesheet, sheet_name='比較解析組み合わせ', engine='openpyxl', index_col=0, usecols=[0,1,2], na_values='', keep_default_na=False).dropna()
combi['Control'] = combi['Control'].str.replace(' ', '')
combi['Case'] = combi['Case'].str.replace(' ', '')

# write samplesheet to csv
combi.set_index('Control').to_csv("control_case.csv")

# write sample information to yaml.
dgsdf = combi.to_dict()

combiinfo = {}
combiinfo["COMBINATION_INFORMATION"] = dgsdf
with open("combinationinfo.yml", "w") as f:
    yaml.dump(combiinfo, f, default_flow_style=False)

# write python and libraries version to yaml.
versions_this_module = {}
versions_this_module["${task.process}"] = {
    "python": platform.python_version(),
    "pandas": pd.__version__,
    "yaml": yaml.__version__,
}

with open("versions.yml", "w") as f:
    yaml.dump(versions_this_module, f, default_flow_style=False)