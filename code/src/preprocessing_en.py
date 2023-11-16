###################################################################################################
# Usage: python preprocessing.py 
#         --stoplist   stoplist.txt
#         --infile     in.txt
#         --emptyline  "output to use if line is empty, default is blank line"
#         --model      "en_core_web_sm"
#
# Preprocessing that tokenizes and applies a stoplist and lowercases,
# and  also identifies and appends phrases to the tokenized text.
#
# Input in --infile: one string per line
#
#  Output to stdout: 
#    Same as input but with texts converted to tokens + phrases
#
#  Example:
#    Input:  This is a really big test of the amazing system written by John Smith and his dog
#    Output: really big test amazing system written john smith dog really_big_test amazing_system john_smith
#
#  This code was designed for English.The commandline arguments do now allow
#  providing a non-English stoplist and spaCy model, which will permit tokenization for
#  other languages, but note that the tokenization subroutines in phrase_tokenization_subs
#  make English-specific assumptions, in particular about the structure of noun phrases.
#
#  For information on how to load spaCy models, see https://spacy.io/models.
#  For example: to download the Spanish es_core_news_sm model:
#     python -m spacy download es_core_news_sm
#
###################################################################################################
# Next line can be deleted if you prefer normal python error traceback
# from traceback_with_variables import activate_by_import
import argparse
import codecs
import sys
import spacy
import io
from phrase_tokenization_subs import *

# Hardwiring max phrase size
max_chunk_length = 3

# Making stderr unbuffered for progress count 
# https://stackoverflow.com/questions/107705/disable-output-buffering/14729823
sys.stderr = io.TextIOWrapper(open(sys.stderr.fileno(), 'wb', 0), write_through=True)


if __name__ == '__main__':

    # Handle command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--stoplist',   dest='stoplist', default=None,
                        help='stopwords or stop phrases, one per line')
    parser.add_argument('--infile',     dest='infile',   default=None,
                        help='input file (ID<tab>text one per line) [required]')
    parser.add_argument('--emptyline',  dest='emptyline', default=None,
                        help='stopwords or stop phrases, one per line')
    parser.add_argument('--model',      dest='model', default="en_core_web_sm",
                        help='spaCy model to use')

    args = parser.parse_args()

    if args.infile is None:
        print("Missing required --infile argument")
        sys.exit(1)
    else:
        infile = args.infile
        
    if args.stoplist is not None:
        stoplist = load_wordlist(args.stoplist)
    else:
        stoplist = set()

    if args.model is not None:
        model = args.model
    else:
        model = "en_core_web_sm"

    # Initialize spacy
    nlp = spacy.load(model)

    # Main loop through input lines, output going to stdout
    count = 0
    with codecs.open(infile, 'r', encoding='utf-8', errors='ignore') as fp:
        for line in fp:
            count = count + 1
            if (count % 100) == 0:
                sys.stderr.write("{} ".format(count))
            if (count % 1000) == 0:
                sys.stderr.write("\n".format(count))
            terms = tokenize_string_adding_phrases(nlp, line, stoplist, max_chunk_length)
            if len(terms) > 0:
                print(" ".join(terms))
            elif args.emptyline is not None:
                print("{}".format(args.emptyline))
            else:
                print("")
            


    




