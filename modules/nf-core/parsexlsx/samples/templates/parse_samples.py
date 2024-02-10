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
sdf = pd.DataFrame(index=df.index)
sdf['group_original'] = df['※サンプル群\\n（Replicate）'].fillna(method='ffill').astype(str)
sdf['group'] = sdf['group_original'].str.replace(r'(_|\\/|\\*|-|:|;)', '.', regex=True)
sdf['group'] = sdf['group'].str.replace(r'\\+', '.plus.', regex=True)
sdf['group'] = sdf['group'].str.replace(r'^([0-9].*)', 'X\\\\1', regex=True)
sdf['sample_original'] = df['※サンプル名'].fillna(method='ffill').astype(str)
sdf['sample'] = sdf['sample_original'].str.replace(r'(_|\\/|\\*|-|:|;)', '.', regex=True)
sdf['sample'] = sdf['sample'].str.replace(r'\\+', '.plus.', regex=True)
sdf['sample'] = sdf['sample'].str.replace(r'^([0-9].*)', 'X\\\\1', regex=True)
sdf['directory'] = [str(i).split('\\\\')[-1] for i in df[u'Fastqファイル名 ※社内用'][u'フォルダ名'].fillna(method='ffill')]
sdf['directory'] = [str(int(i)) if type(i) == float else str(i) for i in sdf['directory']]

for rn in [1,2]:
    sdf['fastq_{}'.format(rn)] = sdf['directory'] + '/' + df[u'Fastqファイル名 ※社内用']['R{}'.format(rn)].fillna('null').str.replace(r'(_fastq.*|_fq.*|\\.fastq.*|\\.html|\\.txt)', '.fastq.gz', regex=True)
    sdf['read_num_{}'.format(rn)] = df[u'Read数']['R{}'.format(rn)].fillna('null')
for c in ['group', 'sample', 'directory', 'fastq_1', 'fastq_2']:
    sdf[c] = sdf[c].str.replace(' ', '')

sdf = sdf[sdf['fastq_1'] != 'NoData']
lane = sdf.groupby(['group', 'sample'])['fastq_1'].apply(lambda x: [i+1 for i,j in enumerate(x)])
sdf['lane'] = lane
sdf = sdf.loc[:,['group', 'sample', 'group_original', 'sample_original', 'directory', 'lane', 'fastq_1', 'fastq_2', 'read_num_1', 'read_num_2']]
sdf['id'] = sdf['group'] + '_' + sdf['sample']

# write samplesheet to csv
sdf.set_index('id').to_csv("samplesheet.csv")

# make sample information

gsdf = sdf.groupby(['id', 'group', 'sample', 'group_original', 'sample_original'])['lane', 'fastq_1'].apply(lambda x: dict(x.values)).to_frame(name='fastq_1')
gsdf['fastq_2'] = sdf.groupby(['id', 'group', 'sample', 'group_original', 'sample_original'])['lane', 'fastq_2'].apply(lambda x: dict(x.values))

gsdf['calc_read_num_1'] = sdf.groupby(['id', 'group', 'sample', 'group_original', 'sample_original'])['read_num_1'].sum()
gsdf['calc_read_num_2'] = sdf.groupby(['id', 'group', 'sample', 'group_original', 'sample_original'])['read_num_2'].sum()

dgsdf = gsdf.reset_index().set_index('id').T.to_dict()

# write sample information to yaml.
sample_info = {}
sample_info["SAMPLE_INFORMATION"] = dgsdf
with open("sampleinfo.yml", "w") as f:
    yaml.dump(sample_info, f, default_flow_style=False)

# write python and libraries version to yaml.
versions_this_module = {}
versions_this_module["${task.process}"] = {
    "python": platform.python_version(),
    "pandas": pd.__version__,
    "yaml": yaml.__version__,
}

with open("versions.yml", "w") as f:
    yaml.dump(versions_this_module, f, default_flow_style=False)