###########################################################################################################
#
# python topwords.py
#
# User-friendly way to look at LDA topic-words distributions: as clouds
#
# Example: python topwords.py --outdir . --pdf_name clouds.pdf --word_topics_file word_topics.csv
#
#   -o OUTDIR, --outdir OUTDIR
#       Directory to contain cloud PDF file
#   -p PDF_NAME, --pdf_name PDF_NAME
#        Name for cloud PDF file
#   -i WORD_TOPICS_FILE, --word_topics_file WORD_TOPICS_FILE
#        CSV file with topic-word distribution
#        Columns: Word, Pr(word|topic1), ..., Pr(word|topic)
#   -n NUMWORDS, --numwords NUMWORDS
#        Number of words to show in clouds
#
###########################################################################################################
import os
import sys
import argparse
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from tqdm import tqdm

# Hardwire how many top words to show for each topic
N = 30


# Generate topic cloud PDF files, one per topic
def generate_topic_cloud_frequencies(sorted_df, label, cloudN):
    
    # Get top cloudN rows by value for the relevant column (label)
    # Note: nlargest would work just as well with unsorted dataframe df
    df_top_rows = sorted_df.nlargest(cloudN,label)
    
    # Convert to a dictionary and return
    freqs = dict(zip(df_top_rows['Word'],df_top_rows[label]))
    return(freqs)

# Argument: dict with word:probability (or word:frequency) pairs    
# https://github.com/amueller/word_cloud/blob/master/wordcloud/wordcloud.py#L150
#  To create a word cloud with a single color, use
#  ``color_func=lambda *args, **kwargs: "white"``.
#  The single color can also be specified using RGB code. For example
#  ``color_func=lambda *args, **kwargs: (255,0,0)`` sets color to red.
# Use plt.show() rather than plt.savefig to display figure on screen
# Use "foo.png" instead of "foo.pdf" to generate PNG file
def generate_topic_cloud_image(freq_pairs, outfile_name):
    wordcloud = WordCloud(max_words=2000,
                          background_color="White",
                          prefer_horizontal=1,
                          relative_scaling=0.75,
                          max_font_size=60,
                          random_state=13)
    wordcloud.generate_from_frequencies(freq_pairs)
    # color_func=lambda *args, **kwargs:(100,100,100) # gray
    color_func=lambda *args, **kwargs:(0,126,157) 
    wordcloud.recolor(color_func=color_func, random_state=3)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(outfile_name,bbox_inches='tight')

def write_pdf_with_title(titlestring, pdf_in, pdf_out):
    # https://stackoverflow.com/questions/1180115/add-text-to-existing-pdf-using-python
    # https://stackoverflow.com/questions/9855445/how-to-change-text-font-color-in-reportlab-pdfgen
    from PyPDF2 import PdfFileWriter, PdfFileReader
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFillColorRGB(0,0,1) #choose your font colour
    can.setFont("Helvetica", 20) #choose your font type and font size
    can.drawString(10, 10, titlestring)
    can.save()
    #move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(open(pdf_in, "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    outputStream = open(pdf_out, "wb")
    output.write(outputStream)
    outputStream.close()
    
def combine_pdfs(pdfs, outfile_name):
    # Solution to merging PDFs into a multi-page PDF document
    # https://stackoverflow.com/questions/3444645/merge-pdf-files
    from PyPDF2 import PdfFileMerger
    merger = PdfFileMerger()
    sys.stderr.write("Merging clouds into {}\n".format(outfile_name))
    for pdf in tqdm(pdfs):
        merger.append(pdf)
    merger.write(outfile_name)
    merger.close()

def combine_pdf_ALTERNATIVE(pdfs, outfile_name):
    # Another solution to merging PDFs into a multi-page PDF document
    # https://kittaiwong.wordpress.com/2020/09/03/how-to-merge-pdf-files-with-python-pypdf2/
    from PyPDF2 import PdfFileReader, PdfFileWriter
    pdf_writer = PdfFileWriter()
    for path in pdfs:
        pdf_reader = PdfFileReader(path, strict=False)
        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))
            if page == 0:
                pdf_writer.addBookmark(os.path.basename(path), pdf_writer.getNumPages()-1, parent=None)
    resultPdf = open(outfile_name, 'wb')
    pdf_writer.write(resultPdf)
    resultPdf.close()
    
################################################################
# Main
################################################################    


parser = argparse.ArgumentParser(description='Generates top-words text file and PDFs from document-topics CSV file')
parser.add_argument('-o','--outdir',
                        help='Directory to contain output [.]',                            dest='outdir',     default=".")
parser.add_argument('-p','--pdf_name',
                        help='Name cloud PDF file [clouds.pdf]',                           dest='pdf_name',   default="clouds.pdf")
parser.add_argument('-i','--word_topics_file',
                        help='CSV file with topic-word distribution [word_topics.csv]',    dest='word_topics_file', default="word_topics.csv")
parser.add_argument('-n','--numwords',
                        help='Number of words to show in clouds [100]',                    dest='numwords',   default=100)

args = vars(parser.parse_args())

outdir           = args['outdir']
pdf_name         = args['pdf_name']
word_topics_file = args['word_topics_file']
numwords         = int(args['numwords'])

# Path to cloud PDF file
pdf_outfile = outdir + "/" + pdf_name

# Read CSV file into DataFrame df
df = pd.read_csv(word_topics_file)

# Get theme labels
labels = list(df.columns.values)
pdfs   = []

# Generate topic cloud PDF file for each theme
sys.stderr.write("Creating cloud PDFs\n")
for label in tqdm(labels):

    # Temporary files
    image_file_name  = outdir + "/" + label.replace(" ", "_") + ".pdf"
    temp_file_name   = outdir + "/" + "TEMP_" + label.replace(" ", "_") + ".pdf"

    # For each theme label, sort descending and report top N words to stdout
    if label == 'Word':
        continue
    sorted_df = df.sort_values(by = label, ascending = False)
    words    = sorted_df['Word'].tolist()
    topwords = words[:N]

    # Not bothering to print topwords 
    # print(label + "\t" + " ".join(topwords))

    # Generate image to temporary PDF file.
    # Skip topic if generate an image for it has problems. (Debug in future!)
    freqs           = generate_topic_cloud_frequencies(sorted_df, label, numwords)
    try:
        # Create image file with cloud
        # sys.stderr.write("Creating cloud image for {} in {}.\n".format(label,temp_file_name))
        generate_topic_cloud_image(freqs, temp_file_name)

        # Create PDF file with topic label, and then remove temporary file
        write_pdf_with_title(label, temp_file_name, image_file_name)
        pdfs.append(image_file_name)
        os.remove(temp_file_name)        

    except Exception as e:
        sys.stderr.write("Error: {}".format(e))
        sys.stderr.write("Unable to create cloud image for {} from {} in {}. Skipping.\n".format(label,temp_file_name,image_file_name))


# Combine into one PDF
combine_pdfs(pdfs, pdf_outfile)

# Clean up temporary files for the individual cloud images
for label in labels:
    if label == 'Word':
        continue
    image_file_name  = outdir + "/" + label.replace(" ", "_") + ".pdf"
    # sys.stderr.write("Removing {}\n".format(image_file_name))
    os.remove(image_file_name)

# sys.stderr.write("Theme clouds are in {}\n".format(pdf_outfile))



