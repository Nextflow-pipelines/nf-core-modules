#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { PARSEXLSX_EXPERIMENTS } from '../../../../../modules/nf-core/parsexlsx/experiments/main.nf'

workflow test_parsexlsx_experiments {

    input = [file(params.test_data['generic']['xlsx']['test_xlsx'], checkIfExists: true]

    PARSEXLSX_EXPERIMENTS ( input )
}
