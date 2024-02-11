#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { PARSEXLSX_CUSTOMER } from '../../../../../modules/nf-core/parsexlsx/customer/main.nf'

workflow test_parsexlsx_customer {

    input = [file(params.test_data['generic']['xlsx']['test_xlsx'], checkIfExists: true)]

    PARSEXLSX_CUSTOMER ( input )
}
