#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { PARSEXLSX_ORGANISM } from '../../../../../modules/nf-core/parsexlsx/organism/main.nf'

workflow test_parsexlsx_organism {

    input = [file(params.test_data['generic']['xlsx']['test_xlsx'], checkIfExists: true)]

    PARSEXLSX_ORGANISM ( input )
}
