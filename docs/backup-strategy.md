# Backup Strategy for External File Modifications

## Naming Convention

When modifying files outside the git repository, always create a backup first:

```
{filename}.{YYYYMMDD}-{counter}
```

Where:
- `YYYYMMDD` = Last modification date of the original file
- `counter` = 3-digit incremental counter (001, 002, etc.)

## Rationale

1. **Historical Context**: Using last modification date preserves when the file was last changed
2. **Multiple Backups**: Counter allows multiple backups on the same day
3. **Sortable**: Format ensures backups sort chronologically
4. **Traceable**: Can track evolution of changes over time

## Implementation

### Get last modification date:
```bash
# Linux/Unix
stat -c %y /path/to/file | cut -d' ' -f1 | tr -d '-'

# Or using ls
ls -l --time-style='+%Y%m%d' /path/to/file | awk '{print $6}'
```

### Check for existing backups:
```bash
# Count existing backups
ls -1 /path/to/file.[0-9]*-[0-9]* 2>/dev/null | wc -l

# Find next counter
COUNTER=$(ls -1 /path/to/file.$(date +%Y%m%d)-* 2>/dev/null | wc -l)
COUNTER=$(printf "%03d" $((COUNTER + 1)))
```

### Create backup:
```bash
# Example for Makefile
ORIG_FILE="/local/incoming/covid/config/Makefile"
MOD_DATE=$(stat -c %y "$ORIG_FILE" | cut -d' ' -f1 | tr -d '-')
COUNTER="001"  # or increment if backups exist

cp "$ORIG_FILE" "${ORIG_FILE}.${MOD_DATE}-${COUNTER}"
```

## Example

Original file:
```
/local/incoming/covid/config/Makefile
```

After modifications on different dates:
```
/local/incoming/covid/config/Makefile           # Current version
/local/incoming/covid/config/Makefile.20250505-001  # First backup from May 5 version
/local/incoming/covid/config/Makefile.20250505-002  # Second backup from May 5 version
/local/incoming/covid/config/Makefile.20250909-001  # Backup from Sep 9 version
```

## Recovery

To restore from backup:
```bash
# View available backups
ls -lt /path/to/file.*

# Restore specific backup
cp /path/to/file.20250909-001 /path/to/file
```

## Best Practices

1. **Always backup before modifying** files outside version control
2. **Document the change** in the backup file or a log
3. **Clean old backups** periodically (keep last 3-5)
4. **Never modify backups** - they are historical records
5. **Use version control** when possible instead of backups

## Automated Backup Function

Add to your shell profile:
```bash
backup_before_edit() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "Error: File not found: $file"
        return 1
    fi
    
    local mod_date=$(stat -c %y "$file" | cut -d' ' -f1 | tr -d '-')
    local counter=1
    local backup_file
    
    while true; do
        backup_file="${file}.${mod_date}-$(printf "%03d" $counter)"
        [ ! -f "$backup_file" ] && break
        ((counter++))
    done
    
    cp -p "$file" "$backup_file"
    echo "Backup created: $backup_file"
}

# Usage
backup_before_edit /local/incoming/covid/config/Makefile
```

This strategy ensures we never lose important configurations while maintaining a clean, traceable history of changes.