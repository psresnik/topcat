#!/usr/bin/env python3
"""
Full TOPCAT pipeline implementation for fresh user test
"""

import os
import sys
import subprocess
import time

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return None

def main():
    print("🚀 Starting Full TOPCAT Pipeline")
    print("=" * 50)
    
    # Configuration
    MALLET_BIN = "/Users/resnik/Misc/projects/topcat/github/fresh_user_test/mallet-2.0.8/bin"
    TOPCAT_SRC = "/Users/resnik/Misc/projects/topcat/github/code/src"
    RAW_DOCS = "data/modeling/comments1088_raw.txt"
    STOPLIST = "/Users/resnik/Misc/projects/topcat/github/fresh_user_test/mallet-2.0.8/stoplists/en.txt"
    GRANULARITIES = [10, 20, 30]
    NUM_ITERATIONS = 1000
    SEED = 13
    
    # For each granularity, run the topic modeling pipeline
    for num_topics in GRANULARITIES:
        print(f"\n📊 Processing {num_topics} topics")
        print("-" * 30)
        
        # Set up directories
        model_dir = f"data/modeling/model_k{num_topics}"
        curation_dir = f"{model_dir}/curation"
        mallet_outdir = f"{model_dir}/mallet_output"
        preprocessed_docs = f"{model_dir}/preprocessed.txt"
        
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(curation_dir, exist_ok=True)
        os.makedirs(mallet_outdir, exist_ok=True)
        
        # Run MALLET topic modeling
        run_mallet_cmd = f"""
python {TOPCAT_SRC}/run_mallet.py \\
    --package mallet \\
    --mallet_bin {MALLET_BIN} \\
    --preprocessing {TOPCAT_SRC}/preprocessing_en.py \\
    --stoplist {STOPLIST} \\
    --modelname comments1088 \\
    --raw_docs {RAW_DOCS} \\
    --preprocessed_docs {preprocessed_docs} \\
    --workdir data/modeling \\
    --modeldir {mallet_outdir} \\
    --model2csv {TOPCAT_SRC}/model2csv.py \\
    --word_topics_file {curation_dir}/word_topics.csv \\
    --document_topics_file {curation_dir}/document_topics.csv \\
    --numtopics {num_topics} \\
    --numiterations {NUM_ITERATIONS} \\
    --extra_args "--random-seed {SEED}"
"""
        
        result = run_command(run_mallet_cmd, f"MALLET topic modeling (K={num_topics})")
        if not result:
            print(f"❌ Failed at K={num_topics}, continuing to next...")
            continue
            
        print(f"✅ Topic modeling complete for K={num_topics}")
        
        # Check outputs
        word_topics = f"{curation_dir}/word_topics.csv"
        doc_topics = f"{curation_dir}/document_topics.csv"
        
        if os.path.exists(word_topics) and os.path.exists(doc_topics):
            print(f"📄 Created files:")
            print(f"  - {word_topics}")
            print(f"  - {doc_topics}")
        else:
            print(f"⚠️  Warning: Expected output files not found for K={num_topics}")
    
    print(f"\n🎉 Full pipeline complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()