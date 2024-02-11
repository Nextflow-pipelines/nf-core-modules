// TODO nf-core: If in doubt look at other nf-core/subworkflows to see how we are doing things! :)
//               https://github.com/nf-core/modules/tree/master/subworkflows
//               You can also ask for help via your pull request or on the #subworkflows channel on the nf-core Slack workspace:
//               https://nf-co.re/join
// TODO nf-core: A subworkflow SHOULD import at least two modules

include { PARSEXLSX_SAMPLES      } from '../../../modules/local/parsexlsx/samples/main.nf'
include { PARSEXLSX_CONCS        } from '../../../modules/local/parsexlsx/concs/main.nf'
include { PARSEXLSX_CUSTOMER     } from '../../../modules/local/parsexlsx/customer/main.nf'
include { PARSEXLSX_EXPERIMENTS  } from '../../../modules/local/parsexlsx/experiments/main.nf'
include { PARSEXLSX_ORGANISM     } from '../../../modules/local/parsexlsx/organism/main.nf'

workflow PARSE_XLSX {
    take:
    ch_xlsx
    
    main:
    
    ch_informations = Channel.empty()
    ch_versions = Channel.empty()
    
    PARSEXLSX_SAMPLES ( ch_xlsx )
    PARSEXLSX_CONCS ( ch_xlsx )
    PARSEXLSX_CUSTOMER ( ch_xlsx )
    PARSEXLSX_EXPERIMENTS ( ch_xlsx )
    PARSEXLSX_ORGANISM ( ch_xlsx )
    
    ch_informations = ch_informations.mix(
                        PARSEXLSX_CUSTOMER.out.yaml,
                        PARSEXLSX_EXPERIMENTS.out.yaml,
                        PARSEXLSX_ORGANISM.out.yaml,
                        PARSEXLSX_SAMPLES.out.yaml,
                        PARSEXLSX_CONCS.out.yaml
                    )
    
    ch_versions = ch_versions.mix(PARSEXLSX_SAMPLES.out.versions.first())
    
    emit:
    
    samples = PARSEXLSX_SAMPLES.out.csv
    concs = PARSEXLSX_CONCS.out.csv
    informations = ch_informations
    
    versions = ch_versions
}