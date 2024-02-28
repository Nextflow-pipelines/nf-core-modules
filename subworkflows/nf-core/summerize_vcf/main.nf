// TODO nf-core: If in doubt look at other nf-core/subworkflows to see how we are doing things! :)
//               https://github.com/nf-core/modules/tree/master/subworkflows
//               You can also ask for help via your pull request or on the #subworkflows channel on the nf-core Slack workspace:
//               https://nf-co.re/join
// TODO nf-core: A subworkflow SHOULD import at least two modules

include { BCFTOOLS_FILTER                               } from '../../../modules/nf-core/bcftools/filter/main.nf'
include { BCFTOOLS_NORM  as BCFTOOLS_NORM_BEFORE_MERGE  } from '../../../modules/nf-core/bcftools/norm/main.nf'
include { BCFTOOLS_NORM  as BCFTOOLS_NORM_AFTER_MERGE   } from '../../../modules/nf-core/bcftools/norm/main.nf'
include { BCFTOOLS_MERGE                                } from '../../../modules/nf-core/bcftools/merge/main.nf'
include { BCFTOOLS_QUERY                                } from '../../../modules/nf-core/bcftools/query/main.nf'
include { BCFTOOLS_INDEX as BCFTOOLS_INDEX_BEFORE_NORM  } from '../../../modules/nf-core/bcftools/index/main.nf'
include { BCFTOOLS_INDEX as BCFTOOLS_INDEX_BEFORE_MERGE } from '../../../modules/nf-core/bcftools/index/main.nf'
include { BCFTOOLS_INDEX as BCFTOOLS_INDEX_AFTER_MERGE  } from '../../../modules/nf-core/bcftools/index/main.nf'
include { BCFTOOLS_INDEX as BCFTOOLS_INDEX_AFTER_NORM   } from '../../../modules/nf-core/bcftools/index/main.nf'
include { BCFTOOLS_SORT                                 } from '../../../modules/nf-core/bcftools/sort/main.nf'

workflow SUMMERIZE_VCF {

    take:
    // TODO nf-core: edit input (take) channels
    ch_vcf   // channel: [ val(meta), vcfs, tbis ]
    ch_fasta
    ch_fai
    ch_bed

    main:

    ch_versions = Channel.empty()

    // TODO nf-core: substitute modules here for the modules of your subworkflow

    ch_vcf.map { meta, vcf, tbi -> return[meta, [vcf]]}
    .set { ch_start_vcf }

    BCFTOOLS_FILTER ( ch_start_vcf )

    BCFTOOLS_INDEX_BEFORE_NORM( BCFTOOLS_FILTER.out.vcf )

    BCFTOOLS_FILTER.out.vcf
    .join(BCFTOOLS_INDEX_BEFORE_NORM.out.tbi)
    .set {ch_norm_in}

    BCFTOOLS_NORM_BEFORE_MERGE ( ch_norm_in, ch_fasta )
    ch_versions = ch_versions.mix(BCFTOOLS_NORM_BEFORE_MERGE.out.versions.first())

    BCFTOOLS_NORM_BEFORE_MERGE.out.vcf
    .map { meta, vcf -> return [ meta, [vcf] ] }
    .set { ch_vcf_index_in }

    BCFTOOLS_INDEX_BEFORE_MERGE ( BCFTOOLS_NORM_BEFORE_MERGE.out.vcf )
    ch_versions = ch_versions.mix(BCFTOOLS_INDEX_BEFORE_MERGE.out.versions.first())

    BCFTOOLS_INDEX_BEFORE_MERGE.out.tbi
    .collect { it[1] }
    .map { it -> return [ ["id": "germline_merged"], it ] }
    .set { ch_vcf_tbis }

    BCFTOOLS_NORM_BEFORE_MERGE.out.vcf
    .collect { it[1] }
    .map { it -> return [ ["id": "germline_merged"], it ] }
    .join(ch_vcf_tbis)
    .set { ch_vcf_merge_in }

    BCFTOOLS_MERGE ( ch_vcf_merge_in, ch_fasta, ch_fai, ch_bed )
    ch_versions = ch_versions.mix(BCFTOOLS_MERGE.out.versions.first())

    BCFTOOLS_INDEX_AFTER_MERGE ( BCFTOOLS_MERGE.out.merged_variants )
    ch_versions = ch_versions.mix(BCFTOOLS_INDEX_AFTER_MERGE.out.versions.first())

    BCFTOOLS_MERGE.out.merged_variants
    .join(BCFTOOLS_INDEX_AFTER_MERGE.out.tbi)
    .set { ch_bcftools_norm_in }

    BCFTOOLS_NORM_AFTER_MERGE ( ch_bcftools_norm_in, ch_fasta )
    ch_versions = ch_versions.mix(BCFTOOLS_NORM_AFTER_MERGE.out.versions.first())

    BCFTOOLS_SORT ( BCFTOOLS_NORM_AFTER_MERGE.out.vcf )
    ch_versions = ch_versions.mix(BCFTOOLS_SORT.out.versions.first())

    BCFTOOLS_INDEX_AFTER_NORM ( BCFTOOLS_SORT.out.vcf )
    ch_versions = ch_versions.mix(BCFTOOLS_INDEX_AFTER_NORM.out.versions.first())

    BCFTOOLS_SORT.out.vcf
    .join(BCFTOOLS_INDEX_AFTER_NORM.out.tbi)
    .set { ch_bcftools_query_in }

    BCFTOOLS_QUERY ( ch_bcftools_query_in, [], [], [] )
    ch_versions = ch_versions.mix(BCFTOOLS_QUERY.out.versions.first())

    emit:
    // TODO nf-core: edit emitted channel
    text     = BCFTOOLS_QUERY.out.output           // channel: [ val(meta), [ bam ] ]
    vcf      = BCFTOOLS_NORM_AFTER_MERGE.out.vcf   // channel: [ val(meta), [ bai ] ]
    tbi      = BCFTOOLS_INDEX_AFTER_NORM.out.tbi   // channel: [ val(meta), [ csi ] ]

    versions = ch_versions                         // channel: [ versions.yml ]
}
