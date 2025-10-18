# Topic-Oriented Protocol for Content Analysis of Text (TOPCAT)

## Table of Contents

<!--

- [Citation](#citation)
- [Overview](#overview)
-->

- [The software](#the-software)
  - [Installing MALLET](#installing-mallet)
  - [Installing the TOPCAT software](#installing-the-topcat-software)
  - [Parameters you'll need to edit](#parameters-youll-need-to-edit)
  - [Parameters you shouldn't need to edit](#parameters-you-shouldnt-need-to-edit)
  - [Running the driver](#running-the-driver)
  - [What the driver produces](#what-the-driver-produces)
  - [Example run](#example-run)
- [The human process](#the-human-process)
  - [Selecting a model as the starting point for human curation](#selecting-a-model-as-the-starting-point-for-human-curation)
  - [Curating the model to build a coding scheme](#curating-the-model-to-build-a-coding-scheme)
  - [Obtaining representative documents ("verbatims") for a code](#obtaining-representative-documents-verbatims-for-a-code)
- [Guidance on topic model granularity](#guidance-on-topic-model-granularity)

<!--
 ## Citation
 
  If you use TOPCAT, kindly make sure to cite the following in any reports, presentations, or publications:
 
 * Stub for citation
 
 ## Overview
 
  Qualitative content analysis (QCA) includes a body of techniques that researchers use in order to gain an understanding of the content in bodies of text. These techniques are applied   across a wide variety of use cases, including, for example, the analysis of open-ended survey responses, social media posts, or online reviews. A widely acknowledged problem with   QCA, however, is that its methods are extremely labor intensive. For example, open-ended text responses can be an incredibly valuable source of insight in survey research, providing   more nuance than traditional questions and revealing categories of response that were not originally expected, but survey researchers frequently avoid open-ends because the   analysis represents too great an investment of resources. And when dealing with large quantities of text data, traditional QCA on the full dataset is simply out of the question.
 
  Topic models such as Latent Dirichlet Allocation (LDA; [Blei et al. 2003](https://www.jmlr.org/papers/volume3/blei03a/blei03a.pdf)) were introduced in the early 2000s as an 
  automated method for discovery of categories in bodies of text, and these models are cost-effective, highly scalable, and transparent in terms of offering a clear understanding how the 
  underlying model works. However, the specifics of their use in practice are wildly variable and many practitioners are unsatisfied with their ability to produce sufficiently high quality results.
 
  TOPCAT is a (still-evolving) software-enabled process for combining the positive aspects of automated topic modeling with the benefits of manual content analysis. A variety of 
  human-centered processes have been built around topic modeling over the years (e.g. interactive topic models; CITE) but TOPCAT is the first to be designed entirely around the traditional 
  qualitative content analysis process with the goal of widespread utility for qual researchers.  With that in mind:
 
 * **TOPCAT has been validated.** See [CITATION] for a direct comparison of the TOPCAT process with traditional, fully manual qualitative content analysis. 
 
 * **TOPCAT's human curation protocol follows a typical qual paradigm.** The  analysts' role should feel pretty familiar for experienced qual researchers. (We thought of just calling this 
  Computer Assisted Content Analysis, but we didn't like the sound of the acronym!) The central part of the human process is designed to closely match traditional coding scheme 
  development, with the outcome of the process comprising a traditional coding scheme (a set of code labels and their descriptions) together with a first-pass automatic coding of the   dataset that can subsequently be refined manually if desired. (Higher quality automated coding is under development.)
 
 * **TOPCAT uses [MALLET](https://mimno.github.io/Mallet/index), the most mature and widely used topic modeling package.** An excellent set of instructions for installing   and running MALLET (both Mac and Windows), friendly to non-technical people, already exists [here](https://programminghistorian.org/en/lessons/topic-modeling-and-mallet).
 
 * **TOPCAT's software is straightforward to install and use for anyone who is capable of running a Python program.**  Currently for Mac, but instructions for Windows are coming. 
   - TOPCAT provides a Python driver (`code/driver.py`) that orchestrates the complete analysis workflow with a single command.
 
 * **TOPCAT does not require learning a new software interface.** Qualitative analysts need only be able to deal with PDF and Excel.
 
 * **TOPCAT is extensible.** The human curation protocol requires only a topic-word distribution and a document-topic distribution (the standard outputs of "vanilla" topic modeling   using LDA), either as CSV or .npy files. These should also be straightforward to obtain from other models such as the [Structural Topic Model](https://www.structuraltopicmodel.com/) or [short text topic models](https://stackoverflow.com/questions/62175452/topic-modeling-on-short-texts-python). 
--> 
 
 
## The software

### Installing MALLET

Follow the directions at Shawn Graham, Scott Weingart, and Ian Milligan, "Getting Started with Topic Modeling and MALLET," Programming Historian 1 (2012), 
[https://doi.org/10.46430/phen0017](https://doi.org/10.46430/phen0017).

### Installing the TOPCAT code

#### Prerequisites

Before installing TOPCAT, you need:

- **conda or miniconda**: If you don't have conda installed, install [miniconda](https://docs.conda.io/projects/miniconda/en/latest/index.html#quick-command-line-install) or full [anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html)

#### Installation Steps

**Step 1: Clone the repository**

```bash
git clone https://github.com/psresnik/topcat.git
cd topcat
```

**Step 2: Create conda environment**

```bash
# Create the topcat environment (includes all dependencies)
conda env create -f code/topcat.yml
```

**Step 3: Install spaCy language model**

```bash
# Activate the topcat environment and download English language model
conda activate topcat
python -m spacy download en_core_web_sm
```

**Step 4: Set up configuration**

```bash
# Copy the template configuration file
cp templates/config_template.ini config.ini

# Edit config.ini and update relevant variables for your system and analysis
```

Note that you can 

**Step 5: Validate installation**

```bash
# Activate the topcat environment and test that everything is working
conda activate topcat
python validate_installation.py
```

If you chose a name other than `config.ini` for your local, analysis-specific configuration file, you can call the validation code this way instead:

```bash
python validate_installation.py --config <your_config_file>
```

If validation passes, you're ready to use TOPCAT! 

### Configuration

TOPCAT uses a Python driver that reads parameters from a configuration file (default is `config.ini`). 

**Key parameters you'll typically need to edit:**

|Parameter|Description|
|-----------|-----------|
|`topcatdir`|Directory containing this TOPCAT repository|
|`malletdir`|Directory containing your MALLET installation|
|`rootdir`|Directory where analysis output files will be created|
|`csv`|Full path to your CSV file containing documents to analyze|
|`textcol`|Column number containing your text documents (1-indexed: first column = 1)|
|`modelname`|Name for your analysis (used in output filenames)|
|`granularities`|Space separated topic model sizes to try, e.g. `10 20 30`|

**Advanced parameters (usually don't need to change):**

|Parameter|Description|
|-----------|-----------|
|`stoplist`|Stopwords file (defaults to MALLET's English stoplist)|
|`numiterations`|MALLET training iterations (default: 1000)|
|`maxdocs`|Maximum documents per topic in curation materials (default: 100)|
|`seed`|Random seed for reproducible results (default: 13)|
|`debug`|Enable debug mode (default: false)|

For the `granularities` parameter, choose topic model sizes based on your dataset size. See [Guidance on Topic Model Granularity](#guidance-on-topic-model-granularity) below for recommendations.

**⚠️ Important Note about Re-running Analyses:**

When `debug = true` in your configuration file, TOPCAT will automatically overwrite existing model directories from previous runs. This allows for easy re-running during development and testing. However, be aware that:

- Re-running the same analysis will replace all previous results
- Each topic granularity (10, 20, 30, etc.) has separate directories, so they won't interfere with each other
- Consider setting `debug = false` to prevent accidental overwrites

### Running the driver

The TOPCAT pipeline performs the following steps:

* Extract and clean documents from your CSV file
* Apply NLP preprocessing with spaCy (tokenization, phrase detection, stopword removal)
* Train topic models using MALLET for each specified granularity
* Generate human curation materials (Excel files, PDF word clouds)

**To run TOPCAT:**

```bash
# Test your configuration first with dry-run mode
python code/driver.py --dry-run --config config.ini

# Run the full analysis
python code/driver.py --config config.ini
# or simply (config.ini is the default):
python code/driver.py
```

**What to expect:**

- Processing time: depends on dataset size and number of topics
- Progress indicators: You'll see preprocessing progress and MALLET progress updates
- Output: Files will be created in your configured output directory



### What the automatic processing produces

In the OUTDIR directory specified in the driver, you will find one subdirectory per granularity in GRANULARITIES. In each directory you will find the following three files to be used during the human curation process.

|Output file|Description|
|-----------|-----------|
|GRANULARITY_categories.xlsx| Top-words bar-chart and top documents for each topic|
|GRANULARITY_clouds.pdf| Cloud representation for each topic|
|GRANULARITY_alldocs.xlsx| Document-topic distribution with one document per row (in the `text` column)|

### Example run

In the `example` directory, you'll find a smaller (2K documents) dataset and a larger (10K documents) dataset sampled from [public comments](https://www.regulations.gov/docket/FDA-2021-N-1088) that were submitted to the U.S. Food and Drug Administration (FDA) in response to a 2021 [request for public comments](https://downloads.regulations.gov/FDA-2021-N-1088-0001/content.pdf) about emergency use authorization for a child COVID-19 vaccine.  Note that some comments can contain upsetting language.

(Some research using these broader public comments was published in Alexander Hoyle, Rupak Sarkar, Pranav Goel, and Philip Resnik. 2023. [Natural Language Decompositions of Implicit Content Enable Better Text Representations](https://aclanthology.org/2023.emnlp-main.815/). In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, pages 13188–13214, Singapore. Association for Computational Linguistics. However, note that neither of these datasets exactly match the data used in that paper.)


By default (as specified in `templates/config.ini` the configuration will run on the 10K dataset. You can also modify your config to use the 2K dataset instead.

**To run the example:**

```bash
python code/driver.py --config config.ini
# or simply (config.ini is the default):
python code/driver.py
```

This will process the example dataset and create topic models with granularities of 10, 20, and 30 topics (as specified in the default configuration).

**Expected outputs:**

- **Processing time**: ~5 minutes for the 10K example dataset on a 2021 M1 Mac
- **Output location**: In your configured output directory (default: `analysis/out/`)
- **Files created**: Excel files and PDF word clouds for human curation

**Validation**: You can compare your results with the reference output in the `example/` directory. Results won't be identical due to the randomness in topic modeling, but topic themes should be similar.

**Troubleshooting**: If you encounter issues, see [INSTALL_TROUBLESHOOTING.md](INSTALL_TROUBLESHOOTING.md) for solutions to common problems.

*Note: The original comments are publicly available [here](https://www.regulations.gov/document/FDA-2021-N-1088-0001). Some comments may contain upsetting language or content.* 

<!--
### Getting your data ready 
The code in this package assumes that the body of text your are analyzing is in a single CSV spreadsheet.  There should be a header row, and the header label for the column containing the items to be analyzed (which we uniformly refer to as "documents" throughout, following the conventions of topic modeling) is identified via the `TEXTCOL` parameter in the `config.ini` configuration file; for example, `TEXTCOL = text`.  

Optionally, the config file can specify a header label for a column with unique document IDs, e,g,. `TEXTCOL = docID`.  If the value for `TEXTCOL` is *NONE* (all caps) then the documents will automatically be given numerical ideas sequentially, i.e. 1, 2, 3, ...etc.

Text encodings are a common issue when working with spreadsheets. In general, if your text is in UTF-8 things should work fine.  If you encounter encoding issues, we recommend [iconv](https://en.wikipedia.org/wiki/Iconv) as a generally workable solution.  Often `iconv -f windows-1252 -t utf-8 -c < infile > outfile` works well for converting Windows-based spreadsheets, where the `-c` flag says to discard any non-convertible characters.-->

## The human process

### Selecting a model as the starting point for human curation

See [these instructions for model selection](instructions/model_selection.pdf).

### Curating the model to build a coding scheme

There are two steps in model curation. 

**Independent coding scheme creation**.  First, two independent analysts familiar with the subject matter (which we often refer to as subject matter experts or SMEs) go through the process for reviewing and labeling categories in [these instructions](instructions/topic_instructions.pdf). This can be viewed as having the SMEs *independently* engage in coding scheme/category creation guided by the bottom-up topic model analysis.

**Creating a consensus coding scheme**. Second, analysts look at the two independently-created sets of categories, following [these instructions](instructions/consensus_instructions.pdf) in order to arrive at a *consensus* set of categories.  These can be two other SMEs, or it can be the SMEs who worked independently in the previous step. (*Note: the consensus instructions have not yet been updated to be consistent with the most recent versions of file names, etc.)*

The end result of this curation process is a set of categories and descriptions that have been guided via an automatic, scalable process that is bottom-up and thus minimizes human bias, while still retaining human quality control. 

### Obtaining representative documents ("verbatims") for a code 

It is often useful to select a set of good examples for codes in a coding scheme. This is straightforward using the files already created by the TOPCAT process.  In the materials used for human curation, each automatically created topic was accompanied by a set of its "top" documents.  These can be considered a set of ranked candidates for verbatims for the code created using that topic.

<!--
### Coding the dataset  

The TOPCAT protocol is currently designed for high-quality, efficient development of a coding scheme, not for automatically coding documents. Automated coding is an active subject of current research, e.g. see:

* *Stub for references to automatic coding papers*

However, even without such fancier approaches the output of the TOPCAT process does give you a reasonable first approximation of automatic coding that is suitable for human review and correction, which should be much more efficient than coding from scratch. For example, you can do the following:

* The products of the human curation effort include: 
  - A *coding_scheme.xlsx* file that contains the coding scheme that was created via topic-driven human curation. This can be viewed as the starting point for a codebook. 

  - A version of the `alldocs.xlsx` spreadsheet in which the generic headers (*Topic 1*, *Topic 2*m, etc.) have been replaced by code labels from the coding scheme.

* Open both files in Excel. (Alternatively, you might find it convenient to print the coding scheme and keep it handy, and just open the all-documents spreadsheet.)

* Each column in the *alldocs* should match a corresponding row in the coding scheme.  

* For each column that was given a code in the coding schema (not *DISCARD* or marked as irrelevant):

  - Hide columns to the right of this one, up to but not including the `text` column containing the document text.

  - Sort the spreadsheet on this code's column in descending numeric order. The documents are now ranked by "goodness of fit" to the code.  (This is the same ranking used to select verbatims as discussed above.)

  - Add a new column to the right of that column, titled "Contains code LABEL" where *LABEL* is the code name/label.

  - Fill that entire column with the value 0 (meaning no, that item doesn't contain the code)

  - Proceed from the top row downward, changing 0 to 1 if the code applies to the document.  That will happen a lot toward the top (where the numbers are higher) and less often as you proceed down the column. 
  
  - Alternatively, you might want to first fill the first 100 values with 1 and change them to 0 when the code *doesn't* apply; then do the same thing for the next 100 items; etc. Because you've sorted by "how good" this code is for the items, the highest-up items are more likely to be good items for this code, and at some point you'll see that it makes more sense to switch from correcting 1's to 0's to starting with 0's and correcting to 1's.  

  - You are likely (certain!) to reach a point where you're assigning 1's very infrequently. In practice once you reach that point, it may make sense to move on to the next column, depending on your tolerance for false negatives.  
  
* Once this is done for all the codes, sort the spreadsheet by the `docID` column to put it back in the original order.  

Voila!  You now have a spreadsheet containing the text, and for each code, a column containing either 0 or 1 depending on whether that code applies to that text item.

*To consider: provide instructions for importing the model-based coding into NVivo for review/correction?*
-->

## Guidance on topic model granularity

Topic models require you to specify in advance the number of categories you would like to automatically create, which we will refer to as the *granularity* of the model; in the literature this value is conventionally referred to as *K*.  

The best granularity varies from analysis to analysis, and at present there are no fully reliable methods to optimize that number for any given collection of text (although we're working on that). For now, the TOPCAT approach involves running multiple models at different granularities and an efficient human-centered process for selecting which one is the best starting point for more detailed curation. 

We generally recommend creating three (or at most up to five) models with different granularities, and these are heuristics we generally follow (anecdotally consistent withg what we have heard from a number of other frequent topic model practitioners). 

* For a document collection with fewer than 500 documents, we would typically try K=5,10,15, though note that LDA may or may not produce anything of use at all for collections that small. 

* For 500-to-1000 documents (K=10,15,20 or 10,20,30)

* For 1000-to-10000 (K=15,20,40 or 20,30,50)

* For 10000- to-200000 (K=75,100,150)

These recommendations are anecdotally consistent with what we have heard from a number of other frequent topic model practitioners. Crucially, the human curation process reduces the burden to view any particular model size as optimal; in general we tend to err mildly on the side of more rather than fewer top- ics since our process permits less-good topics to be discarded and fine-grained topics can be merged under a single label and description. 
