##################################################################################
# Preprocessing
#
#  Tokenizes, applies stoplist, lowercases
#  Appends multi_word_phrases to the non-stoplist unigram tokens
#
#  Usage example:
#
#    # Initialize
#    nlp           = spacy.load("en_core_web_sm")
#    stoplist      = load_wordlist("stoplist.txt")
#
#    # Optionally include a list of already-known phrases (one per line in input file)
#    known_phrases    = load_wordlist("known_phrases.txt")
#    phrase_tokenizer = initialize_known_phrase_tokenization(known_phrases)
#
#    input_string  = "This is a test of the emergency broadcast system, I think!"
#    terms         = tokenize_string_adding_phrases(nlp, input_string, stoplist, 3, phrase_tokenizer)
#    tok_string    = (" ".join(terms))
#
##################################################################################
import codecs
import re


# Create set of terms from filename, assuming one term per line
# For multi-word inputs, term is created by joining using underscores
# (e.g. "a lot" becomes a_lot)
def load_wordlist(filename):
    with codecs.open(filename, 'r', encoding='ascii', errors='ignore') as fp:
        linelist = fp.read().split('\n')
    linelist = [s.lower().replace(" ","_") for s in linelist]
    return set(linelist)

# Takes list of chunks from spacy NP chunker, maximum phrase length, stoplist
# Strips stopwords at start of each phrase (e.g. strings of determiners).
# Returns resulting phrases in lowercase that are at most maxn words long
# (after removing leading stoplist words like determiners, e.g. a_small_dog
# becomes small_dog)
def normalize_phrases(chunks,maxn,stoplist):
    result = []
    for phrase in chunks:
        tokenlist = [token.lower() for token in phrase.text.split()]
        while len(tokenlist) > 0:
            if tokenlist[0] not in stoplist:
                break
            tokenlist.pop(0)
        if len(tokenlist) > 1 and len(tokenlist) <= maxn:
            result.append("_".join(tokenlist))
    return result

# Given input_string, returns list of tokens, list of phrases 
# First argument nlp is an already-initialized spaCy nlp object
def extract_tokens_and_phrases(nlp, input_string, stoplist, max_chunk_length):
    analysis    = nlp(input_string)
    tokenlist   = [token.lower_ for token in analysis if re.search('[^\s_]', token.orth_) is not None]
    entities    = [entity.text.lower().split() for entity in analysis.ents
                    if entity.label_ in ['PERSON','FACILITY','GPE','LOC'] and re.search('[^\s_]', entity.text) is not None]
    entitylist  = ['_'.join(e) for e in entities if len(e) > 1]
    chunklist   = normalize_phrases(analysis.noun_chunks,max_chunk_length,stoplist)
    phraselist  = chunklist + [e for e in entitylist if e not in chunklist]
    return tokenlist, phraselist

# Returns true if token fits rules for filtering tokens out
# Filters
#  - strings in stoplist
#  - strings containing a non-alphanumeric character other than hyphen or underscore
#  - strings that are entirely numeric
#
# 2020-08-13 Saving info about latest change so it's easy to undo if necessary
#    -#  - strings with a non-alphanumeric character 
#    +#  - strings containing a non-alphanumeric character other than hyphen or underscore
#     #  - strings that are entirely numeric
#     def filter_token(token,stoplist):
#         return (token in stoplist
#    -            or re.search('[^\w_]', token) is not None
#    -            or re.search('[^\d]',  token) is None)
#    +            or re.search('[^\w_\-]', token) is not None
#    +            or re.search('[^\d]',  token) is None
#    +            or token == '-'
#    +            or token == '_'
#    +    )
def filter_token(token,stoplist):
    return (token in stoplist
            or re.search('[^\w_\-]', token) is not None
            or re.search('[^\d]',  token) is None
            or token == '-'
            or token == '_'
    )


# Initialization for tokenize_known_phrases()
# Argument is a list of known phrases, either space- or underscore-separated strings.
# Initializes NLTK tokenizer and add known multi-word expressions.
# For useful discussion about putting the import inside the initialization function, see
# https://stackoverflow.com/questions/128478/should-import-statements-always-be-at-the-top-of-a-module
def initialize_known_phrase_tokenization(phrases):
    from nltk.tokenize import MWETokenizer 
    tokenizer = MWETokenizer()
    for phrase in phrases:
        if (phrase):
            phrase_as_list = phrase.replace("_"," ").split()
            tokenizer.add_mwe(phrase_as_list)
    return tokenizer

# Requires first having called intialize_known_phrase_tokenization(list_of_known_phrases)
# Given initialized NLTK MWETokenizer and space-separated tokens,
# return string where multi-word expressions have been tokenized with underscores
def tokenize_known_phrases(phrase_tokenizer, input_string):
    original_tokens      = input_string.lower().split()
    result_tokens        = phrase_tokenizer.tokenize(original_tokens)
    result_known_phrases = [tok for tok in result_tokens if re.search('_',tok)]
    result_string        = " ".join(result_tokens)
    return result_string, result_known_phrases

# Given spaCy nlp object, input string, stoplist (as a set), and maximum phrase length
# returns a token list that contains tokens and, appended at the end, phrasal tokens
def tokenize_string_adding_phrases(nlp, input_string, stoplist, max_chunk_length, phrase_tokenizer=None):
    tokens, phrases = extract_tokens_and_phrases(nlp, input_string, stoplist, max_chunk_length)
    terms           = tokens + phrases
    if (phrase_tokenizer):
        _, known_phrases   = tokenize_known_phrases(phrase_tokenizer, input_string) 
        terms              = terms + [p for p in known_phrases if p not in phrases]
    filtered_terms         = [t for t in terms if not filter_token(t,stoplist)]
    return filtered_terms
