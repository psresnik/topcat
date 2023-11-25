
<div id="toc"/>
# Topic-Oriented Protocol for Content Analysis of Text (TOPCAT)

<!-- To generate table of contents:
  pandoc -s --toc README.md -o foo.md

  Add <div id="NAME"/> as appearing in the TOC at top if needed
  Copy/paste the TOC here
-->




*   [Citation](#citation) 

*   [Overview](#overview)

*   [The software](#software)
	-	[Installing MALLET](#mallet)
	-	[Installing the TOPCAT software](#installing)
	-   [Parameters you'll need to edit](#parameters-edit)
	-   [Parameters you shouldn't need to edit](#parameters-noedit)
	-   [Running the driver](#driver)
	-   [What the driver produces](#outfiles)
	-   [Example run](#example)

*   [The human process](#human)
	-	[Selecting a model as the starting point for human curation](#model-selection)
	-	[Curating the model to build a coding scheme](#curating)
	-	[Obtaining representative documents ("verbatims") for a code](#verbatims)
	-	[Coding the dataset](#coding)

*	[Guidance on topic model granularity](#granularity)


<div id="citation"/>
## Citation

If you use TOPCAT, kindly make sure to cite the following in any reports, presentations, or publications:

* Stub for citation

[Return to top](#toc)

<div id="overview"/>
## Overview

Qualitative content analysis (QCA) includes a body of techniques that researchers use in order to gain an understanding of the content in bodies of text. These techniques are applied across a wide variety of use cases, including, for example, the analysis of open-ended survey responses, social media posts, or online reviews. A widely acknowledged problem with QCA, however, is that its methods are extremely labor intensive. For example, open-ended text responses can be an incredibly valuable source of insight in survey research, providing more nuance than traditional questions and revealing categories of response that were not originally expected, but survey researchers frequently avoid open-ends because the analysis represents too great an investment of resources. And when dealing with large quantities of text data, traditional QCA on the full dataset is simply out of the question.

Topic models such as Latent Dirichlet Allocation (LDA; [Blei et al. 2003](https://www.jmlr.org/papers/volume3/blei03a/blei03a.pdf)) were introduced in the early 2000s as an automated method for discovery of categories in bodies of text, and these models are cost-effective, highly scalable, and transparent in terms of offering a clear understanding how the underlying model works. However, the specifics of their use in practice are wildly variable and many practitioners are unsatisfied with their ability to produce sufficiently high quality results.

TOPCAT is a (still-evolving) software-enabled process for combining the positive aspects of automated topic modeling with the benefits of manual content analysis. A variety of human-centered processes have been built around topic modeling over the years (e.g. interactive topic models; CITE) but TOPCAT is the first to be designed entirely around the traditional qualitative content analysis process with the goal of widespread utility for qual researchers.  With that in mind:

* **TOPCAT has been validated.** See [CITATION] for a direct comparison of the TOPCAT process with traditional, fully manual qualitative content analysis. 

* **TOPCAT's human curation protocol follows a typical qual paradigm.** The  analysts' role should feel pretty familiar for experienced qual researchers. (We thought of just calling this Computer Assisted Content Analysis, but we didn't like the sound of the acronym!) The central part of the human process is designed to closely match traditional coding scheme development, with the outcome of the process comprising a traditional coding scheme (a set of code labels and their descriptions) together with a first-pass automatic coding of the dataset that can subsequently be refined manually if desired. (Higher quality automated coding is under development.)

* **TOPCAT uses [MALLET](https://mimno.github.io/Mallet/index), the most mature and widely used topic modeling package.** An excellent set of instructions for installing and running MALLET (both Mac and Windows), friendly to non-technical people, already exists [here](https://programminghistorian.org/en/lessons/topic-modeling-and-mallet).

* **TOPCAT's software is straightforward to install and use for anyone who is capable of running a Python program.**  Currently for Mac, but instructions for Windows are coming. 
  - At the moment, using TOPCAT involves running a top-level "driver" shell script. This will be converted to a top-level Python program that invokes the relevant pieces of software.

* **TOPCAT does not require learning a new software interface.** Qualitative analysts need only be able to deal with PDF and Excel.


* **TOPCAT is extensible.** The human curation protocol requires only a topic-word distribution and a document-topic distribution (the standard outputs of "vanilla" topic modeling using LDA), either as CSV or .npy files. These should also be straightforward to obtain from other models such as the [Structural Topic Model](https://www.structuraltopicmodel.com/) or [short text topic models](https://stackoverflow.com/questions/62175452/topic-modeling-on-short-texts-python). 

[Return to top](#toc)



<div id="software"/>
## The software


<div id="mallet"/>
### Installing MALLET

Follow the directions at Shawn Graham, Scott Weingart, and Ian Milligan, "Getting Started with Topic Modeling and MALLET," Programming Historian 1 (2012), [https://doi.org/10.46430/phen0017](https://doi.org/10.46430/phen0017).

[Return to top](#toc)


<div id="installing"/>
### Installing the TOPCAT software

 
* Installing the environment
	*  If you have `conda` already installed, you should be good to go. Skip this step.
	
	*  If not, we recommend that you install [miniconda](https://docs.conda.io/projects/miniconda/en/latest/index.html#quick-command-line-install) unless for other reasons you'd prefer to do a full [anaconda installation](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html)

* Installing TOPCAT
	* Do a `git clone` for this TOPCAT package

* Installing necessary packages
	* For reference, see the conda documentation on [Creating an environment from an environment.yml file](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file)
	
	* At the moment, we have two separate conda environments that need to be installed. These will be combined into just one when we make the move to a python driver. 
		* The `topics` package:
		
			* Edit the `prefix` variable at the end of [code/topics.yml](code/topics.yml) so that it points to wherever you want the `topics` environment to live

		
			* Excecute `conda env create -f code/topics.yml`

		* The `topic_curation` package:
		
			* Edit the `prefix` variable at the end of [code/topic_curation.yml](code/topic_curation.yml) so that it points to wherever you want the `topic_curation` environment to live
			
			* Execute `conda env create -f code/topic_curation.yml`

	* Finally, install the [csvfix](https://wlbr.de/csvfix/) package via [this git repository](https://github.com/wlbr/csvfix). 

[Return to top](#toc)



<div id="parameters-edit"/>
### Parameters you'll need to edit

Right now TOPCAT is driven by the `drivers.csh` shell script in the `code/src` directory. (It's `csh`, not `bash`, because I'm seriously old school. And yes, I already know `csh` is [widely reviled ](https://www.grymoire.com/Unix/CshTop10.txt)for shell scripting. But this particular script isn't all that fancy and it gets the job done.) 

Ultimately this driver will be rewritten as a python program that reads a `config.ini` configuration file, but for now parameters for the runs are established using environment variable assignments at the top of the script. That means you'll want a separate copy of the script for each dataset you analyze.

Here's a description of the variables you'll need to localize/customize and what they are for.

__Installation variables__

|Variable|Description|
|-----------|-----------|
|MALLETDIR|          Installed directory for MALLET (contains the MALLET `LICENSE` file)|
|TOPCATDIR|			 Directory with the TOPCAT package (contains this README.md file)
|PREPROC|            Full path to this package's NLP preprocessing script, e.g. `preprocessing_en.py` |
|RUNMALLET|          Full path to this package's Mallet driver, i.e. `run_mallet.py` |

__Analysis-specific variables__


|Variable|Description|
|-----------|-----------|
|ROOTDIR|            Your main directory for analysis of this specific dataset|
|CSV|                Full path to the input CSV file containing the documents|
|TEXTCOL|            Column number in the CSV file containing the documents (first column is numbered 0, not 1!) |
|MODELNAME|          Name to use for the models|
|DATADIR|            Directory software will create to contain topic modeling output|
|OUTDIR|             Directory software will create to contain the files to be used during human curation|
|GRANULARITIES|		 List of topic model sizes to try for potential starting-point models, e.g. `'(20 30 40)'`|

With regard to `GRANULARITIES`, the driver script iterates through several (typically three to five) choices of topic model size. This value is typically denoted K in the topic modeling literature. See the [_Guidance on Topic Model Granularity_](#granularity) discussion below for recommendations about what values to use, which depends on the dataset.  Note that the `csh` syntax is a little persnickety so when you edit that veriable, make sure you only change the numbers, not the parentheses or single-quotes.



<div id="parameters-noedit"/>
### Parameters you shouldn't need to edit

Finally, here's an explanation of some other variables that you shouldn't need to change.

|Variable|Description|
|-----------|-----------|
|STOPLIST|           Stoplist (words to ignore), one word per line (defaults to MALLET's stoplist)|
|NUMITERATIONS|      Number of iterations to run topic model (defaults to 1000)|
|RAWDOCS|            Name for intermediate file with raw documents to be created automatically from the CSV file|
|SEED|					 Random seed for MALLET runs (for reproducibility)

<div id="driver"/>
### Running the driver

The main flow in the driver is as follows:

* Extract and clean documents from the specified column in the CSV file
* Run run_mallet.py to build a topic model on NLP-preprocessed text for each value of NUMTOPICS
* For each model create the materials used in the TOPCAT human curation protocol 

To run the driver, simply execute `driver.csh` on the command line. 

Currently you may get some warnings but if things work properly the script should run all the way through. 

<div id="outfiles">
### What the driver produces

In the OUTDIR directory specified in the driver, you will find one subdirectory per granularity in GRANULARITIES. In each directory you will find the following three files to be used during the human curation process.

|Output file|Description|
|-----------|-----------|
|GRANULARITY_categories.xlsx| Top-words bar-chart and top documents for each topic|
|GRANULARITY_clouds.pdf| Cloud representation for each topic|
|GRANULARITY_alldocs.xlsx| Document-topic distribution with one document per row (in the `text` column)|

<div id="example">
### Example run

Assuming that you have installed everything and created a version of the driver file with variables appropriately edited, you can run topic modeling for the example dataset in `example` simply by executing 

`code/driver.csh` 

with no arguments. This will run through the topic modeling process for a sample of 2000 public comments (out of ~130,000) submitted to the U.S. Food and Drug Administration (FDA) in response to a 2021 request for public comments about emergency use authorization for a child COVID-19 vaccine. The original comments are publicly available [here](https://www.regulations.gov/document/FDA-2021-N-1088-0001) and [straightforward to download](https://www.regulations.gov/bulkdownload). Note that some comments can contain upsetting language or content.

After it runs to completion you will find the output files suitable for the human curation process in an `example/out` subdirectory. Intermediate modeling output (including the preprocessed version of the corpus) can be found in `example/data`.

To confirm that things have run successfully, you can compare your outputs with the output material in `example_out`. The output might not be identical, because topic modeling has an element of randomness and your results could vary on a different machine even if you're using the default random seed value. However, for eachy granularity your topic models and the example outputs provided with the package are expected to be substantially similar. 


<!--
### Getting your data ready 
The code in this package assumes that the body of text your are analyzing is in a single CSV spreadsheet.  There should be a header row, and the header label for the column containing the items to be analyzed (which we uniformly refer to as "documents" throughout, following the conventions of topic modeling) is identified via the `TEXTCOL` parameter in the `config.ini` configuration file; for example, `TEXTCOL = text`.  

Optionally, the config file can specify a header label for a column with unique document IDs, e,g,. `TEXTCOL = docID`.  If the value for `TEXTCOL` is *NONE* (all caps) then the documents will automatically be given numerical ideas sequentially, i.e. 1, 2, 3, ...etc.

Text encodings are a common issue when working with spreadsheets. In general, if your text is in UTF-8 things should work fine.  If you encounter encoding issues, we recommend [iconv](https://en.wikipedia.org/wiki/Iconv) as a generally workable solution.  Often `iconv -f windows-1252 -t utf-8 -c < infile > outfile` works well for converting Windows-based spreadsheets, where the `-c` flag says to discard any non-convertible characters.-->


[Return to top](#toc)


<div id="human"/>
## The human process


<div id="model-selection"/>
### Selecting a model as the starting point for human curation


See [these instructions for model selection](instructions/model_selection.pdf).

[Return to top](#toc)


<div id="curating"/>
### Curating the model to build a coding scheme

There are two steps in model curation. 

**Independent coding scheme creation**.  First, two independent analysts familiar with the subject matter (which we often refer to as subject matter experts or SMEs) go through the process for reviewing and labeling categories in [these instructions](instructions/topic_instructions.pdf). This can be viewed as having the SMEs *independently* engage in coding scheme/category creation guided by the bottom-up topic model analysis.

**Creating a consensus coding scheme**. Second, analysts look at the two independently-created sets of categories, following [these instructions](instructions/consensus_instructions.pdf) in order to arrive at a *consensus* set of categories.  These can be two other SMEs, or it can be the SMEs who worked independently in the previous step. (*Note: the consensus instructions have not yet been updated to be consistent with the most recent versions of file names, etc.)*

The end result of this curation process is a set of categories and descriptions that have been guided via an automatic, scalable process that is bottom-up and thus minimizes human bias, while still retaining human quality control. 

[Return to top](#toc)


<div id="verbatims"/>
### Obtaining representative documents ("verbatims") for a code 

It is often useful to select a set of good examples for codes in a coding scheme. This is straightforward using the files already created by the TOPCAT process.  In the materials used for human curation, each automatically created topic was accompanied by a set of its "top" documents.  These can be considered a set of ranked candidates for verbatims for the code created using that topic.

[Return to top](#toc)


<div id="coding"/>
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

[Return to top](#toc)



<div id="granularity"/>
## Guidance on topic model granularity

Topic models require you to specify in advance the number of categories you would like to automatically create, which we will refer to as the *granularity* of the model; in the literature this value is conventionally referred to as *K*.  

The best granularity varies from analysis to analysis, and at present there are no fully reliable methods to optimize that number for any given collection of text (although we're working on that). For now, the TOPCAT approach involves running multiple models at different granularities and an efficient human-centered process for selecting which one is the best starting point for more detailed curation. 

We generally recommend creating three (or at most up to five) models with different granularities, and these are heuristics we generally follow (anecdotally consistent withg what we have heard from a number of other frequent topic model practitioners). 

* For a document collection with fewer than 500 documents, we would typically try K=5,10,15, though note that LDA may or may not produce anything of use at all for collections that small. 

* For 500-to-1000 documents (K=10,15,20 or 10,20,30)

* For 1000-to-10000 (K=15,20,40 or 20,30,50)

* For 10000- to-200000 (K=75,100,150)

These recommendations are anecdotally consistent with what we have heard from a number of other frequent topic model practitioners. Crucially, the human curation process reduces the burden to view any particular model size as optimal; in general we tend to err mildly on the side of more rather than fewer top- ics since our process permits less-good topics to be discarded and fine-grained topics can be merged under a single label and description. 

[Return to top](#toc)
