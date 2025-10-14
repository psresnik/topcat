################################################################
# Python driver for topic modeling and creating visualizations.
#
#   Currently just handles MALLET.
#   Planning to extend to handle other packages.
#
#   Note: change default values at top for your local install.
#
#   Note: uses os.system(cmd) to run shell commands where
#   cmd is constructed using commandline arguments. Be careful
#   about this from a security perspective!
#
#   Note: If you encounter encoding errors, try using
#   'iconv -f windows-1252 -t utf-8 -c' on the offending file.
#
#   Author: Philip Resnik (resnik@umd.edu)
#   
################################################################
# Next line can be deleted if you prefer normal python error traceback
#  from traceback_with_variables import activate_by_import

import argparse
import tempfile
import os
import sys
import pandas as pd

################################################################
# Default values. Change these for your local installation.
################################################################
default_mallet_bin           =  '/Users/resnik/misc/pkg/mallet/mallet-git/Mallet/bin'
default_stoplist             =  '/Users/resnik/misc/pkg/mallet/mallet-git/Mallet/stoplists/en.txt'
default_preprocessing        =  '/Users/resnik/misc/projects/rapid2020_nsf/modeling/preprocessing.py'
default_model2csv            =  '/Users/resnik/Misc/pkg/scholar_clip/scholar/utils/model2csv.py'
default_word_topics_file     =  './word_topics.csv'
default_document_topics_file =  './document_topics.csv'
default_optimize_interval    =  10

################################################################
# Handle command line
################################################################
parser = argparse.ArgumentParser(description='Driver to run topic modeling')
parser.add_argument('-p','--package',
                        help='Topic model package: scholar, mallet, segan',             dest='package',      default='mallet')
parser.add_argument('-W','--workdir',
                        help='Directory to contain preprocessed/imported files',        dest='workdir',      default=None)
parser.add_argument('-m','--modeldir',
                        help='Model output directory, usually under workdir',           dest='modeldir',     default=None)
parser.add_argument('-M','--modelname',
                        help='Name to use for model',                                   dest='modelname',    default='model')
parser.add_argument('-r','--raw_docs',
                        help='File containing raw documents one per line',              dest='raw_docs',     default=None)
parser.add_argument('-d','--preprocessed_docs',
                        help='File containing preprocessed documents one per line. ' \
                        'If RAW_DOCS is provided instead, this file is created',        dest='preprocessed_docs',      default=None)
parser.add_argument('-w','--word_topics_file',
                        help='Path to output CSV file for topic-words distribution',    dest='word_topics_file',       default=default_word_topics_file)
parser.add_argument('-D','--document_topics_file',
                        help='Path to output CSV file for doc-topics distribution',     dest='document_topics_file',   default=default_document_topics_file)
parser.add_argument('-b','--mallet_bin',
                        help='Path to mallet bin',                                      dest='mallet_bin',             default=default_mallet_bin)
parser.add_argument('-P','--preprocessing',
                        help='Path to preprocessing.py',                                dest='preprocessing',          default=default_preprocessing)
parser.add_argument('-c','--model2csv',
                        help='Path to model2csv.py',                                    dest='model2csv',              default=default_model2csv)
parser.add_argument('-s','--stoplist',
                        help='Path to stoplist that preprocessing.py will use',         dest='stoplist',               default=default_stoplist)
parser.add_argument('-k','--numtopics',
                        help='Number of topics',                                        dest='numtopics',              default=10)
parser.add_argument('-i','--numiterations',
                        help='Number of iterations',                                    dest='numiterations',          default=1000)
parser.add_argument('-x','--extra_args',
                        help='Command-line flags to add to topic modeling command. ' \
                        'For example: -x "--random-seed 42 --beta 0.1"',                dest='extra_args',             default='')


args = vars(parser.parse_args())
package               = args['package']
workdir               = args['workdir']
modeldir              = args['modeldir']
raw_docs              = args['raw_docs']
preprocessed_docs     = args['preprocessed_docs']
modelname             = args['modelname']
word_topics_file      = args['word_topics_file']
document_topics_file  = args['document_topics_file']
mallet_bin            = args['mallet_bin']
preprocessing         = args['preprocessing']
model2csv             = args['model2csv']
stoplist              = args['stoplist']
numtopics             = args['numtopics']
numiterations         = args['numiterations']
extra_args            = args['extra_args']

if args['workdir'] is None :
    parser.error('Required arguments: --workdir. Use -h to see detailed usage info.')
    sys.exit(1)
if args['modeldir'] is None:
    modeldir = "{}/{}".format(workdir, modelname)
if preprocessed_docs is None and raw_docs is None:
    parser.error('Either --preprocessed_docs or --raw_docs is required. Use -h to see detailed usage info.')
    sys.exit(1)
if (package != 'mallet'):
    sys.stderr.write("Not yet handling package '{}'\n".format(package))
    sys.exit(1)
    
################################################################
# Main
################################################################

# If raw documents are provided, do preprocessing
if raw_docs is not None:
    
    # Run preprocessing, collect output
    # Note: optional arg --emptyline 'contents" can be used to make sure preproc docs have no blank lines 
    tempfile_fp    = tempfile.NamedTemporaryFile()
    tempfile_name  = tempfile_fp.name
    template       = "python {} --stoplist {} --infile {} > {}"
    cmd            = template.format(preprocessing, stoplist, raw_docs, tempfile_name)
    sys.stderr.write("Running: {}\n".format(cmd))
    os.system(cmd)

    # Convert to mallet 3-column format: docID<tab>label<tab>text, using modelname as label and numbering docIDs sequentially
    # Then clean up temporary file
    sys.stderr.write("Converting {} to 3-column format and writing to {}\n".format(tempfile_name, preprocessed_docs))

    # Commenting out version where pd.read_csv was used to create dataframe
    # Instead, just reading lines from the file as strings into a fresh dataframe
    # docs_df  = pd.read_csv(tempfile_name, sep='\t', encoding='utf-8', header=None, engine='python', on_bad_lines='warn', skip_blank_lines = False)
    with open(tempfile_name, 'r') as file:
          lines = file.read().splitlines()
    docs_df = pd.DataFrame(lines, columns=['text'])
    docs_df.insert(loc = 0, column = 'modelname', value = modelname)
    docs_df.insert(loc = 0, column = 'docID',     value = [x+1 for x in range(len(docs_df.index))])
    docs_df.to_csv(preprocessed_docs, sep='\t', index=False, header=False)
    sys.stderr.write("Done writing to {}\n".format(preprocessed_docs))

    tempfile_fp.close()

# Import preprocessed documents 
importfile = "{}/{}.mallet".format(workdir, modelname)
template   = "{}/mallet import-file --input {} --output {} --token-regex '\\S+' --preserve-case --keep-sequence"
cmd        = template.format(mallet_bin, preprocessed_docs, importfile)
sys.stderr.write("Running: {}\n".format(cmd))
os.system(cmd)

# Create topic model
# For details on parameters: malletbin/mallet train-topics --help
if (os.path.isdir(modeldir)):
    sys.stderr.write("Error: can't create model directory {} because it already exists. Exiting.\n".format(modeldir))
    sys.exit(3)
os.mkdir(modeldir)
template = "{}/mallet train-topics " \
   " --input {}" \
   " --num-topics {}" \
   " --optimize-interval {}" \
   " --num-iterations {}" \
   " {}" \
   " --output-model             MODELDIR/MODELNAME.model" \
   " --output-doc-topics        MODELDIR/MODELNAME.doc-topics" \
   " --output-topic-keys        MODELDIR/MODELNAME.topic-keys" \
   " --output-state             MODELDIR/MODELNAME.topic-state.gz" \
   " --inferencer-filename      MODELDIR/MODELNAME.inferencer" \
   " --word-topic-counts-file   MODELDIR/MODELNAME.word-topic-counts" \
   " --topic-word-weights-file  MODELDIR/MODELNAME.topic-word-weights"
template = template.format(mallet_bin, importfile, numtopics, default_optimize_interval, numiterations, extra_args)
template = template.replace('MODELDIR',  modeldir)
template = template.replace('MODELNAME', modelname)
cmd      = ' '.join(template.split()) # Multiple spaces in string -> single space
sys.stderr.write("Running: {}\n".format(cmd))
os.system(cmd)

if (model2csv):
    
  # Convert model output to CSV format
  if raw_docs:
      # Create 3-column format for raw documents, as expected by model2csv
      docfile_fp  = tempfile.NamedTemporaryFile()
      docfile     = docfile_fp.name
      sys.stderr.write("Converting {} to 3-column format and writing to {}\n".format(raw_docs, docfile))
      # Commenting out version where pd.read_csv was used to create dataframe
      # since this is now throwing an error, even after updating to use on_bad_lines.
      #  # Pandas handling of bad lines changed from < 1.3 to >= 1.3
      #  # raw_docs_df  = pd.read_csv(raw_docs, sep='\t', encoding='utf-8', header=None, engine='python', warn_bad_lines=True, error_bad_lines=True)
      #  raw_docs_df  = pd.read_csv(raw_docs, sep='\t', encoding='utf-8', header=None, engine='python', on_bad_lines='warn')
      # Instead, just reading lines from the file as strings into a fresh dataframe
      with open(raw_docs, 'r') as file:
          lines = file.read().splitlines()
      raw_docs_df = pd.DataFrame(lines, columns=['text'])
      raw_docs_df.insert(loc = 0, column = 'modelname', value = modelname)
      raw_docs_df.insert(loc = 0, column = 'docID',     value = [x+1 for x in range(len(raw_docs_df.index))])
      raw_docs_df.to_csv(docfile, sep='\t', index=False, header=False)
  else:
      # Preprocessed docs file is already in the 3-column format
      docfile = preprocessed_docs

  template = "python {} --package mallet --docfile {} --modeldir {} --modelname {} --word_topics_file {} --document_topics_file {} --vocabfile {}/{}.word-topic-counts"
  cmd      = template.format(model2csv, docfile, modeldir, modelname, word_topics_file, document_topics_file, modeldir, modelname)
  sys.stderr.write("Creating CSV files. Running: {}\n".format(cmd))
  os.system(cmd)

  if raw_docs:
      sys.stderr.write("Cleaning up {}\n".format(docfile))
      docfile_fp.close()



 
 
 
 
 
 
 
 
 
 
   
