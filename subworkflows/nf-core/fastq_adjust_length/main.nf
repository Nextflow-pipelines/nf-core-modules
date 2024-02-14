// TODO nf-core: If in doubt look at other nf-core/subworkflows to see how we are doing things! :)
//               https://github.com/nf-core/modules/tree/master/subworkflows
//               You can also ask for help via your pull request or on the #subworkflows channel on the nf-core Slack workspace:
//               https://nf-co.re/join
// TODO nf-core: A subworkflow SHOULD import at least two modules

include { SEQKIT_SUBSEQ                         } from '../../../modules/nf-core/seqkit/subseq/main.nf'
include { SEQKIT_STATS as SEQKIT_STATS_RAW      } from '../../../modules/nf-core/seqkit/stats/main.nf'
include { SEQKIT_STATS as SEQKIT_STATS_ADJUSTED } from '../../../modules/nf-core/seqkit/stats/main.nf'

workflow FASTQ_ADJUST_LENGTH {

    take:
    // TODO nf-core: edit input (take) channels
    ch_reads // channel: [ val(meta), [ fastq ] ]
    ch_aparams

    main:

    ch_versions = Channel.empty()

    // TODO nf-core: substitute modules here for the modules of your subworkflow

    //ch_reads.

    SEQKIT_STATS_RAW ( ch_reads )
    ch_versions = ch_versions.mix(SEQKIT_STATS_RAW.out.versions.first())

    SEQKIT_STATS_RAW.out.stats
    .map { meta, stats ->
        Channel.fromPath(stats)
        .splitCsv(header: true, sep: "\t")
        .map { row ->
            meta = meta + ['num_seqs_raw': row.num_seqs, 'num_seqs_raw': row.min_len, 'min_len_raw': row.min_len, 'max_len_raw': row.max_len ]
            return [ meta.id, [meta, stats]]
        }
    }
    .set { ch_stats_raw }

    ch_reads
    .map { meta, reads ->
        return [meta.id, [meta, reads]]
    }
    .join(ch_stats_raw, by:0)
    .map { id, ch_items ->
        (reads, stats) = ch_items
        meta = stats[0]
        return [meta, reads[1]]
    }
    .combine(ch_aparams)
    .map { meta, reads, aparams ->
        meta.read1_astart  = aparams[0]
        meta.read1_alength = aparams[1]
        meta.read2_astart  = aparams[2]
        meta.read2_alength = aparams[3]
        return [meta, reads]
    }
    .set { input_fastq }

    SEQKIT_SUBSEQ ( input_fastq )
    ch_versions = ch_versions.mix(SEQKIT_SUBSEQ.out.versions.first())

    SEQKIT_SUBSEQ.out.adjusted_resds
    .set { ch_reads_adjuted }

    SEQKIT_STATS_ADJUSTED ( ch_reads_adjuted )
    ch_versions = ch_versions.mix(SEQKIT_STATS_ADJUSTED.out.versions.first())

    SEQKIT_STATS_ADJUSTED.out.stats
    .map { meta, stats ->
        Channel.fromPath(stats)
        .splitCsv(header: true, sep: "\t")
        .map { row ->
            meta = meta + ['num_seqs_adjusted': row.num_seqs, 'num_seqs_adjusted': row.min_len, 'min_len_adjusted': row.min_len, 'max_len_adjusted': row.max_len ]
            return [ meta.id, [meta, stats]]
        }
    }
    .set { ch_stats_adjusted }

    ch_reads_adjuted
    .map { meta, reads ->
        return [meta.id, [meta, reads]]
    }
    .join(ch_stats_adjusted, by:0)
    .map { id, ch_items ->
        (reads, stats) = ch_items
        meta = stats[0]
        return[meta, reads[1]]
    }
    .set { output_fastq }

    emit:
    // TODO nf-core: edit emitted channels
    fastq    = output_fastq                    // channel: [ val(meta), [ reads ] ]

    versions = ch_versions                     // channel: [ versions.yml ]
}
