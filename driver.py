import configparser
import os
import sys
import time
import argparse

def load_config(config_file):

    # Declare parameters as global
    # Yes, this is ugly! I'm being quick and dirty.
    global malletdir, topcatdir, csvfixdir, preproc, runmallet
    global rootdir, csv, textcol, modelname, datadir, outdir, granularities
    global workdir, rawdocs, preprocdir, stoplist, numiterations, maxdocs, seed
    global debug
    
    # Parse config file
    config = configparser.ConfigParser()
    config.read(config_file)

    # Are we debugging?
    debug = config.getboolean('variables', 'debug')
    if (debug):
        print("NOTE: Running in debugging mode")
    else:
        print("NOT IN DEBUGGING MODE")
    
    # Load installation variables
    malletdir = config.get('variables', 'malletdir')
    topcatdir = config.get('variables', 'topcatdir')
    csvfixdir = config.get('variables', 'csvfixdir')
    preproc   = config.get('variables', 'preproc')
    runmallet = config.get('variables', 'runmallet')

    # Load analysis-specific variables
    rootdir       = config.get('variables', 'rootdir')
    csv           = config.get('variables', 'csv')
    textcol       = config.get('variables', 'textcol')
    modelname     = config.get('variables', 'modelname')
    datadir       = config.get('variables', 'datadir')
    outdir        = config.get('variables', 'outdir')
    granularities = config.get('variables', 'granularities')

    # Check if output directories already exist to avoid overwriting
    if os.path.isdir(outdir) and not debug:
        print(f"Output directory {outdir} already exists. Exiting.")
        sys.exit(1)
    if os.path.isdir(datadir) and not debug:
        print(f"Output directory {datadir} already exists. Exiting.")
        sys.exit(1)
        
    # Load other variables
    workdir       = config.get('variables', 'workdir')
    rawdocs       = config.get('variables', 'rawdocs')
    preprocdir    = config.get('variables', 'preprocdir')
    stoplist      = config.get('variables', 'stoplist')
    numiterations = config.get('variables', 'numiterations')
    maxdocs       = config.get('variables', 'maxdocs')
    seed          = config.get('variables', 'seed')

    # Add csvfix binary directory to PATH
    csvfix_path = os.path.join(csvfixdir, "bin")
    if os.path.exists(csvfix_path):
        os.environ["PATH"] += os.pathsep + csvfix_path
        print(f"Added csvfix to PATH: {csvfix_path}")
    else:
        print(f"WARNING: csvfix not found at {csvfix_path}")




################################################################
# Main
################################################################
if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run TOPCAT topic modeling pipeline')
    parser.add_argument('--config', default='./config.ini',
                        help='Configuration file (default: ./config.ini)')
    args = parser.parse_args()

    # Read config
    load_config(args.config)

    # DEBUG
    if (debug):
        print("malletdir =\t {}".format(malletdir))
        print("topcatdir =\t {}".format(topcatdir))
        print("csvfixdir =\t {}".format(csvfixdir))
        print("preproc =\t {}".format(preproc))
        print("runmallet =\t {}".format(runmallet))
        print("rootdir =\t {}".format(rootdir))
        print("csv =\t {}".format(csv))
        print("textcol =\t {}".format(textcol))
        print("modelname =\t {}".format(modelname))
        print("datadir =\t {}".format(datadir))
        print("outdir =\t {}".format(outdir))
        print("granularities =\t {}".format(granularities))
        print("workdir =\t {}".format(workdir))
        print("rawdocs =\t {}".format(rawdocs))
        print("preprocdir =\t {}".format(preprocdir))
        print("stoplist =\t {}".format(stoplist))
        print("numiterations =\t {}".format(numiterations))
        print("maxdocs =\t {}".format(maxdocs))
        print("seed =\t {}".format(seed))
        print("\n")

    # Create output directories
    if (debug):
        os.makedirs(outdir,  exist_ok=True)
        os.makedirs(datadir, exist_ok=True)
    else:
        os.makedirs(outdir)
        os.makedirs(datadir)

    print("✅ Configuration loaded successfully!")
    print(f"📁 Output will be in: {outdir}")
    print(f"📊 Will process: {csv}")
    print(f"🔢 Granularities: {granularities}")