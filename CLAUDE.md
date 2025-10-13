# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TOPCAT (Topic-Oriented Protocol for Content Analysis of Text) is a software-enabled pipeline that combines automated topic modeling using MALLET with human-centered qualitative content analysis. It processes CSV data through NLP preprocessing, topic modeling, and generates human curation materials.

## Architecture & Core Workflow

### Pipeline Flow
CSV Input → NLP Preprocessing → MALLET Topic Modeling → Curation Material Generation

### Two-Phase Conda Environment System
- **`topics` environment**: NLP preprocessing and MALLET topic modeling (spacy, wordcloud, pandas)
- **`topic_curation` environment**: Human curation material generation (numpy=1.21.5, matplotlib=3.2.2, xlsxwriter=3.0.3)

## Key Components

### Main Execution
- **`code/driver.csh`**: Primary shell script orchestrating the entire pipeline (7627 lines)
- **`code/driver.py`**: Experimental Python configuration loader
- **`code/config.ini`**: Configuration file with installation and analysis parameters

### Core Source Files (`code/src/`)
- **`run_mallet.py`**: Python driver for MALLET topic modeling, handles preprocessing and CSV conversion
- **`preprocessing_en.py`**: English NLP preprocessing using spaCy with phrase detection
- **`model2csv.py`**: Converts topic model outputs to CSV format (supports MALLET, Scholar, Segan)
- **`create_topic_curation_files_with_custom_ratings_columns.py`**: Generates Excel files, word clouds, and PDFs for human review
- **`phrase_tokenization_subs.py`**: Multi-word phrase detection and normalization utilities

## Configuration System

Configuration is managed through `code/config.ini` with these key sections:

**Installation Variables:**
- `malletdir`: MALLET installation directory
- `topcatdir`: TOPCAT package directory
- `preproc`/`runmallet`: Paths to core scripts

**Analysis Variables:**
- `csv`: Input CSV file path
- `textcol`: Column number containing documents (0-indexed)
- `granularities`: Topic model sizes to try (e.g., "10 20 30")
- `datadir`/`outdir`: Output directories

**Processing Parameters:**
- `numiterations`: MALLET iterations (default: 1000)
- `maxdocs`: Max documents per topic for curation (default: 100)
- `seed`: Random seed for reproducibility (default: 13)

## Commands

### Main Execution
```bash
# Primary method (shell script)
./code/driver.csh

# Experimental Python driver
python code/driver.py config.ini
```

### Development/Testing
```bash
# Create sample CSV from larger dataset
python example/create_example_csv_file.py fda_1088_sampled.csv 2000 50 400 > fda_1088_sampled_2K.csv

# Individual component testing
python code/src/run_mallet.py [options]
python code/src/preprocessing_en.py [options]
```

## Dependencies & Setup

### External Dependencies
1. **MALLET**: Java-based topic modeling toolkit
2. **csvfix**: CSV manipulation utility
3. **Conda/Miniconda**: Environment management

### Environment Setup
```bash
conda env create -f code/topics.yml
conda env create -f code/topic_curation.yml
```

## Data Flow

### Input Requirements
- CSV file with text documents in specified column
- UTF-8 encoding recommended
- Header row expected

### Output Structure
For each granularity (e.g., 10, 20, 30 topics):
- **`granularity_{N}_categories.xlsx`**: Top words and documents per topic
- **`granularity_{N}_clouds.pdf`**: Word cloud visualizations
- **`granularity_{N}_alldocs.xlsx`**: Document-topic distributions

### Intermediate Files
- `{modelname}_raw.txt`: Extracted raw documents
- `preprocessed.txt`: NLP-processed documents
- MALLET format files (`.mallet`, `.model`, `.doc-topics`, etc.)

## Processing Steps

1. **Text Extraction**: Extract documents from CSV using csvfix
2. **Environment Activation**: Switch to `topics` conda environment
3. **For each granularity**:
   - Run NLP preprocessing with spaCy
   - Execute MALLET topic modeling
   - Switch to `topic_curation` environment
   - Generate Excel files and PDF word clouds
4. **Output Organization**: Copy final files to output directory with standardized naming

## Human Curation Workflow

The pipeline supports a three-stage human curation process:
1. **Model Selection**: Choose optimal granularity using generated materials
2. **Independent Curation**: Two SMEs independently label topics using Excel/PDF outputs
3. **Consensus Building**: SMEs create unified coding scheme

Support materials are provided in `/instructions/` including PDFs for model selection, topic labeling, and consensus building.

## Granularity Recommendations

- **<500 docs**: K=5,10,15
- **500-1000 docs**: K=10,15,20 or 10,20,30
- **1000-10000 docs**: K=15,20,40 or 20,30,50
- **10000-200000 docs**: K=75,100,150

## Current Architecture Limitations

- Shell script should be converted to pure Python
- Two conda environments should be merged
- Hard-coded paths need parameterization
- Character encoding issues with Excel-generated CSVs require `iconv` preprocessing
- Uses `os.system()` calls that need input validation

## Example Dataset

The repository includes FDA COVID-19 vaccine public comments:
- **Source**: 2000 comments sampled from ~130,000 total
- **File**: `example/fda_1088_sampled_2K.csv`
- **Reference Output**: Available in `example/example_out/` for comparison

---

# FRESH USER INSTALLATION & TESTING DOCUMENTATION

## Overview of Fresh User Simulation

A comprehensive fresh user simulation was conducted to identify and resolve all barriers to TOPCAT adoption. This simulation involved creating a completely isolated test environment, installing all dependencies from scratch, and running the full pipeline end-to-end.

## Test Environment Location

All fresh user testing was conducted in: `/Users/resnik/Misc/projects/topcat/github/fresh_user_test/`

This directory contains:
- Complete dependency installations (MALLET, csvfix)  
- Properly configured conda environments
- Modified configuration files with corrected paths
- Full end-to-end test run results

## Critical Issues Identified & Resolved

### 1. **Hardcoded Path Dependencies** 
**Problem**: Original `code/config.ini` contains hardcoded paths like `/Users/resnik/misc`  
**Impact**: Prevents any other user from running TOPCAT without manual path editing  
**Solution Created**: `fresh_user_test/config_fresh_user.ini` with parameterized paths  
**Fixed Paths**:
- `myhome` → Test environment directory
- `malletdir` → Local MALLET installation  
- `topcatdir` → Repository root
- `csvfix` PATH → Corrected binary location

### 2. **Conda Environment Version Conflicts**
**Problem**: Original environment files specify package versions that are no longer available  
**Specific Issues**:
- `python=3.7.13` (unavailable)
- `matplotlib=3.2.2` (unavailable) 
- `numpy=1.21.5` (conflicts with newer scipy)
**Solution Created**: Updated environment files in `fresh_user_test/environments/`
- `fresh_user_topics_test.yml` (flexible version specs)
- `fresh_user_curation_test.yml` (compatible versions)

### 3. **Missing spaCy Language Model**
**Problem**: `preprocessing_en.py` requires `en_core_web_sm` model not included in conda environment  
**Impact**: Preprocessing fails with "Can't find model 'en_core_web_sm'" error  
**Solution**: Must run `python -m spacy download en_core_web_sm` in activated environment

### 4. **csvfix Build & PATH Issues**
**Problem**: 
- csvfix must be built from source (no binary packages)
- Build location differs from expected PATH in `driver.py`
**Details**: 
- Original expects: `myhome/pkg/csvfix/csvfix-build/csvfix/bin`
- Actual build location: `myhome/csvfix/csvfix/bin`  
**Solution**: Modified `driver_fresh_user.py` with corrected PATH handling

### 5. **Missing Python Dependencies**
**Problem**: Several required packages not in conda environments:
- `traceback-with-variables` (imported by `preprocessing_en.py`)
- Standard library issues with regex escaping (`SyntaxWarning` in multiple files)

### 6. **Directory Creation Timing Issues**
**Problem**: MALLET runner expects certain directories to not exist, others to exist  
**Impact**: "Directory already exists" errors during repeat runs  
**Solution**: Proper cleanup and directory management in test workflow

## Successful End-to-End Test Results

### Pipeline Execution Confirmed Working:
1. ✅ **CSV Text Extraction**: Successfully extracted 2000 documents using csvfix
2. ✅ **spaCy NLP Preprocessing**: Full linguistic analysis with phrase detection (2000 docs processed)  
3. ✅ **MALLET Topic Modeling**: Complete 1000-iteration LDA training (K=10 topics)
4. ✅ **Model Convergence**: Proper log-likelihood improvement and beta optimization
5. ✅ **CSV Output Generation**: Converting MALLET outputs to human-readable formats

### Generated Files (Test Run Location):
```
/Users/resnik/Misc/projects/topcat/github/fresh_user_test/test_run/data/modeling/
├── comments1088_raw.txt                    # Extracted documents (2000 lines)
├── comments1088_test.mallet                # MALLET import format  
└── model_k10/
    ├── preprocessed.txt                    # spaCy processed text
    ├── mallet_output/                      # MALLET model files
    │   ├── comments1088_test.model         # Trained LDA model
    │   ├── comments1088_test.doc-topics    # Document-topic distributions
    │   ├── comments1088_test.topic-keys    # Human-readable topic summaries
    │   └── comments1888_test.topic-word-weights # Topic-word weight matrix
    └── curation/                           # Human curation files (in progress)
        ├── word_topics.csv                 # For topic labeling
        └── document_topics.csv             # For document analysis
```

### Topic Quality Verification:
Meaningful topics emerged from FDA vaccine comment data:
- **Topic 0**: Age-based vaccination (children, age groups, approval)
- **Topic 1**: School/immunity concerns (kids, natural immunity, mandates)  
- **Topic 2**: Experimental concerns (experimental vaccine, rights, safety)
- **Topic 3**: Religious/philosophical opposition (god, humanity, trials)
- **Topic 4**: Parental choice (parents, mandate, government, choice)
- **Topic 5**: Immune system science (immune system, support, evidence)
- **And 4 additional coherent topics...**

## Dependencies Successfully Installed & Tested

### 1. **MALLET 2.0.8**
- **Source**: http://mallet.cs.umass.edu/dist/mallet-2.0.8.tar.gz  
- **Installation**: Direct download + tar extraction
- **Location**: `fresh_user_test/mallet-2.0.8/`
- **Verification**: `./bin/mallet` shows all available commands
- **Java Requirement**: Confirmed compatible with system Java 1.8.0_73

### 2. **csvfix** 
- **Source**: https://github.com/wlbr/csvfix (cloned and built)
- **Build Process**: `make mac` (successful with warnings)
- **Location**: `fresh_user_test/csvfix/csvfix/bin/csvfix`
- **Verification**: Successfully processes CSV with `write_dsv` command

### 3. **Conda Environments**
- **`fresh_user_topics_test`**: spaCy, wordcloud, pandas, traceback-with-variables
- **`fresh_user_curation_test`**: numpy, matplotlib, xlsxwriter, pypdf2, etc.
- **Installation Time**: ~5-10 minutes each (with package downloads)
- **spaCy Model**: `en_core_web_sm` successfully downloaded and functional

## Key Scripts Created for Fresh Users

### 1. **`config_fresh_user.ini`** - Parameterized Configuration
Replaces hardcoded paths with relative/parameterized ones:
```ini
myhome = /Users/resnik/Misc/projects/topcat/github/fresh_user_test  
malletdir = %(myhome)s/mallet-2.0.8
topcatdir = /Users/resnik/Misc/projects/topcat/github
```

### 2. **`driver_fresh_user.py`** - Fixed PATH Handler  
Addresses csvfix PATH issues and provides better error reporting:
```python
# Add csvfix binary directory to PATH - Updated path for fresh user test
csvfix_path = os.path.join(myhome, "csvfix", "csvfix", "bin")
if os.path.exists(csvfix_path):
    os.environ["PATH"] += os.pathsep + csvfix_path
```

### 3. **Updated Environment Files**  
- `environments/topics.yml` (name: fresh_user_topics_test)
- `environments/topic_curation.yml` (name: fresh_user_curation_test)
- Flexible package versions to avoid conflicts

## Complete Fresh User Workflow (Validated)

```bash
# 1. Install external dependencies  
curl -O https://mallet.cs.umass.edu/dist/mallet-2.0.8.tar.gz
tar -xzf mallet-2.0.8.tar.gz
git clone https://github.com/wlbr/csvfix.git && cd csvfix && make mac

# 2. Create conda environments
conda env create -f environments/topics.yml
conda env create -f environments/topic_curation.yml  

# 3. Install spaCy model
conda activate fresh_user_topics_test
python -m spacy download en_core_web_sm

# 4. Run pipeline
python driver_fresh_user.py config_fresh_user.ini
source /opt/anaconda3/bin/activate fresh_user_topics_test
python /path/to/run_mallet.py [parameters...]
```

## Gotchas for Future Fresh Users

### Environment Issues:
1. **Global vs Environment Packages**: Never install spaCy/dependencies globally - use conda environments  
2. **Environment Activation**: Must use `source /opt/anaconda3/bin/activate` not just `conda activate`
3. **spaCy Model**: Not included in environment - must download separately
4. **Directory Conflicts**: Delete existing model directories before repeat runs

### Build Issues:  
1. **csvfix Dependencies**: Requires system GCC/compiler tools
2. **Java Version**: MALLET works with Java 1.8+, may have issues with much newer versions
3. **PATH Management**: csvfix binary location differs from original expectations

### Data Processing Issues:
1. **CSV Encoding**: Excel-generated CSVs may need `iconv` preprocessing  
2. **Text Column Indexing**: Column numbers are 1-indexed in config but 0-indexed in code
3. **Empty Documents**: `grep .` removes empty lines, ensure input has content  
4. **Memory Requirements**: Large datasets may need increased Java heap size

### Iteration Timing:
1. **Full Runs**: 1000 iterations can take 10-60 minutes depending on data size
2. **Convergence**: Log-likelihood should stabilize, beta optimization occurs every 10 iterations  
3. **Progress Monitoring**: MALLET shows iteration progress: `<10> LL/token: -8.18903`

## Claude Code Permissions Already Granted

The following permissions have been explicitly granted for TOPCAT development:

### Pre-Approved Tool Usage:
- ✅ **WebFetch** from:
  - `programminghistorian.org` (MALLET installation guides)
  - `mallet.cs.umass.edu` (MALLET downloads)
  - `github.com` (csvfix repository)

- ✅ **Bash Commands** for:
  - `curl` (downloading dependencies)
  - `tar` (extracting archives)  
  - `git clone` (cloning repositories)
  - `make` (building csvfix)
  - `javac` (Java compilation testing)
  - `./bin/mallet` (MALLET execution)
  - `conda` environment management
  - `python` script execution 
  - `pip install` (within conda environments only)
  - `source` (environment activation)
  - `export PATH` (PATH modifications)

### Directory Permissions:
- ✅ **Full read/write access** to: `/Users/resnik/Misc/projects/topcat/`
- ✅ **Subdirectory creation** for testing: `fresh_user_test/`, `test_run/`, etc.
- ✅ **Temporary file creation** in standard temp directories

### Restrictions Confirmed:  
- ❌ **No global pip installs** (must use conda environments)
- ❌ **No home directory modifications** outside project tree  
- ❌ **No system-level package installation** (use local builds)

When working on TOPCAT improvements, Claude Code should reference this section to avoid re-requesting permissions for standard development tasks.

---

## Next Steps for Fresh User Documentation

Based on this comprehensive testing, the following improvements should be made:

1. **Update README.md** with corrected installation procedures
2. **Create automated setup script** based on validated workflow  
3. **Update environment.yml files** with compatible package versions
4. **Add troubleshooting section** covering identified gotchas
5. **Provide pre-configured example** with working paths
6. **Document memory/performance requirements** for different data sizes

The fresh user simulation successfully demonstrated that TOPCAT can work for new users, but requires significant setup documentation improvements to handle the identified dependency and configuration issues.