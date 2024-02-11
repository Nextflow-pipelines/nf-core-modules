#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { PARSEXLSX_SAMPLES } from '../../../../../modules/nf-core/parsexlsx/samples/main.nf'

workflow test_parsexlsx_samples {

    input = [file(params.test_data['generic']['xlsx']['test_xlsx'], checkIfExists: true)]

    PARSEXLSX_SAMPLES ( input )
}
