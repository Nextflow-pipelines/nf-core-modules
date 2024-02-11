#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { PARSE_XLSX } from '../../../../subworkflows/nf-core/parse_xlsx/main.nf'

workflow test_parse_xlsx {

    input = [file(params.test_data['generic']['xlsx']['test_xlsx'], checkIfExists: true)]

    PARSE_XLSX ( input )
}
