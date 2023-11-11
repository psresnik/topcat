import configargparse
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm 


if __name__ == "__main__":
    parser = configargparse.ArgParser()
    parser.add('--topic_word',
               default='word_topics.csv',
               type=str,
               help='path to .csv file storing the word-topic info')
    parser.add('--doc_topic',
               default='document_topics.csv',
               type=str,
               help='path to .csv file storing the document-topic info')
    
    parser.add('--output',
               default='curation_inputs/',
               type=str,
               help='path to store the output files generated - that can serve as input to topic curation code')
    
    args = parser.parse_args()
    # create output directory if it does not exist
    Path(args.output).mkdir(parents=True, exist_ok=True)

    print("Reading topic-word and doc-topic CSVs")
    tw_df = pd.read_csv(args.topic_word)
    td_df = pd.read_csv(args.doc_topic)

    print("Writing topic_word.npy")
    np.save(Path(args.output) / 'topic_word.npy', 
            tw_df.iloc[:, 1:].to_numpy().T)

    print("Writing doc_topic.npy")
    np.save(Path(args.output) / 'doc_topic.npy', 
            td_df.iloc[:, 1:-1].to_numpy())

    print("Writing vocab.txt")
    vocab = list(tw_df['Word'])
    with open(Path(args.output) / 'vocab.txt', 'w') as vocab_f:
        for i, w in tqdm(enumerate(vocab)):
            vocab_f.write(str(w))
            if i < len(vocab) - 1:
                vocab_f.write('\n')

    print("Writing raw_documents.txt")
    docs = list(td_df['text'])
    with open(Path(args.output) / 'raw_documents.txt', 'w') as docs_f:
        for ind, text in tqdm(enumerate(docs)):
            docs_f.write(str(text))
            if ind < len(docs) - 1:
                docs_f.write('\n')
                
    print('Files created and saved.')
    
    
