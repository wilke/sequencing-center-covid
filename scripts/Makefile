BAMS := $(wildcard bam/*.bam)
VARIANTS :=$(patsubst bam/%.sorted.bam,variants/%.variants.tsv,$(BAMS))

call: variants/%.variants.tsv

strain: $(VARIANTS)
	echo $@
	echo $<

depth/%.depth: bam/*.sorted.bam
	singularity run docker://wilke/freyja:latest ls $@

bam/%.sorted.bam: 
	echo BAM $@

variants/%.variants.tsv: bam/%.sorted.bam
	echo Variants $*
	$(eval sample:=$(shell basename $@ .variants.tsv))
	singularity run -B `pwd` /local/incoming/covid/config/freyja_latest.sif freyja variants bam/${sample}.sorted.bam --variants variants/${sample}.variants --depths depth/${sample}.depth --ref MN908947.3.trimmed.fa        
	singularity run -B `pwd` /local/incoming/covid/config/freyja_latest.sif freyja demix variants/${sample}.variants.tsv depth/${sample}.depth --output output/${sample}.out
