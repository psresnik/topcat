################################################################
#
#  Converts topic model output to CSV suitable as input for
#  utilities for topic visualization and model comparison
#
#  Example for Scholar:
#    python model2csv.py
#    --package   scholar
#    --docfile   /path/to/documents.jsonlist
#    --modeldir  /path/to/scholar_model_output/
#    --vocabfile /path/to/scholar_model_output/vocab.json
#
#  Example for Segan:
#    python model2csv.py
#    --package   segan
#    --docfile   example/open_1.csv 
#    --modeldir  example/segan_data/models/797EB5C4-F0C7-11E7-8E04-C9F8A43A3182/RANDOM_LDA_K-15_B-100_M-500_L-10_a-0.1_b-0.1_opt-false
#    --vocabfile example/segan_data/import/segan_files/segan.wvoc
#    --docids    example/segan_data/import/segan_files/segan.docinfo
#
#  Example for Mallet:
#    python model2csv.py
#    --package   mallet
#    --docfile   /path/to/preprocessed_documents.txt
#    --modeldir  /path/to/mallet_model_output/
#    --vocabfile /path/to/mallet_model_output/model.word-topic-counts
#
################################################################
from traceback_with_variables import activate_by_import
import argparse
import pandas as pd
import numpy as np
import json
import os
import sys
import csv
from collections import defaultdict
from tqdm import tqdm


def softmax_rows_in_2d_array(X):
    # Converts rows of unnormalized logits (e.g. Scholar's beta/phi matrix) to probability distributions
    # Adapted from https://nolanbconaway.github.io/blog/2017/softmax-numpy
    sys.stderr.write("Normalizing...\n")
    result = np.empty(X.shape)
    for i in tqdm(range(X.shape[0])):
        result[i,:]  = np.exp(X[i,:])
        result[i,:] /= np.sum(result[i,:])
    return result 

def convert_scholar(modeldir, docfile, vocabfile, word_topics_file):
    
    # Read in original documents and the vocabulary file
    docs_df = pd.read_json(docfile, lines=True)
    with open(vocabfile) as f:
        vocab_list = json.load(f)

    # Load beta matrix (topic-word unnormalized logit weights),
    # convert to topic-word distributions,
    # transpose to get word-topic matrix,
    # convert to a dataframe with 'Word' as the first column,
    # output to CSV file.
    beta          = np.load(os.path.join(modeldir, 'beta.npz'))['beta']
    beta_distrib  = softmax_rows_in_2d_array(beta)
    betaT         = np.transpose(beta_distrib)
    V, K          = betaT.shape
    labels        = ["Topic {}".format(str(i+1)) for i in range(K)]
    betaT_df      = pd.DataFrame(betaT, columns = labels)
    betaT_df.insert(0, 'Word', vocab_list)
    betaT_df.to_csv(word_topics_file, index=False)
    sys.stderr.write("Wrote {}\n".format(word_topics_file))

    # Load theta (document-topic proportions) matrix (training docs only, not dev/test),
    # and document jsonlines.
    npz   = np.load(os.path.join(modeldir, 'theta.train.npz')) 
    ids   = npz['ids']
    theta = npz['theta']
    n_docs, n_topics = theta.shape
    with open(docfile) as f:
        doc_jsonl = f.readlines()
    
    # For CSV output header and one row per document
    with open(document_topics_file, 'w', encoding="utf-8", errors="replace") as csvfile:
        writer = csv.writer(csvfile, dialect='excel', delimiter=',', quoting=csv.QUOTE_ALL)
        row = ['docID'] + labels + ['text']
        writer.writerow(row)
        for i in range(n_docs):
            doc         = json.loads(doc_jsonl[i])
            text        = doc['text'].replace("\n", " ")
            row         = [doc['id']] + list(theta[i]) + [text]
            writer.writerow(row)
    sys.stderr.write("Wrote {}\n".format(document_topics_file))


def convert_segan(modeldir, docfile, vocabfile, word_topics_file, docinfo_file):
    
    # Read in original documents, vocabulary file, and document IDs for the documents that were included in the modeling
    # (Noting that for segan some documents are excluded on import, e.g. if document is empty because all tokens were stopwords)
    with open(docfile) as f:
        # docs_df = pd.read_csv(docfile, sep=',', encoding='utf-8', engine='python', warn_bad_lines=True, error_bad_lines=False)
        docs_df = pd.read_csv(docfile, sep=',', encoding='utf-8', engine='python', on_bad_lines='warn')
    with open(vocabfile) as f:
        vocab_list = [s.rstrip() for s in f.readlines()]
    with open(docinfo_file) as f:
        docid_list = [s.rstrip() for s in f.readlines()]
        
    # Load phi file (topic-word distributions) 
    #   - Calling it beta below for consistency with scholar
    #   - Skipping first row (which is number of topics)
    #   - Dropping first column (which is size of vocabulary, repeated in each row)
    #     See https://stackoverflow.com/questions/13411544/delete-column-from-pandas-dataframe
    # transpose to get word-topic matrix,
    # convert to a dataframe with 'Word' as the first column,
    # output to CSV file.
    #
    # beta_df       = pd.read_csv(os.path.join(modeldir,'phis.txt'), sep='\t', encoding='utf-8', engine='python', header=None, skiprows=[0],
    #                         warn_bad_lines=True, error_bad_lines=False)
    beta_df       = pd.read_csv(os.path.join(modeldir,'phis.txt'), sep='\t', encoding='utf-8', engine='python', header=None, skiprows=[0], on_bad_lines='warn')

    beta_distrib  = beta_df.drop(beta_df.columns[[0]], axis=1).to_numpy()
    betaT         = np.transpose(beta_distrib)
    V, K          = betaT.shape
    labels        = ["Topic {}".format(str(i+1)) for i in range(K)]
    betaT_df      = pd.DataFrame(betaT, columns = labels)
    betaT_df.insert(0, 'Word', vocab_list)
    betaT_df.to_csv(word_topics_file, index=False)
    sys.stderr.write("Wrote {}\n".format(word_topics_file))

    # Load theta (document-topic proportions) matrix
    # Skip first row (number of documents included), remove first column (number of topics, repeated each row)
    # Add column names to dataframe and insert docID column with document IDs for docs that were included in the model
    # Merge/join topic posteriors (theta_df) with the text documents themselves (docs_df)
    # See https://stackoverflow.com/questions/64385747/valueerror-you-are-trying-to-merge-on-object-and-int64-columns-when-use-pandas
    #  for use of astype(str), which ensures that docID column is interpreted as a string for purposes of the merge (join) in both dfs.
    #
    # theta_df         = pd.read_csv(os.path.join(modeldir,'thetas.txt'), sep='\t', encoding='utf-8', engine='python', header=None, skiprows=[0],
    #                          warn_bad_lines=True, error_bad_lines=False)
    theta_df         = pd.read_csv(os.path.join(modeldir,'thetas.txt'), sep='\t', encoding='utf-8', engine='python', header=None, skiprows=[0], on_bad_lines='warn')
    theta_df         = theta_df.drop(beta_df.columns[[0]], axis=1)
    theta_df.columns = labels
    theta_df.insert(0, 'docID', docid_list)
    theta_df['docID'] = theta_df['docID'].astype(str)
    docs_df['docID']  = docs_df['docID'].astype(str)
    theta_merged_df   = pd.merge(theta_df, docs_df, on='docID')
    n_docs, _         = theta_merged_df.shape
    theta_merged_df.to_csv(document_topics_file, index=False)
    sys.stderr.write("Wrote {}\n".format(document_topics_file))
    

#  Example for Mallet:
#    python model2csv.py
#    --package   mallet
#    --docfile   /path/to/preprocessed_documents.txt
#    --modeldir  /path/to/mallet_model_output/
#    --vocabfile /path/to/mallet_model_output/model.word-topic-counts
#    --modelname fold_0.k25

def convert_mallet(modeldir, docfile, vocabfile, word_topics_file, document_topics_file, modelname):
    
    # Read in original documents (mallet format is docID<tab>label<tab>text)
    # We only want the docID and text columns, hence usecols.
    sys.stderr.write("Reading {}\n".format(docfile))
    with open(docfile) as f:
        # docs_df = pd.read_csv(docfile, sep='\t', encoding='utf-8', engine='python', usecols = [0,2],
        #                          names=['docID','label','text'], warn_bad_lines=True, error_bad_lines=False)
        docs_df = pd.read_csv(docfile, sep='\t', encoding='utf-8', engine='python', usecols = [0,2],
                                  names=['docID','label','text'], on_bad_lines='warn')

    # Read in vocabulary file (the word-topic-counts file contains word in second space-separated column)
    sys.stderr.write("Reading {}\n".format(vocabfile))
    with open(vocabfile) as f:
        vocab_lines = [s.split()[1] for s in f.readlines()]

    # Read topic-word weights file
    #   - Calling it beta below for consistency with scholar
    #   - Per ParallelTopicModel.java, the mallet file has an unnormalized weight for every word in every topic,
    #     and most of these will be equal to the smoothing parameter beta (see function printTopicWordWeights)
    # Normalize and turn these into columns of word-topic matrix
    # where vocabulary ('Word') is the first column, topics are columns; then
    # output to CSV file.
    sys.stderr.write("Creating {}\n".format(word_topics_file))
    betaT_df       = pd.DataFrame(vocab_lines, columns = ['Word'])
    sys.stderr.write("Reading topic-word weights.\n")
    betaT_df       = pd.DataFrame(vocab_lines, columns = ['Word'])
    # beta_input_df  = pd.read_csv(os.path.join(modeldir, modelname + '.topic-word-weights'), sep='\t', encoding='utf-8', engine='python', header=None, 
    #                          names = ['topicnum', 'word', 'weight'], warn_bad_lines=True, error_bad_lines=False)
    beta_input_df  = pd.read_csv(os.path.join(modeldir, modelname + '.topic-word-weights'), sep='\t', encoding='utf-8', engine='python', header=None, 
                              names = ['topicnum', 'word', 'weight'], on_bad_lines='warn')

    groups         = beta_input_df.groupby('topicnum')
    for topicnum, group_df in tqdm(groups):
        weights = group_df['weight'].values
        total   = weights.sum()
        probs   = weights / total
        # print("DEBUG: weights has length {}, probs has length {}, betaT_df is...".format(len(weights),len(probs)))
        # print(betaT_df)
        betaT_df.loc[:,"Topic {}".format(topicnum+1)] = probs  # https://re-thought.com/how-to-add-new-columns-in-a-dataframe-in-pandas/
    betaT_df.to_csv(word_topics_file, index=False)
    sys.stderr.write("Wrote {}\n".format(word_topics_file))
    
    # Load theta (document-topic proportions) matrix
    # Drop document number column
    # Output to CSV file
    sys.stderr.write("Creating {}\n".format(document_topics_file))
    cols             = ['docnum','docID'] + betaT_df.columns.values.tolist()[1:]
    # theta_df         = pd.read_csv(os.path.join(modeldir,modelname + '.doc-topics'), sep='\t', encoding='utf-8', engine='python', header=None,
    #                                   names=cols, warn_bad_lines=True, error_bad_lines=False)
    theta_df         = pd.read_csv(os.path.join(modeldir,modelname + '.doc-topics'), sep='\t', encoding='utf-8', engine='python', header=None,
                                      names=cols, on_bad_lines='warn')

    theta_df         = theta_df.drop(theta_df.columns[[0]], axis=1)
    theta_merged_df  = pd.merge(theta_df, docs_df, on='docID')
    theta_merged_df.to_csv(document_topics_file, index=False)
    sys.stderr.write("Wrote {}\n".format(document_topics_file))

    
# Handle command line
parser = argparse.ArgumentParser(description='Converts topic model output into a uniform format using CSV files')
parser.add_argument('-p','--package',
                        help='Topic model package: scholar, mallet, segan',                        dest='package',      default='scholar')
parser.add_argument('-m','--modeldir',
                        help='Directory containing model output',                                  dest='modeldir',     default=None)
parser.add_argument('-d','--docfile',
                        help='File containing input documents',                                    dest='docfile',      default=None)
parser.add_argument('-v','--vocabfile',
                        help='File containing vocabulary',                                         dest='vocabfile',    default=None)
parser.add_argument('-i','--docinfo',
                        help='Docinfo file containing docIDs (segan only)',                        dest='docinfo_file', default=None)
parser.add_argument('-M','--modelname',
                        help='Name of model, M, where M.model is the output-model (mallet only)',  dest='modelname',    default='mallet')
parser.add_argument('-w','--word_topics_file',
                        help='Output CSV file for topic-words distribution',  dest='word_topics_file',     default="word_topics.csv")
parser.add_argument('-D','--document_topics_file',
                        help='Output CSV filefor doc-topics distribution',    dest='document_topics_file', default="document_topics.csv")
args = vars(parser.parse_args())
if args['modeldir'] is None  or args['docfile'] is None  or args['vocabfile'] is None:
    parser.error('Required arguments: --modeldir, --docfile, --vocabfile. Use -h to see detailed usage info.')

package              = args['package']
modeldir             = args['modeldir']
docfile              = args['docfile']
vocabfile            = args['vocabfile']
docinfo_file         = args['docinfo_file']
modelname            = args['modelname']
word_topics_file     = args['word_topics_file']
document_topics_file = args['document_topics_file']


# Convert according to package
if (package == 'scholar'):
    convert_scholar(modeldir, docfile, vocabfile, word_topics_file)
elif (package == 'segan'):
    convert_segan(modeldir, docfile, vocabfile, word_topics_file, docinfo_file)
elif (package == 'mallet'):
    convert_mallet(modeldir, docfile, vocabfile, word_topics_file, document_topics_file, modelname)
else:
    sys.stderr.write("Not yet handling package '{}'\n".format(package))
