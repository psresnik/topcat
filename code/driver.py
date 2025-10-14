import configparser
import os
import sys
import time
import subprocess
import argparse
import csv as csv_module

def extract_csv_column_python(csv_file, column_index, output_file):
    """
    Python replacement for csvfix write_dsv -f N
    Extracts column N from CSV file and outputs each value on separate line
    Includes header to match csvfix behavior exactly
    """
    with open(csv_file, 'r', encoding='utf-8', newline='') as infile:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            reader = csv_module.reader(infile)
            
            for row in reader:
                if len(row) > column_index:
                    # Output the field value, handling empty fields
                    outfile.write(row[column_index] + '\n')
                else:
                    # Handle case where row doesn't have enough columns
                    outfile.write('\n')

def load_config(config_file):

    # Declare parameters as global
    # Yes, this is ugly! I'm being quick and dirty.
    global malletdir, topcatdir, preproc, runmallet
    global rootdir, csv, textcol, modelname, datadir, outdir, granularities
    global workdir, rawdocs, preprocdir, stoplist, numiterations, maxdocs, seed
    global debug, dry_run, use_python_csv
    
    # Parse config file
    config = configparser.ConfigParser()
    config.read(config_file)
    
    # Initialize dry_run mode (set by command line, default to False)
    if 'dry_run' not in globals():
        global dry_run
        dry_run = False

    # Are we debugging?
    debug = config.getboolean('variables', 'debug')
    if (debug):
        print("NOTE: Running in debugging mode")
    else:
        print("NOT IN DEBUGGING MODE")
    
    # Check CSV extraction method
    use_python_csv = config.getboolean('variables', 'use_python_csv')
    if (use_python_csv):
        print("Using Python CSV extraction (no csvfix dependency)")
    else:
        print("Using csvfix for CSV extraction")
    
    # Load installation variables
    malletdir = config.get('variables', 'malletdir')
    topcatdir = config.get('variables', 'topcatdir')
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
    csvfixdir = config.get('variables', 'csvfixdir')
    csvfix_path = os.path.join(csvfixdir, "bin")
    if os.path.exists(csvfix_path):
        os.environ["PATH"] += os.pathsep + csvfix_path
    else:
        print(f"Warning: csvfix binary directory not found at {csvfix_path}")




def extract_text():
    """Phase 1: Extract text from CSV"""
    print(f"Extracting text items from {csv}.")
    print("")
    print("Note: if you have character encoding issues, e.g.")
    print("weird-looking characters when using a CSV created using Microsoft Excel,")
    print("try starting with: iconv -f windows-1252 -t utf-8 -c < original.csv > utf8.csv")
    print("If iconv is not installed on your system see https://en.wikipedia.org/wiki/Iconv")
    print("")

    if dry_run:
        print(f"[DRY RUN] Would create workdir: {workdir}")
        print(f"[DRY RUN] Would clean CSV lines using: {os.path.join(topcatdir, 'code/src/csv_clean_lines.py')}")
        extraction_method = "Python CSV module" if use_python_csv else "csvfix"
        print(f"[DRY RUN] Would extract column {textcol} from CSV using {extraction_method}")
        print(f"[DRY RUN] Would create output file: {rawdocs}")
        return

    # Create workdir
    os.makedirs(workdir, exist_ok=True)
    
    # Clean CSV lines
    temp_clean = os.path.join(workdir, "temp_clean.csv")
    csv_clean_script = os.path.join(topcatdir, "code/src/csv_clean_lines.py")
    
    with open(csv, 'r') as input_file:
        with open(temp_clean, 'w') as output_file:
            subprocess.run(["python", csv_clean_script], stdin=input_file, stdout=output_file, check=True)
    
    # Extract text column using either csvfix or Python
    if use_python_csv:
        # Use Python CSV extraction
        temp_extracted = os.path.join(workdir, "temp_extracted.txt")
        extract_csv_column_python(temp_clean, int(textcol) - 1, temp_extracted)  # Convert to 0-based indexing
        
        with open(temp_extracted, 'r') as input_file:
            lines = input_file.read().split('\n')
        os.remove(temp_extracted)
    else:
        # Use csvfix extraction  
        cmd = [
            "csvfix", "write_dsv", "-f", str(textcol), temp_clean
        ]
        p1 = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = p1.stdout.split('\n')
    
    # Filter empty lines and skip first line (header) - same for both methods
    with open(rawdocs, 'w') as output_file:
        filtered_lines = [line for line in lines[1:] if line.strip()]
        output_file.write('\n'.join(filtered_lines))
    
    # Clean up temp file
    os.remove(temp_clean)
    print(f"Done. Created {rawdocs}")


def run_topic_modeling(numtopics):
    """Phase 2: Run topic modeling for given number of topics"""
    print("================================================================")
    print(f"Running {numtopics} topic model")
    print("================================================================")
    
    modeldir = os.path.join(workdir, f"model_k{numtopics}")
    curationdir = os.path.join(modeldir, "curation")
    mallet_outdir = os.path.join(modeldir, "mallet_output")
    preprocessed_docs = os.path.join(modeldir, "preprocessed.txt")
    
    if dry_run:
        print(f"[DRY RUN] Would create directories: {modeldir}, {curationdir}")
        print(f"[DRY RUN] Would run MALLET with {numtopics} topics, {numiterations} iterations")
        print(f"[DRY RUN] Would use stoplist: {stoplist}")
        print(f"[DRY RUN] Would create preprocessed docs: {preprocessed_docs}")
        print(f"[DRY RUN] Would output word_topics.csv and document_topics.csv to: {curationdir}")
        return curationdir
    
    # Create directories (but let run_mallet.py create mallet_outdir itself)
    os.makedirs(modeldir, exist_ok=True)
    os.makedirs(curationdir, exist_ok=True)
    
    # In debug mode, clean up existing mallet_outdir so run_mallet.py can recreate it
    if debug and os.path.exists(mallet_outdir):
        import shutil
        print(f"Debug mode: removing existing {mallet_outdir}")
        shutil.rmtree(mallet_outdir)
    # Note: mallet_outdir will be created by run_mallet.py
    
    # Run MALLET topic modeling
    cmd = [
        "python", runmallet,
        "--package", "mallet",
        "--mallet_bin", os.path.join(malletdir, "bin"),
        "--preprocessing", preproc,
        "--stoplist", stoplist,
        "--modelname", modelname,
        "--raw_docs", rawdocs,
        "--preprocessed_docs", preprocessed_docs,
        "--workdir", workdir,
        "--modeldir", mallet_outdir,
        "--model2csv", os.path.join(topcatdir, "code/src/model2csv.py"),
        "--word_topics_file", os.path.join(curationdir, "word_topics.csv"),
        "--document_topics_file", os.path.join(curationdir, "document_topics.csv"),
        "--numtopics", str(numtopics),
        "--numiterations", str(numiterations),
        "--extra_args", f"--random-seed {seed}"
    ]
    
    subprocess.run(cmd, check=True)
    return curationdir


def generate_curation_materials(curationdir):
    """Phase 3: Generate human curation materials"""
    print("Converting run_mallet.py CSV outputs to numpy")
    
    if dry_run:
        print(f"[DRY RUN] Would convert CSV to numpy in: {curationdir}")
        print(f"[DRY RUN] Would create topic curation files with {maxdocs} top docs")
        print(f"[DRY RUN] Would generate Excel files and PDF word clouds")
        return
    
    # Convert CSV to numpy
    cmd = [
        "python", os.path.join(topcatdir, "code/src/convert_csv_to_npy.py"),
        "--topic_word", os.path.join(curationdir, "word_topics.csv"),
        "--doc_topic", os.path.join(curationdir, "document_topics.csv"),
        "--output", curationdir
    ]
    subprocess.run(cmd, check=True)
    
    print("Creating topic curation file")
    
    # Create curation files
    cmd = [
        "python", os.path.join(topcatdir, "code/src/create_topic_curation_files_with_custom_ratings_columns.py"),
        "--topic_word", os.path.join(curationdir, "topic_word.npy"),
        "--doc_topic", os.path.join(curationdir, "doc_topic.npy"),
        "--texts", os.path.join(curationdir, "raw_documents.txt"),
        "--vocab", os.path.join(curationdir, "vocab.txt"),
        "--output", curationdir,
        "--num_top_docs", "-1",
        "--num_top_words", "20",
        "--num_top_words_cloud", "100",
        "--show_top_docs_in_topic_word_file",
        "--num_top_docs_in_topic_word_file", str(maxdocs)
    ]
    subprocess.run(cmd, check=True)


def organize_final_output(granularities_list):
    """Phase 4: Organize final output files"""
    print("================================================================")
    print("Gathering human curation files")
    
    if dry_run:
        print(f"[DRY RUN] Would organize final output files in: {outdir}")
        for numtopics in granularities_list:
            prefix = f"granularity_{numtopics}"
            finaldir = os.path.join(outdir, prefix)
            print(f"[DRY RUN] Would create: {finaldir}/{prefix}_clouds.pdf")
            print(f"[DRY RUN] Would create: {finaldir}/{prefix}_categories.xlsx")
            print(f"[DRY RUN] Would create: {finaldir}/{prefix}_alldocs.xlsx")
        return
    
    for numtopics in granularities_list:
        print(f"Gathering human curation files for granularity {numtopics}")
        
        modeldir = os.path.join(workdir, f"model_k{numtopics}")
        curationdir = os.path.join(modeldir, "curation")
        prefix = f"granularity_{numtopics}"
        finaldir = os.path.join(outdir, prefix)
        
        os.makedirs(finaldir, exist_ok=True)
        
        # Copy files
        import shutil
        shutil.copy(os.path.join(curationdir, "clouds.pdf"), 
                   os.path.join(finaldir, f"{prefix}_clouds.pdf"))
        shutil.copy(os.path.join(curationdir, "topic_word.xlsx"), 
                   os.path.join(finaldir, f"{prefix}_categories.xlsx"))
        shutil.copy(os.path.join(curationdir, "document_topics.xlsx"), 
                   os.path.join(finaldir, f"{prefix}_alldocs.xlsx"))


################################################################
# Main
################################################################
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description='TOPCAT: Topic-Oriented Protocol for Content Analysis of Text')
    parser.add_argument('--config', default='./config.ini', help='Configuration file path')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without actually running')
    args = parser.parse_args()
    
    # Set global dry_run flag
    dry_run = args.dry_run
    
    # Load configuration
    load_config(args.config)

    if dry_run:
        print("🧪 DRY RUN MODE - showing what would be done without executing")
        print("="*70)
    
    print(f"Starting: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # DEBUG output
    if debug:
        print("malletdir =\t {}".format(malletdir))
        print("topcatdir =\t {}".format(topcatdir))
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
    if dry_run:
        print(f"[DRY RUN] Would create output directory: {outdir}")
        print(f"[DRY RUN] Would create data directory: {datadir}")
    else:
        if debug:
            os.makedirs(outdir, exist_ok=True)
            os.makedirs(datadir, exist_ok=True)
        else:
            os.makedirs(outdir)
            os.makedirs(datadir)

    # Phase 1: Extract text
    extract_text()

    # Parse granularities
    granularities_list = [int(x) for x in granularities.split()]

    # Phase 2 & 3: Loop through different topic model sizes
    for numtopics in granularities_list:
        curationdir = run_topic_modeling(numtopics)
        generate_curation_materials(curationdir)
        print(f"Done with {numtopics} topics: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Phase 4: Organize final output
    organize_final_output(granularities_list)

    print("================================================================")
    if dry_run:
        print("🧪 DRY RUN COMPLETED - no files were actually created")
        print("To run for real, remove the --dry-run flag")
        print(f"Would process {len(granularities_list)} topic granularities: {granularities_list}")
        print(f"Estimated processing time: {len(granularities_list) * 5}-{len(granularities_list) * 20} minutes")
    else:
        print(f"Done: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Files for human curation are in {outdir}")
    print("================================================================")
