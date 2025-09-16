# GitHub Issue: Reorganize /local/incoming/covid/config folder structure

## Issue Title
Reorganize config folder to separate configuration, containers, and data

## Labels
- enhancement
- infrastructure
- technical-debt
- refactoring

## Description

The `/local/incoming/covid/config/` directory currently contains a mix of:
- Configuration files (Makefile, .yml, .json)
- Singularity containers (23GB+ .sif files)
- Reference data (usher_barcodes, lineages)
- SSH keys and credentials

This creates several problems:
1. Cannot version control large binary files (containers)
2. Security risk having credentials in same directory
3. Difficult to track configuration changes
4. Backup/sync issues with mixed content types

## Current State Analysis

```
/local/incoming/covid/config/
├── Singularity Containers (28GB+)
│   ├── bvbrc-build-191.sif (23GB)
│   ├── freyja_*.sif (multiple versions, ~500MB-1.2GB each)
│   └── freyja_latest.sif -> symlink
├── Configuration Files
│   ├── Makefile
│   ├── pathogen_config.yml
│   └── curated_lineages.json
├── Reference Data
│   ├── usher_barcodes.*.feather (100+ files)
│   ├── lineages.yml
│   └── MN908947.3.trimmed.fa
└── Credentials
    └── covid_rsa (SSH keys)
```

## Proposed Structure

```
/local/incoming/covid/
├── config/                    # Version controlled
│   ├── Makefile
│   ├── pathogen_config.yml
│   └── pipeline_config.json
├── containers/                # Not version controlled
│   ├── freyja/
│   │   ├── 1.5.3-07_14_2025-00-44-2025-07-14.sif
│   │   ├── 2.0.0-09_08_2025-00-34-2025-09-08.sif
│   │   └── latest -> 1.5.3-07_14_2025-00-44-2025-07-14.sif
│   └── assembly/
│       └── bvbrc-build-191.sif
├── reference_data/            # Partially version controlled
│   ├── genomes/
│   │   └── MN908947.3.trimmed.fa
│   └── databases/
│       ├── usher_barcodes.feather
│       └── lineages.yml
└── credentials/               # Never version controlled
    └── covid_rsa
```

## Implementation Plan

### Phase 1: Create new directory structure
```bash
mkdir -p /local/incoming/covid/{containers/{freyja,assembly},reference_data/{genomes,databases},credentials}
```

### Phase 2: Move files to appropriate locations
```bash
# Move containers
mv /local/incoming/covid/config/freyja_*.sif /local/incoming/covid/containers/freyja/
mv /local/incoming/covid/config/bvbrc-build-*.sif /local/incoming/covid/containers/assembly/

# Move reference data
mv /local/incoming/covid/config/usher_barcodes.* /local/incoming/covid/reference_data/databases/
mv /local/incoming/covid/config/MN908947.3.trimmed.fa /local/incoming/covid/reference_data/genomes/

# Move credentials
mv /local/incoming/covid/config/*_rsa* /local/incoming/covid/credentials/
chmod 600 /local/incoming/covid/credentials/*
```

### Phase 3: Update symlinks
```bash
# Update freyja_latest symlink
cd /local/incoming/covid/containers/freyja
ln -sf 1.5.3-07_14_2025-00-44-2025-07-14.sif latest

# Create backward compatibility symlinks in config/
cd /local/incoming/covid/config
ln -s ../containers/freyja/latest freyja_latest.sif
```

### Phase 4: Update scripts to use new paths
- Update Makefile paths
- Update process-covid-run paths
- Update assembly.sh paths

## Benefits

1. **Version Control**: Can track config changes without large binaries
2. **Security**: Credentials isolated with proper permissions
3. **Organization**: Clear separation of concerns
4. **Maintenance**: Easier to update/manage containers
5. **Backup**: Can backup config separately from data

## Backward Compatibility

Maintain symlinks in original locations during transition:
```bash
/local/incoming/covid/config/freyja_latest.sif -> ../containers/freyja/latest
/local/incoming/covid/config/Makefile -> tracked in git
```

## Acceptance Criteria

- [ ] New directory structure created
- [ ] All files moved to appropriate locations
- [ ] Symlinks maintain backward compatibility
- [ ] Scripts updated to use new paths
- [ ] Documentation updated
- [ ] No disruption to production pipeline
- [ ] Git tracking only appropriate files

## Related Issues
- #123 Freyja version parameterization
- Security audit of credential storage
- Container management strategy

## Notes

Large container files (>100MB) should NEVER be added to git. Use git-lfs or external storage with version tracking instead.