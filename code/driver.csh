#!/bin/csh
#####################################################################
#
# TOPCAT DRIVER SCRIPT
#
# NLP preprocessing and topic modeling using MALLET,
# followed by creation of files for human topic model curation.
#
# Uses run_mallet.py to do preprocessing, run mallet, postprocessing
# These produce LDA output as word_topics.csv and document_topics.csv.
# Then uses the topic_curation package to create files suitable for
# use in the human curation process.
#
# Note that although many parameters are pulled into shell variables
# for easy adaptation, there are a number of hard-wired elements.
#
# Eventually this script should be converted into a top-level
# driver in Python, though note that different conda environments
# are active in different parts of the script so that will need
# to be taken care of, probably by combining into a single
# environment.
#
#####################################################################

#####################################################################
# Need to have C
# Add csvfix bin to path
#####################################################################
setenv PATH ~/misc/pkg/csvfix/csvfix-build/csvfix/bin:$PATH

################################################################
# Parameters you will need to update for your work
################################################################

# Installation variables
setenv MYHOME             /Users/myusername/misc
setenv MALLETDIR          $MYHOME/pkg/mallet/mallet-git/Mallet
setenv TOPCATDIR          $MYHOME/projects/topcat/github/code
setenv PREPROC            $TOPCATDIR/src/preprocessing_en.py
setenv RUNMALLET          $TOPCATDIR/src/run_mallet.py

#  Analysis-specific variables
#  See README.md for explanations of variables.
setenv ROOTDIR            $MYHOME/projects/hospital_reviews/Google_Reviews
setenv CSV                $ROOTDIR/reviews.csv
setenv TEXTCOL            9
setenv MODELNAME          reviews
setenv DATADIR            $ROOTDIR/data
setenv OUTDIR             $ROOTDIR/out
setenv GRANULARITIES      '(10 20 30)'

################################################################
# Other things you could change but probably won't need to.
# See README.md for explanations of variables.
################################################################


setenv WORKDIR            $DATADIR/modeling
setenv RAWDOCS            $WORKDIR/${MODELNAME}_raw.txt
setenv PREPROCDIR         $WORKDIR/processed
setenv STOPLIST           $MALLETDIR/stoplists/en.txt
setenv NUMITERATIONS      1000
setebv MAXDOCS            100

mkdir $OUTDIR
mkdir $DATADIR

################################################################
# Extracting text ("documents")
#
# Note: csvfix write_dsv -f 1  converts single col CSV to text
#
# Note: add tail -n+2 to exclude CSV header line?
#
# Note: need to add bookkeeping to preserve correspondence
#       with docID column so that documents can be linked back
#       to metadata, or see if simply removing grep . works.
################################################################

echo "Extracting text items from $CSV."
echo ""
echo "Note: if you have character encododing issues, e.g."
echo "weird-looking characters when using a CSV created using Microsoft Excel,"
echo "try starting with: iconv -f windows-1252 -t utf-8 -c < original.csv > utf8.csv"
echo "If iconv is not installed on your system see https://en.wikipedia.org/wiki/Iconv"
echo ""

mkdir -p $WORKDIR

cat $CSV \
| python $TOPCATDIR/code/src/csv_clean_lines.py \
> $WORKDIR/temp_clean.csv

# Extract just the text column from the CSV.
# If this doesn't work make sure the executable for csvfix is on your PATH.

csvfix write_dsv -f $TEXTCOL $WORKDIR/temp_clean.csv \
 | grep . \
 > $RAWDOCS

rm $WORKDIR/temp_clean.csv
 
echo "Done. Created $RAWDOCS"



################################################################
# Other than NUMTOPICS loop, in theory nothing below
# herer should require changing.
################################################################


# Loop through different topic model sizes
foreach NUMTOPICS $GRANULARITIES

  # Activate conda environment for the topic modeling
  conda activate topics

  echo "================================================================"
  echo "Running $NUMTOPICS topic model"
  echo "================================================================"

  setenv MODELDIR           $WORKDIR/model_k$NUMTOPICS
  setenv CURATIONDIR        $MODELDIR/curation
  setenv MALLET_OUTDIR      $MODELDIR/mallet_output
  setenv PREPROCESSED_DOCS  $MODELDIR/preprocessed.txt

  # Run preprocessing and mallet topic model and create output CSV files in $WORKDIR
  # Assumes $RAWDOCS contains documents one per line if present
  # Run 'python run_mallet.py -h' for details about commandline arguments
  #
  # TO DO: do preprocessing as a separate step first and use --preprocessed_docs
  # so that we don't have to do preprocessing every time through the loop for K
  mkdir $MODELDIR
  mkdir $CURATIONDIR
  python  $RUNMALLET \
    --package              mallet \
    --mallet_bin           $MALLETDIR/bin/mallet \
    --preprocessing        $PREPROC \
    --stoplist             $STOPLIST \
    --modelname            $MODELNAME \
    --raw_docs             $RAWDOCS \
    --preprocessed_docs    $PREPROCESSED_DOCS \
    --workdir              $WORKDIR \
    --modeldir             $MALLET_OUTDIR \
    --word_topics_file     $CURATIONDIR/word_topics.csv \
    --document_topics_file $CURATIONDIR/document_topics.csv \
    --numtopics            $NUMTOPICS \
    --numiterations        $NUMITERATIONS \
    --extra_args           "--random-seed 13" 

  # Generate cloud visualizations in $MODELDIR/theme_clouds
  # Note: topwords.py assumes document_topics.csv and word_topics.csv are in current directory
  # (TO DO: Add commandline options to topwords.py for source and destination directories.)
  pushd $CURATIONDIR
  echo "Creating clouds"
  python $TOPCAT/code/src/topwords.py > $CURATIONDIR/top_words.txt
  popd

  #
  # Generate model selection spreadsheets (bar-chart version of topic-word distribution plus top documents)
  #

  # Activate conda environment for generation of curation materials
  conda activate topic_curation

  # Convert run_mallet.py CSV file outputs to numpy
  echo "Converting run_mallet.py CSV outputs to numpy"
  python $$TOPCAT/code/src/convert_csv_to_npy.py \
    --topic_word $CURATIONDIR/word_topics.csv \
    --doc_topic  $CURATIONDIR/document_topics.csv \
    --output     $CURATIONDIR

  # Create curation file including top-docs and coherence ratings column
  echo "Creating topic curation file"
  python $$TOPCAT/code/src/create_topic_curation_files_with_custom_ratings_columns.py \
    --topic_word          $CURATIONDIR/topic_word.npy \
    --doc_topic           $CURATIONDIR/doc_topic.npy \
    --texts               $CURATIONDIR/raw_documents.txt \
    --vocab               $CURATIONDIR/vocab.txt \
    --output              $CURATIONDIR \
    --num_top_docs        -1 \
    --num_top_words       20 \
    --num_top_words_cloud 100 \
    --show_top_docs_in_topic_word_file \
    --num_top_docs_in_topic_word_file $MAXDOCS


  date
  echo "Done. Results in $CURATIONDIR"

# End of For loop for NUMTOPICS  
end

echo "Done"
date
echo "-----------------------"


# Gather up curation files suitable for distribution
mkdir $OUTDIR
foreach NUMTOPICS ( 50 70 100 )
  echo "Creating curation distribution files for granularity $NUMTOPICS"

  setenv MODELDIR           $WORKDIR/model_k$NUMTOPICS
  setenv CURATIONDIR        $MODELDIR/curation
  setenv PREFIX             granularity_${NUMTOPICS}
  setenv FINALDIR           $OUTDIR/$PREFIX
  mkdir -p $FINALDIR
  cp $CURATIONDIR/clouds.pdf            $FINALDIR/${PREFIX}_clouds.pdf
  cp $CURATIONDIR/topic_word.xlsx       $FINALDIR/${PREFIX}_categories.xlsx
  cp $CURATIONDIR/document_topics.xlsx  $FINALDIR/${PREFIX}_alldocs.xlsx
end

