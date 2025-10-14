#!/usr/bin/env python3
"""
Test script to compare csvfix vs Python CSV extraction methods
Ensures both produce identical output before removing csvfix dependency
"""

import os
import sys
import tempfile
import shutil

# Add the code directory to Python path to import driver
sys.path.insert(0, '/Users/resnik/Misc/projects/topcat/github/code')

def create_test_config(use_python_csv=False):
    """Create a temporary config file for testing"""
    method_suffix = "python" if use_python_csv else "csvfix"
    config_content = f"""[variables]

# Installation variables
topcatdir = /Users/resnik/Misc/projects/topcat/github
malletdir = /Users/resnik/Misc/projects/topcat/github/Old/fresh_user_test/mallet-2.0.8
csvfixdir = /Users/resnik/Misc/projects/topcat/github/Old/fresh_user_test/csvfix/csvfix
preproc   = %(topcatdir)s/code/src/preprocessing_en.py
runmallet = %(topcatdir)s/code/src/run_mallet.py

# Analysis-specific variables  
rootdir       = /tmp/topcat_csv_test_{method_suffix}
csv           = %(topcatdir)s/example/fda_1088_sampled_2K.csv
textcol       = 2
granularities = 10
modelname     = csv_test
datadir       = %(rootdir)s/data
outdir        = %(rootdir)s/out

# Advanced parameters
workdir       = %(datadir)s/modeling
rawdocs       = %(workdir)s/%(modelname)s_raw.txt
preprocdir    = %(workdir)s/processed
stoplist      = %(malletdir)s/stoplists/en.txt
numiterations = 100
maxdocs       = 10
seed          = 13

debug = false
use_python_csv = {str(use_python_csv).lower()}
"""
    
    # Create temporary config file
    temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False)
    temp_config.write(config_content)
    temp_config.close()
    return temp_config.name

def run_extraction_test(use_python_csv):
    """Run text extraction with specified method and return output file path"""
    import driver
    
    # Create test config
    config_file = create_test_config(use_python_csv)
    
    try:
        # Load config
        driver.load_config(config_file)
        
        # Create output directory
        os.makedirs(driver.workdir, exist_ok=True)
        
        # Run extraction
        driver.extract_text()
        
        # Return the path to the generated file
        return driver.rawdocs
        
    finally:
        # Clean up config file
        os.unlink(config_file)

def compare_files(file1, file2):
    """Compare two files byte-for-byte"""
    if not os.path.exists(file1):
        return False, f"File 1 does not exist: {file1}"
    if not os.path.exists(file2):
        return False, f"File 2 does not exist: {file2}"
    
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        content1 = f1.read()
        content2 = f2.read()
    
    if content1 == content2:
        return True, "Files are identical"
    else:
        return False, f"Files differ: {len(content1)} vs {len(content2)} bytes"

def main():
    print("Testing CSV extraction methods...")
    print("="*50)
    
    # Clean up any existing test directories
    for suffix in ["csvfix", "python"]:
        test_root = f"/tmp/topcat_csv_test_{suffix}"
        if os.path.exists(test_root):
            shutil.rmtree(test_root)
    
    try:
        # Test csvfix method
        print("1. Testing csvfix extraction...")
        csvfix_output = run_extraction_test(use_python_csv=False)
        print(f"   Output: {csvfix_output}")
        
        # Test Python method
        print("2. Testing Python extraction...")
        python_output = run_extraction_test(use_python_csv=True)
        print(f"   Output: {python_output}")
        
        # Compare outputs
        print("3. Comparing outputs...")
        identical, message = compare_files(csvfix_output, python_output)
        
        print(f"   Result: {message}")
        
        if identical:
            print("\n✅ SUCCESS: Both methods produce identical output!")
            print("   Safe to switch to Python-only implementation")
        else:
            print("\n❌ FAILURE: Methods produce different output!")
            print("   Need to investigate differences before removing csvfix")
            
            # Show first few lines of each file for debugging
            print("\nFirst 5 lines from csvfix:")
            with open(csvfix_output, 'r') as f:
                for i, line in enumerate(f):
                    if i >= 5:
                        break
                    print(f"  {i+1}: {repr(line)}")
            
            print("\nFirst 5 lines from Python:")
            with open(python_output, 'r') as f:
                for i, line in enumerate(f):
                    if i >= 5:
                        break
                    print(f"  {i+1}: {repr(line)}")
        
        return identical
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test directories
        for suffix in ["csvfix", "python"]:
            test_root = f"/tmp/topcat_csv_test_{suffix}"
            if os.path.exists(test_root):
                shutil.rmtree(test_root)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)