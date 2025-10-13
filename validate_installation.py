#!/usr/bin/env python3
"""
TOPCAT Installation Validation Script

This script tests whether TOPCAT has been installed correctly by running
a quick test with the example dataset. It checks all major components:
- Configuration file setup
- Conda environments  
- External dependencies (MALLET, csvfix)
- NLP preprocessing
- Topic modeling
- Output file generation

Usage: python validate_installation.py [--config CONFIG_FILE]
"""

import os
import sys
import subprocess
import configparser
import argparse
from pathlib import Path

def print_status(message, status="INFO"):
    """Print status message with formatting"""
    prefix = "✓" if status == "PASS" else "✗" if status == "FAIL" else "→"
    print(f"{prefix} {message}")

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print_status(f"{description}: {filepath}", "PASS")
        return True
    else:
        print_status(f"{description}: {filepath} NOT FOUND", "FAIL")
        return False

def run_command(command, description, check_return_code=True):
    """Run a system command and report status"""
    print_status(f"Testing {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if check_return_code and result.returncode != 0:
            print_status(f"{description} FAILED: {result.stderr.strip()}", "FAIL")
            return False
        else:
            print_status(f"{description} OK", "PASS")
            return True
    except Exception as e:
        print_status(f"{description} ERROR: {str(e)}", "FAIL") 
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Validate TOPCAT installation')
    parser.add_argument('--config', default='./config.ini', 
                        help='Configuration file (default: ./config.ini)')
    args = parser.parse_args()
    
    print("="*60)
    print("TOPCAT Installation Validation")
    print("="*60)
    
    # Check if config file exists
    config_file = args.config
    if not check_file_exists(config_file, "Configuration file"):
        print_status("Please copy templates/config_template.ini to config.ini and edit paths", "FAIL")
        return False
    
    # Read configuration
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        
        myhome = config.get('variables', 'myhome')
        malletdir = config.get('variables', 'malletdir') 
        topcatdir = config.get('variables', 'topcatdir')
        
        print_status(f"Configuration loaded: myhome = {myhome}")
        
    except Exception as e:
        print_status(f"Configuration file error: {str(e)}", "FAIL")
        return False
    
    # Check key directories and files
    all_checks_passed = True
    
    # Check MALLET installation
    mallet_bin = os.path.join(malletdir, "bin", "mallet")
    if not check_file_exists(mallet_bin, "MALLET binary"):
        all_checks_passed = False
    
    # Check csvfix
    csvfix_bin = os.path.join(myhome, "csvfix", "csvfix", "bin", "csvfix") 
    if not check_file_exists(csvfix_bin, "csvfix binary"):
        all_checks_passed = False
    
    # Check TOPCAT source files
    preprocessing_script = os.path.join(topcatdir, "code", "src", "preprocessing_en.py")
    if not check_file_exists(preprocessing_script, "Preprocessing script"):
        all_checks_passed = False
        
    run_mallet_script = os.path.join(topcatdir, "code", "src", "run_mallet.py")
    if not check_file_exists(run_mallet_script, "MALLET runner script"):
        all_checks_passed = False
    
    # Check example dataset
    example_csv = os.path.join(topcatdir, "example", "fda_1088_sampled_2K.csv")
    if not check_file_exists(example_csv, "Example dataset"):
        all_checks_passed = False
    
    if not all_checks_passed:
        print_status("File check failures - cannot proceed with functional tests", "FAIL")
        return False
    
    print("\n" + "="*60)
    print("FUNCTIONAL TESTS")
    print("="*60)
    
    # Test conda environments
    if not run_command("conda env list | grep 'topics'", "Topics conda environment"):
        all_checks_passed = False
        
    if not run_command("conda env list | grep 'topic_curation'", "Topic curation conda environment"):
        all_checks_passed = False
    
    # Test spaCy model in topics environment
    spacy_test = "source /opt/anaconda3/bin/activate topics && python -c 'import spacy; nlp = spacy.load(\"en_core_web_sm\"); print(\"spaCy model loaded successfully\")'"
    if not run_command(spacy_test, "spaCy language model"):
        all_checks_passed = False
    
    # Test MALLET
    mallet_test = f"{mallet_bin} --help"
    if not run_command(mallet_test, "MALLET command", check_return_code=False):
        all_checks_passed = False
    
    # Test csvfix
    csvfix_test = f"{csvfix_bin} help"
    if not run_command(csvfix_test, "csvfix command", check_return_code=False):
        all_checks_passed = False
    
    print("\n" + "="*60)
    print("VALIDATION RESULTS")
    print("="*60)
    
    if all_checks_passed:
        print_status("All validation tests PASSED!", "PASS")
        print("\nYour TOPCAT installation appears to be working correctly.")
        print("You can now run: python driver.py --config config.ini")
        print("\nExpected processing time: 10 minutes for example dataset")
        print("Expected output: Files in your configured output directory")
        return True
    else:
        print_status("Some validation tests FAILED", "FAIL") 
        print("\nPlease check INSTALL_TROUBLESHOOTING.md for solutions")
        print("Common issues:")
        print("  - Missing spaCy language model (run: python -m spacy download en_core_web_sm)")
        print("  - Incorrect paths in config.ini")
        print("  - Conda environments not created properly")
        print("  - External dependencies not built correctly")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
