#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { PARSEXLSX_CONCS } from '../../../../../modules/nf-core/parsexlsx/concs/main.nf'

workflow test_parsexlsx_concs {

    input = [file(params.test_data['generic']['xlsx']['test_xlsx'], checkIfExists: true)]

    PARSEXLSX_CONCS ( input )
}
