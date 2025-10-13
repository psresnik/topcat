#!/usr/bin/env python3
"""Simple preprocessing for TOPCAT without dependencies"""
import re
import sys

def simple_preprocess(input_file, output_file):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for i, line in enumerate(f_in):
            line = line.strip()
            if line:
                # Simple preprocessing - lowercase and basic tokenization
                words = re.findall(r'\b\w+\b', line.lower())
                # Remove very short words and numbers
                words = [w for w in words if len(w) > 2 and not w.isdigit()]
                if words:
                    # Format for MALLET: doc_id<TAB>label<TAB>text
                    f_out.write(f'doc{i:04d}\tlabel\t{" ".join(words)}\n')

if __name__ == "__main__":
    simple_preprocess('data/modeling/comments1088_raw.txt', 'data/modeling/simple_preprocessed.txt')
    print("✅ Simple preprocessing complete")