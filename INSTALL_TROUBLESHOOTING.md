# TOPCAT Installation Troubleshooting Guide


## Installation Validation

### Step 1: Validation Script

Run the validation script to test all dependencies are intalled:

```bash
conda activate topcat
python validate_installation.py --config <your_config_file>
```

If you omit the config file argument it will default to `./config.ini`.


### Step 2: Dry-Run Test

Test your configuration without running the full analysis:

```bash
python code/driver.py --config <config_file> --dry-run
```

If you omit the config file argument it will defaul to `./config.ini`.


This shows what would be done without actually executing.

### Expected Output Files

After successful run, you should see (showing files for 10-topic run):

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

### Java Version Compatibility

**Problem**: MALLET fails to run with newer Java versions

**Tested working**: Java 1.8.0_73

**Solution**: If you have Java issues, consider installing Java 8 specifically for MALLET


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
- Text column number incorrect (remember: 1-indexed in config, e.g., first column = 1)
- Empty lines in original CSV

### Memory Issues with Large Datasets

**Problem**: Java runs out of memory during MALLET processing

**Solution**: Increase Java heap size in MALLET calls (this is handled automatically by the driver for typical datasets)


- **Normal completion**: MALLET exits with "Total time: X seconds"
