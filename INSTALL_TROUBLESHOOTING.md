# TOPCAT Installation Troubleshooting Guide

This guide covers potential issues during TOPCAT installation.

## Environment or Resource Issues

### spaCy Language Model Missing

**Problem**: `preprocessing_en.py` fails with "Can't find model '`en_core_web_sm`'"

**Solution**: After creating the `topcat` environment:

```bash
conda activate topcat
python -m spacy download en_core_web_sm
```

**Note**: The language model is NOT included in the conda environment - it must be downloaded separately.

## Build Issues

### csvfix Build Failures

**Problem**: `make mac` fails during csvfix compilation

**Requirements**: System must have GCC compiler tools installed

**Solutions**:

- Install Xcode command line tools: `xcode-select --install`
- On some systems, you may need to install full Xcode from App Store
- Build warnings are normal - only worry if build completely fails

### Java Version Compatibility

**Problem**: MALLET fails to run with newer Java versions

**Tested working**: Java 1.8.0_73

**Solution**: If you have Java issues, consider installing Java 8 specifically for MALLET

## PATH and File Location Issues

### csvfix Binary Not Found

**Problem**: `csvfix: command not found` even after building

**Cause**: The csvfix binary location differs from original expectations

**Solution**: The driver automatically adds csvfix to PATH, but verify location:

```bash
# Expected location after build:
your_topcat_directory/csvfix/csvfix/bin/csvfix
```

### Directory Already Exists Errors

**Problem**: "Directory already exists" errors during repeat runs

**Solution**: Use debug mode for automatic cleanup, or clean up manually:

**Automatic (recommended)**:
Set `debug = true` in your config.ini - the driver will automatically clean up existing directories

**Manual**:
```bash
rm -rf your_analysis_directory/data/modeling/model_*
```

## Data Processing Issues

### CSV Encoding Problems

**Problem**: Strange characters or encoding errors when processing CSV files

**Solution**: Convert CSV to UTF-8 if needed:

```bash
iconv -f windows-1252 -t utf-8 -c input.csv > output.csv
```

### Empty Documents After Preprocessing  

**Problem**: All documents disappear after NLP preprocessing

**Causes**:

- All text was stopwords (removed by preprocessing)
- Text column number incorrect (remember: 0-indexed in code, 1-indexed in config)
- Empty lines in original CSV

### Memory Issues with Large Datasets

**Problem**: Java runs out of memory during MALLET processing

**Solution**: Increase Java heap size in MALLET calls (this is handled automatically by the driver for typical datasets)

## Timing and Performance

### Expected Processing

- **1000 iterations**: 10-30 minutes depending on dataset size and computer speed  

- **Progress indicators**: MALLET shows `<10> LL/token: -8.18903` every 10 iterations. Should become less negative over iterations

- **Model files**: Expect ~20MB total for typical datasets (2000 documents, 30 topics)



- **Normal completion**: MALLET exits with "Total time: X seconds"

## Installation Validation

### Step 1: Validation Script

Run the validation script to test all dependencies:

```bash
conda activate topcat
python validate_installation.py
```

### Step 2: Dry-Run Test

Test your configuration without running the full analysis:

```bash
python code/driver.py --dry-run
```

This shows what would be done without actually executing, including timing estimates.

### Expected Output Files

After successful run, you should see:

```
your_analysis_directory/
├── data/
│   ├── modeling/
│   │   ├── comments_raw.txt          # Extracted documents
│   │   └── model_k10/                # Topic model files
│   │       ├── preprocessed.txt      # spaCy processed text  
│   │       └── mallet_output/        # MALLET results
└── out/                              # Human curation materials
    ├── 10_categories.xlsx
    ├── 10_clouds.pdf
    └── 10_alldocs.xlsx
```

### Success Criteria

1. **CSV extraction**: Raw text file created with correct number of lines

2. **NLP preprocessing**: Processed text shows tokenization and phrase detection

3. **MALLET training**: Model files created without errors

4. **Topic quality**: Meaningful topic clusters visible in output files

## Common Error Messages

### "Can't find model '`en_core_web_sm`'"

**Fix**: Download spaCy language model (see Environment Issues above)

### "java: command not found" 

**Fix**: Install Java 8+ or ensure Java is in system PATH

### "csvfix: command not found"

**Fix**: Verify csvfix build completed successfully and PATH is set correctly

### "Directory already exists"

**Fix**: Remove existing model directories or choose different output directory

### "No such file or directory: config.ini"

**Fix**: Ensure you copied `templates/config_template.ini` to `config.ini` and edited paths

## Getting Help

If you encounter issues not covered here:

1. **Check file paths**: Verify all paths in `config.ini` are correct for your system

2. **Test components individually**: Try running preprocessing, MALLET, and curation steps separately

3. **Check dependencies**: Ensure all conda environments created successfully

4. **Verify example works**: Test with provided FDA comment dataset before using your own data

## System Requirements Summary

- **Operating System**: macOS (tested), Linux (should work), Windows (not tested)
- **Python**: 3.9+ (handled by conda environments)
- **Java**: 1.8+ for MALLET
- **Compiler**: GCC/Xcode command line tools for csvfix
- **Memory**: 4GB+ recommended for typical datasets
- **Disk Space**: ~1GB for dependencies + space for your data and models
