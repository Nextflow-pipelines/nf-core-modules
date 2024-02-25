#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, shutil, re, csv, yaml, json, argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
from docx import Document
from docx.shared import Inches, Cm
from docx.enum.table import WD_ROW_HEIGHT, WD_ROW_HEIGHT_RULE

dtnow = datetime.now()

def testKeys_old(keys, text):
    hitKeys = []
    for key in keys:
        braketkey = '{' + key + '}'
        if (braketkey in text):
            hitKeys.append(key)
    return(hitKeys)

def testKeys(keys, text):
    def tester(key):
        return( ('{' + key + '}') in text )

    return(list(filter(tester, keys)))

def modDocument(doc, mInfo):

    tags = {
            'DATE' : dtnow.strftime("%Y-%m-%d"),
            'CUSTOMERNAME' : mInfo["customer_name"],
            'CUSTOMERINSTITUTE' : mInfo["customer_inst"].split(" ")[0],
            'ANALYSIS' : mInfo["analysis"],
            'SEQUENCER' : mInfo["sequencer"],
            'RRNA' : mInfo["rRNA_removal_kit"],
            'LIBRARY' : mInfo["library_preparation_kit"],
#          'DIRTREE' : getTree(mInfo),
            'COMMONNAME' : mInfo["organism"],
#          'SCIENTIFICNAME' : mInfo["scientific_name"],
            'GENOMEASSEMBLY' : mInfo["reference"],
        }
    keys = tags.keys()

    for para in doc.paragraphs:
        hitKeys = testKeys(tags, para.text)
        if len(hitKeys) > 0:
#            print("{}: {}".format(hitKeys, para.text))
            inline = para.runs
            # Loop added to work with runs (strings with same style)
            for i in range(len(inline)):
                textMod = inline[i].text.replace('{','').replace('}','')
                for hitKey in hitKeys:
                    textMod = textMod.replace(hitKey, tags[hitKey])
#                print("({}) {} ===> {}".format(i, inline[i].text, textMod))
                inline[i].text = textMod

def modPictutre(doc):

    tags = {
            'WORKFLOW' : ["workflow.png", 15, 20, "図1. 解析ワークフロー"],
            'CONTENTS' : ["contents.png", 15, 10, "図2. 解析フォルダ構成"]
            #'HEATMAP' : ["heatmap.png", 15, 10, "図2. 発現遺伝子のクラスタリング結果(ヒートマップ)"]
        }
    keys = tags.keys()

    for para in doc.paragraphs:
        hitKeys = testKeys(tags, para.text)
        if len(hitKeys) > 0:
#            print("{}: {}".format(hitKeys, para.text))
            inline = para.runs
            # Loop added to work with runs (strings with same style)
            for hitKey in hitKeys:
                textMod1 = inline[0].text.replace('{','').replace('}','').replace(hitKey, '')
                textMod2 = inline[1].text.replace('{','').replace('}','').replace(hitKey, tags[hitKey][3])
                inline[0].text = textMod1
                inline[1].text = textMod2
                inline[0].add_picture(tags[hitKey][0], width=Cm(tags[hitKey][1]), height=Cm(tags[hitKey][2]))

            #for i in range(len(inline)):
            #    textMod = inline[i].text.replace('{','').replace('}','')
            #    for hitKey in hitKeys:
            #        textMod = textMod.replace(hitKey, tags[hitKey][0])
            #    print("({}) {} ===> {}".format(i, inline[i].text, textMod))
            #    inline[i].text = textMod

def readMappingStat(mappingStat):
    with open(mappingStat, 'r') as f:
        reader = csv.reader(f, delimiter = '\t')
        header = next(reader)
        data = []
        for row in reader:
            rowT = row[0].split('_')
            rowD = list(map(lambda d: "{:,}".format(int(d)), row[2:5:]))
            data.append(rowT + rowD)
        return(data)

def addMappingTable(table, mappingStat):
    mtx = readMappingStat(mappingStat)
    # mtx_sorted = sorted(mtx, key = lambda d: d[1])
    # for drow in mtx_sorted:
    for drow in mtx:
        trow = table.add_row()
        for cell, data in zip(trow.cells, drow):
            cell.text = data
        trow.height_rule = WD_ROW_HEIGHT_RULE.AUTO

def readFragmentSize(fragmentSize):
    with open(fragmentSize, 'r') as f:
        reader = csv.reader(f, delimiter = '\t')
        header = next(reader)
        data = []
        for row in reader:
            data.append(row)
        return(data)

def addFragmentSize(table, fragmentSize):
    mtx = readFragmentSize(fragmentSize)
    # mtx_sorted = sorted(mtx, key = lambda d: d[1])
    # for drow in mtx_sorted:
    for drow in mtx:
        trow = table.add_row()
        for cell, data in zip(trow.cells, drow):
            cell.text = data

def readYaml(yml):
    """
    description: yamlを読み込んで、辞書を返す。
    """
    with open(yml, 'r') as f:
        info = yaml.load(f, Loader = yaml.SafeLoader)
    return info

def makeAllInfo(cinfo, sinfo):
    """
    description: 全てのサンプル情報を結合した'all_informations.yml'を作成する
    """
    all_info = readYaml(cinfo)
    all_info['SOFTWARE_VERSIONS'] = readYaml(sinfo)
    return all_info

def addInfoTable(table, json):
    """
    description: Library作製キット及びrRNA除去キットの情報を挿入する。

    """
    df = pd.DataFrame()
    df['Step'] = ['rRNA removal', 'Library preparation']
    df['Kit'] = [json['rRNA_removal_kit'], json['library_preparation_kit']]
#    df =  df.set_index('Step')
    for i in range(df.shape[0]):
        trow = table.add_row()
        for cell, data in zip(trow.cells, df.loc[i]):
            cell.text = str(data)

    table.height_rule = WD_ROW_HEIGHT_RULE.AUTO

def main():
    """
    description: main関数
    """

    """インプットファイルの解析"""
    customer_info = "${customer_info}"
    software_versions = "${software_versions}"
    template = "${docx_template}"
    workflowpic = "${pictures[0]}"
    contentspic = "${pictures[1]}"
    outdir = '.'

    """all_informations.ymlの作成"""
    all_info = makeAllInfo(customer_info, software_versions)
    with open("all_informations.yml", "w") as f:
        yaml.dump(all_info, f, default_flow_style=False)

    customer = all_info['CUSTOMER_INFORMATION']
    experiments = all_info['EXPERIMENTS_INFORMATION']
    organism = all_info['ORGANISM_INFORMATION']
    samples = all_info['SAMPLE_INFORMATION']
    tools = all_info['SOFTWARE_VERSIONS']

    """docxファイルの作成"""
    outfile = "{}/{}・{}_{}_report_{}.docx".format(
        outdir,
        customer["customer_inst"].split(" ")[0].replace(" ", "_"),
        customer["customer_name"].replace(" ", "_"),
        experiments['analysis'],
        dtnow.strftime("%Y%m%d")
    )

    doc = Document(template)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'

    workflow = doc.add_picture(workflowpic, width=Cm(15), height=Cm(20))
    contents = doc.add_picture(contentspic, width=Cm(15), height=Cm(20))
    #heatmap =  doc.add_picture('heatmap.png', width=Cm(15), height=Cm(10))

    #fastq = readJsonTable(fastqd, select=['actual_read_num', 'min_len' ,'avg_len', 'max_len'], csep=True)
    #mapping = readJsonTable(samples,  select=['mapping_input_reads', 'unmapped_reads' ,'rrna_reads', 'total_mapped_reads', 'unique_mapped_reads'])

    modDocument(doc, analysis)
    modPictutre(doc)

    #if 'STAR_RSEM' in os.path.basename(args.template):
    #    addJsonTable(doc.tables[0], fastq)
    #    #addJsonTable(doc.tables[1], mapping)
    #    addMappingTable(doc.tables[1], star_mapping)
    #    addMappingTable(doc.tables[2], rsem_mapping)
    #    addInfoTable(doc.tables[3], analysis)
    #else:
    #    addJsonTable(doc.tables[0], fastq)
    #    addJsonTable(doc.tables[1], mapping)
    #    addMappingTable(doc.tables[1], star_mapping)
    #    addInfoTable(doc.tables[1], analysis)


    doc.save(outfile)

    # write python and libraries version to yaml.
    versions_this_module = {}
    versions_this_module["${task.process}"] = {
        "python": platform.python_version(),
        "pandas": pd.__version__,
        "yaml": yaml.__version__,
        "docx": docx.__version__
    }

    with open("versions.yml", "w") as f:
        yaml.dump(versions_this_module, f, default_flow_style=False)

if __name__ == '__main__':
    main()
