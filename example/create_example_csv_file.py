import csv
import sys
################################################################
# Filters CSV file to first N rows where 'text' value
# has between min_len and max_len characters.
################################################################

def filter_csv_file(csv_file, num_lines, min_len, max_len):
    try:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.DictReader(file)
            
            output_lines = []
            for row in reader:
                text = row.get('text', '')
                text_length = len(text)
                if min_len <= text_length <= max_len:
                    output_lines.append(row)
                    if len(output_lines) == num_lines:
                        break

            if output_lines:
                writer = csv.DictWriter(sys.stdout, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(output_lines)
            else:
                print("No matching lines found in the CSV file.")
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python program.py <csv_file> <num_lines> <min_len> <max_len>")
        sys.exit(1)

    csv_file = sys.argv[1]
    num_lines = int(sys.argv[2])
    min_len = int(sys.argv[3])
    max_len = int(sys.argv[4])

    filter_csv_file(csv_file, num_lines, min_len, max_len)
