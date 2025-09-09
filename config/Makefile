BASE := /local/incoming/covid/
BAMS := $(wildcard bam/*.bam)
VARIANTS :=$(patsubst bam/%.sorted.bam,variants/%.variants.tsv,$(BAMS))

# Freyja version configuration - backward compatible
# Priority: make argument > environment variable > default (latest)
FREYJA_VERSION ?= latest

# Direct path construction - no mapping needed
SINGULARITY := /local/incoming/covid/config/freyja_$(FREYJA_VERSION).sif 
BARCODES := /local/incoming/covid/config/usher_barcodes.feather
LINEAGES := /local/incoming/covid/config/lineages.yml
CURATED_LINEAGES := /local/incoming/covid/config/curated_lineages.json
CURATED_LINEAGES_TARGET := /opt/conda/envs/freyja-env/lib/python3.10/site-packages/freyja/data/
CUTOFF := 0
BIND := --bind /local/incoming/covid/ --bind /nfs/seq-data/covid/
REFERENCE := /local/incoming/covid/config/MN908947.3.trimmed.fa 

# Version validation
.PHONY: validate-version
validate-version:
	@if [ ! -f "$(SINGULARITY)" ]; then \
		echo "ERROR: Freyja container not found: $(SINGULARITY)"; \
		echo "Available versions:"; \
		ls -1 /local/incoming/covid/config/freyja_*.sif 2>/dev/null | sed 's/.*freyja_/  - /' | sed 's/.sif//'; \
		exit 1; \
	fi
	@if [ "$(FREYJA_VERSION)" = "latest" ] && [ ! -L "$(SINGULARITY)" ]; then \
		echo "WARNING: freyja_latest.sif is not a symlink - may affect reproducibility"; \
	fi

call: variants/%.variants.tsv

.PHONY: update
update: validate-version
	$(eval d:=$(shell date +"%Y-%m-%d"))
	singularity run $(BIND) $(SINGULARITY) freyja update --outdir $(BASE)/config/
	cp $(BASE)/config/usher_barcodes.feather $(BASE)/config/usher_barcodes.${d}.feather
	chmod a+w $(BASE)/config/usher_barcodes.feather

strain: validate-version $(VARIANTS)
	echo $@
	echo $<

depth/%.depth: bam/*.sorted.bam
	singularity run docker://wilke/freyja:latest ls $@

bam/%.sorted.bam: 
	echo BAM $@

variants/%.variants.tsv: bam/%.sorted.bam validate-version
	@echo "Processing $* with Freyja $(FREYJA_VERSION)"
	$(eval sample:=$(shell basename $@ .variants.tsv))
	singularity run $(BIND) $(SINGULARITY)  freyja variants bam/${sample}.sorted.bam --variants variants/${sample}.variants --depths depth/${sample}.depth --ref $(REFERENCE)        
	echo $(shell if [ -f variants/${sample}.variants.tsv ] ; then echo "Found variants/${sample}.variants.tsv" ; else touch variants/${sample}.variants.missing ; echo Missing variants/${sample}.variants.tsv ; fi )
	singularity exec $(BIND) $(SINGULARITY) freyja demix --depthcutoff $(CUTOFF) --lineageyml $(LINEAGES) --meta $(CURATED_LINEAGES) --barcodes $(BARCODES) --output output/${sample}.out variants/${sample}.variants.tsv depth/${sample}.depth
	@echo "$(FREYJA_VERSION)" > output/${sample}.freyja_version
