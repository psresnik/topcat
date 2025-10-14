#!/usr/bin/env python3
"""
TOPCAT Installation Validation Script

This script tests whether TOPCAT has been installed correctly by checking
all major components:
- Configuration file setup
- TOPCAT conda environment  
- External dependencies (MALLET, csvfix)
- NLP preprocessing libraries
- Required Python packages

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
        print_status(f"Please copy templates/config_template.ini to {config_file} and edit paths", "FAIL")
        return False
    
    # Read configuration
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        
        malletdir = config.get('variables', 'malletdir') 
        topcatdir = config.get('variables', 'topcatdir')
        csvfixdir = config.get('variables', 'csvfixdir')
        use_python_csv = config.getboolean('variables', 'use_python_csv')
        
        print_status(f"Configuration loaded from {config_file}")
        if use_python_csv:
            print_status("Using Python CSV extraction (no csvfix required)")
        else:
            print_status("Using csvfix for CSV extraction")
        
    except Exception as e:
        print_status(f"Configuration file error: {str(e)}", "FAIL")
        return False
    
    # Check key directories and files
    all_checks_passed = True
    
    # Check MALLET installation
    mallet_bin = os.path.join(malletdir, "bin", "mallet")
    if not check_file_exists(mallet_bin, "MALLET binary"):
        all_checks_passed = False
    
    # Check csvfix (only if using csvfix extraction)
    if not use_python_csv:
        csvfix_bin = os.path.join(csvfixdir, "bin", "csvfix") 
        if not check_file_exists(csvfix_bin, "csvfix binary"):
            all_checks_passed = False
    else:
        print_status("csvfix validation skipped (using Python CSV extraction)", "PASS")
    
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
    
    # Test that we're in the right conda environment
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print_status("spaCy language model", "PASS")
    except ImportError:
        print_status("spaCy not available - make sure you're in the topcat environment", "FAIL")
        all_checks_passed = False
    except OSError:
        print_status("spaCy model 'en_core_web_sm' not found - run: python -m spacy download en_core_web_sm", "FAIL")
        all_checks_passed = False
    
    # Test other required packages
    required_packages = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'), 
        ('matplotlib', 'matplotlib'),
        ('wordcloud', 'wordcloud'),
        ('xlsxwriter', 'xlsxwriter'),
        ('configargparse', 'configargparse'),
        ('kneed', 'kneed'),
        ('tqdm', 'tqdm')
    ]
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print_status(f"{package_name} package", "PASS")
        except ImportError:
            print_status(f"{package_name} package not available", "FAIL")
            all_checks_passed = False
    
    # Test MALLET
    mallet_test = f"{mallet_bin} --help"
    if not run_command(mallet_test, "MALLET command", check_return_code=False):
        all_checks_passed = False
    
    # Test csvfix (only if using csvfix extraction)
    if not use_python_csv:
        csvfix_test = f"{csvfix_bin} help"
        if not run_command(csvfix_test, "csvfix command", check_return_code=False):
            all_checks_passed = False
    else:
        print_status("csvfix functional test skipped (using Python CSV extraction)", "PASS")
    
    print("\n" + "="*60)
    print("VALIDATION RESULTS")
    print("="*60)
    
    if all_checks_passed:
        print_status("All validation tests PASSED!", "PASS")
        print("\nYour TOPCAT installation appears to be working correctly.")
        print(f"You can now run: python code/driver.py --config {config_file}")
        print("\nExpected processing time: 10 minutes for example dataset")
        print("Expected output: Files in your configured output directory")
        return True
    else:
        print_status("Some validation tests FAILED", "FAIL") 
        print("\nPlease check INSTALL_TROUBLESHOOTING.md for solutions")
        print("Common issues:")
        print("  - Not running in topcat environment (run: conda activate topcat)")
        print("  - Missing spaCy language model (run: python -m spacy download en_core_web_sm)")
        print(f"  - Incorrect paths in {config_file}")
        print("  - Missing Python packages (recreate environment: conda env create -f code/topcat.yml)")
        print("  - External dependencies not built correctly")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
