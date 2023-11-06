##########################################################################################
#  python csv_clean_lines.py < stdin > stdout
#
#   Converts within-field whitespace to a single space,
#   including taking care of newlines embedded in CSV fields
#
#   Note: if input CSV looks like a single line with control characters as line
#   separators, it's probably using Windows encoding for line endings. To convert
#   to Linux with one CSV row per text line:
#
#    perl -pi -e 's/\r/\n/g' FILE.csv
#
#   This will destructively change the newlines in FILE.csv. 
##########################################################################################
import csv
import sys
import re

out    = csv.writer(sys.stdout)
reader = csv.reader(sys.stdin, dialect="excel")

try:
    for row in reader:
        output_columns = [re.sub(r"\s+"," ",col) for col in row]
        out.writerow(output_columns)
except csv.Error as e:
    sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))
        
