#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml, platform, docx
import pandas as pd
from pathlib import Path
from datetime import datetime
from docx import Document
from docx.shared import Inches, Cm
from docx.enum.table import WD_ROW_HEIGHT, WD_ROW_HEIGHT_RULE

dtnow = datetime.now()

def testKeys(keys, text):
    def tester(key):
        return( ('{' + key + '}') in text )
    return(list(filter(tester, keys)))

def modDocument(doc, tags, mInfo):
    """
    description: docテンプレートの指定箇所に指定した値を代入する。
    arguments:
        doc : docxオブジェクト
        tags: 代入すべき箇所(report_contents.ymlの'DOCUMENTS'の項目を辞書化)
        mInfo: 代入する値(all_informations.ymlより取得)
    """
    #tags['DATE'] = dtnow.strftime("%Y-%m-%d")
    #tags['CUSTOMERNAME'] = mInfo["CUSTOMER_INFORMATION"]["customer_name"]
    #tags['CUSTOMERINSTITUTE'] = mInfo["CUSTOMER_INFORMATION"]["customer_inst"].split(" ")[0]
    #tags['ANALYSIS'] = mInfo["EXPERIMENTS_INFORMATION"]["analysis"]
    #tags['SEQUENCER'] = mInfo["EXPERIMENTS_INFORMATION"]["sequencer"]
    #tags['RRNA'] = mInfo["EXPERIMENTS_INFORMATION"]["rrna_removal"]
    #tags['LIBRARY'] = mInfo["EXPERIMENTS_INFORMATION"]["library_preparation_kit"]
    #tags['COMMONNAME'] = mInfo["ORGANISM_INFORMATION"]["organism_name"]
#   tags['SCIENTIFICNAME'] = mInfo["scientific_name"]
    #tags['GENOMEASSEMBLY'] = mInfo["ORGANISM_INFORMATION"]["reference_name"]
    #keys = tags.keys()
    for para in doc.paragraphs:
        hitKeys = testKeys(tags, para.text)
        if len(hitKeys) > 0:
            print("{}: {}".format(hitKeys, para.text))
            inline = para.runs
            # Loop added to work with runs (strings with same style)
            for i in range(len(inline)):
                textMod = inline[i].text.replace('{','').replace('}','')
                for hitKey in hitKeys:
                    textMod = textMod.replace(hitKey, tags[hitKey])
                print("({}) {} ===> {}".format(i, inline[i].text, textMod))
                inline[i].text = textMod

def modPictutre(doc, tags):
    #keys = tags.keys()
    for para in doc.paragraphs:
        hitKeys = testKeys(tags, para.text)
        if len(hitKeys) > 0:
            #print("{}: {}".format(hitKeys, para.text))
            inline = para.runs
            # Loop added to work with runs (strings with same style)
            for hitKey in hitKeys:
                #textMod1 = inline[0].text.replace('{','').replace('}','').replace(hitKey, '')
                #textMod2 = inline[1].text.replace('{','').replace('}','').replace(hitKey, tags[hitKey][3])
                #inline[0].text = textMod1
                #inline[1].text = textMod2
                #inline[0].add_picture(tags[hitKey][0], width=Cm(tags[hitKey][1]), height=Cm(tags[hitKey][2]))
                for i in range(len(inline)):
                    textMod = inline[i].text.replace('{','').replace('}','')
                    for hitKey in hitKeys:
                        textMod = textMod.replace(hitKey, tags[hitKey][0])
                    #print("({}) {} ===> {}".format(i, inline[i].text, textMod))
                    inline[i].text = textMod
                    inline[i].add_picture(tags[hitKey][0], width=Cm(tags[hitKey][1]), height=Cm(tags[hitKey][2]))

def readYaml(yml):
    """
    description: yamlを読み込んで、辞書を返す。
    """
    with open(yml, 'r') as f:
        info = yaml.load(f, Loader = yaml.SafeLoader)
    return info

def addTable(doc, tags, tdata):
    """
    description: tableを作成する。
    """
    col_title = tags['columns']
    print(col_title)
    table = doc.add_table(rows=1, cols=len(col_title))
    for i, cell in enumerate(table.rows[0].cells):
        cell.text = col_title[i]
    for drow in tdata:
        trow = table.add_row()
        for cell, data in zip(trow.cells, drow):
            cell.text = data
    table.height_rule = WD_ROW_HEIGHT_RULE.AUTO

def makeAllInfo(cinfo, sinfo):
    """
    description: 全てのサンプル情報を結合した'all_informations.yml'を作成する
    """
    all_info = readYaml(cinfo)
    all_info['SOFTWARE_VERSIONS'] = readYaml(sinfo)
    return all_info

def main():
    """
    description: main関数
    """

    dfs = {}

    """インプットファイルの解析"""
    customer_info = "${customer_info}"
    software_versions = "${software_versions}"
    template = "${docx_template}"
    contents_info = "${docx_contents}"
    outdir = '.'

    """contents_infoの作成"""
    contentsinfo = readYaml(contents_info)
    doctags = contentsinfo['DOCUMENTS']
    pictags = contentsinfo['PICTURES']
    tabletags = contentsinfo['TABLES']

    """all_informations.ymlの作成"""
    all_info = makeAllInfo(customer_info, software_versions)
    with open("all_informations.yml", "w") as f:
        yaml.dump(all_info, f, default_flow_style=False)

    customer = all_info['CUSTOMER_INFORMATION']
    experiments = all_info['EXPERIMENTS_INFORMATION']
    dfs['SAMPLES'] = pd.DataFrame(all_info['SAMPLE_INFORMATION']).T
    dfs['SOFTWARE'] = pd.DataFrame(all_info['SOFTWARE_VERSIONS']).T.reset_index().melt(id_vars='index').dropna().sort_values(by='index')
    dfs['KITS'] = pd.DataFrame(all_info['EXPERIMENTS_INFORMATION'], columns=['Step', 'Kit'])

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

    """docx内文章の変換"""
    modDocument(doc, doctags, all_info)
    """図表画像の挿入"""
    modPictutre(doc, pictags)
    """表の挿入"""
    for n, tabletag in enumerate(tabletags.keys()):
        print('{}: {}'.format(n, tabletag))
        addTable(doc, tabletags[tabletag], dfs[tabletag])

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
