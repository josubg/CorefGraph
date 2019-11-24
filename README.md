*CorefGraph is an independent python module to perform coreference
resolution*, a Natural Language Processing task which consists of
determining the mentions that refer to the same entity in a text or
discourse. CorefGraph is a multilingual rule-based system loosely
based on the Stanford Multi Sieve Coreference System
[Stanford Multi Sieve Pass system (Lee et al., 2013)](http://www-nlp.stanford.edu/downloads/dcoref.shtml).
Currently it supports English and Spanish but it can be extended to other
languages.

**If you use corefgraph, please cite this paper:**

Rodrigo Agerri, Josu Bermudez and German Rigau (2014): "IXA pipeline: Efficient and Ready to Use Multilingual NLP tools", in: Proceedings of the 9th Language Resources and Evaluation Conference (LREC2014), 26-31 May, 2014, Reykjavik, Iceland.

CorefGraph is being used by the [ixa pipes tools](http://ixa2.si.ehu.es/ixa-pipes) which can be used to provide the necessary input. 

This work has been partially funded by a *PhD Grant of the University of Deusto*. 

# How to install

PIP can install the module and every dependency in one command. 

        sudo -H pip install corefgraph

 
# Usage

This module may be used to process single files or directories (corpus). CorefGraph 
takes NAF documents as input. The input NAF documents must contain: 

+ Tokenized text
+ Part of Speech tags and Lemmas
+ Named Entities
+ Constituent Parsing with headwords for each constituent marked. 


The NAF specification can be found [here](https://github.com/ixa-ehu/naf "NAF Homepage")

We recommend using the tools in the [IXA pipeline](https://github.com/opener-project/ixa-ehu "IXA Pipeline Homepage") 
to obtain the necessary linguistic annotation in a easy and efficient manner. 

## Single file

The most simple way to use this module is this:

    corefgraph --file your_file.KAF -l en_conll

This sentence outputs a *NAF* file containing all the original file info plus the 
coreference clusters.

The module is usable as a pipe:

    cat your_file.naf | corefgraph -l en_conll > output.naf


#### Options

The system comes with a lot of options. Use *--help* parameter for the default and possible values. 

These options can be passed to the program via yalm file with the -c parameter
    cat your_file.naf | corefgraph -c semeval_config.yalm > output.naf
    
See [configArgParse](https://github.com/bw2/ConfigArgParse#config-file-syntax) for yaml available syntax
  
 
#### English example config
    
english.yalm
~~~~

language: en_conll
encoding: utf-8
# Document name 
#document_id=result

# Catchers used to extract mention from text. 
# You can create new in the corefgpaph.multisieve.catchers module and add the short_name here. Or remove from the list.
mention_catchers: [NamedEntities, EnumerableCatcher, ConstituentCatcher, PronounCatcher]

# Mentions Filters
# You can create new in the corefgpaph.multisieve.filter module and add the short_name here. Or remove from the list.
mention_filters: [ReplicatedSpanFilter, NamedEntityPartFilter, QuantityFilter, PleonasticFilter, DemonymFilter, InterjectionFilter, PartitiveFilter, BareNPFilter, QuantifierFilter, InvalidWordFilter, InvalidNerFilter, NonWordFilter, SameHeadFilter]

# Purges extract mentions from entities but not remove they from the result. (Uncomment to activate)
#extractor_options: soft_purge

# Filters avoid mention to be processed but are keep on the response. (Uncomment to activate)
#extractor_options: soft_filter

# Sieves used to match mentions
# You can create new in the corefgpaph.multisieve.sieve module and add the short_name here. Or remove from the list.
sieves: [SPM, RSM, ESM, PCM, SHMA, SHMB, SHMC, SHMD, RHM, PNM]

# Writer used to show result output. Select only one:
# OR create one in corefgraph.output and select by its short name
# Default
writer: NAF
# For backward compatibility:
#Writer: KAF
# Also available CONLL format
#writer: CONLL

# Reader used to lad document
reader:NAF
# For backward compatibility
#reader:KAF

# Additional files

# An additional file with the document syntactic parse trees if base one don't have it. Uncoment and set to use.
#treebank: file_name

# An additional file with the speakers of the tokens.  Uncoment and set to use.
#speakers: file_name                      


~~~~

 
#### Spanish example config
    
Spanish.yalm
~~~~

language: es_semeval
encoding: utf-8
# Document name 
#document_id=document_name

# Catchers used to extract mention from text. 
# You can create new in the corefgpaph.multisieve.catchers module and add the short_name here. Or remove from the list.
mention_catchers: [NamedEntities, PermissiveEnumerableCatcher, PermissiveConstituentCatcher, PermissivePronounCatcher]

# Mentions Filters
# You can create new in the corefgpaph.multisieve.filter module and add the short_name here. Or remove from the list.
mention_filters: [ReplicatedSpanFilter, NamedEntityPartFilter, QuantityFilter, PleonasticFilter, DemonymFilter, InterjectionFilter, PartitiveFilter, BareNPFilter, QuantifierFilter, InvalidWordFilter, InvalidNerFilter, NonWordFilter, SameHeadFilter]

# Purges extract mentions from entities but not remove they from the result. (Uncomment to activate)
#extractor_options: soft_purge

# Filters avoid mention to be processed but are keep on the response. (Uncomment to activate)
#extractor_options: soft_filter

# Sieves used to match mentions
# You can create new in the corefgpaph.multisieve.sieve module and add the short_name here. Or remove from the list.
sieves: [SPM, ESM, RSM, PCM, SHMSNE_A, SHMSNE_B, SHMSNE_C, SHMSNE_D, RHMSNE_A, PNM]

# Writer used to show result output. Select only one:
# OR create one in corefgraph.output and select by its short name
# Default
writer: NAF
# For backward compatibility:
#Writer: KAF
# Also available CONLL format
#writer: CONLL

# Reader used to lad document
reader:NAF
# For backward compatibility
#reader:KAF

# Additional files

# An additional file with the document syntactic parse trees if base one don't have it. Uncoment and set to use.
#treebank: file_name

# An additional file with the speakers of the tokens.  Uncoment and set to use.
#speakers: file_name                      

~~~~

## Multiple files

Multiple files mode, or corpus mode, can process multiple files concurrently. 

    python corefgraph_corpus --directories /home/KAF_dir -config configfile

#### Corpus options
The multi file processor needs two basic parameters: a list of files and/or a list 
of input directories, plus a list of configuration files. Both lists should 
at least contain one element, otherwise the processing will end with empty
results. 

You can pass the parameter via yalm file with -p parameter: 
    
    corefgraph_corpus -p corpus_parameters.yalm
    
you can control the max concurrent jobs with  --jobs parameter:

    corefgraph_corpus -jobs 4 -p corpus_parameters.yalm
  
**Input files**

    --file FILES        File to process. May be used multiple times and with
                        directory parameter.
    --directory DIRECTORIES
                        All the files contained by the directory(recursively)
                        are processed. May be used multiple times and with the
                        file parameter.
    --extension EXTENSIONS
                        The extensions of the files(without dot) that must be
                        processed form directories. The '*' is used as accept
                        all. May be used multiple times .WARNING doesn't
                        filter files from --files.
                 
    
    --result             (Optional) A extension added to the result files. The 
                         files are stored next to the original files with
                         the same base name. Also is used in evaluation.
    
    --log_base           The prefix added to the log files usually a directory 
                         
                         
    --speaker_extension  (Optional) If set, the module searches for a file with 
                         the same base name plus the extension and uses
                         it as speaker file. This option is switched off by default.
                           
    --treebank_extension (Optional) If set, the module searches for a file with 
                         the same base name plus the extension and uses it
                         as treebank file. 
                         This option is switched off by default if is set the system 
                         ignores the naf file parse.

**Proceesing parameters**
The parameters used processing each file are passed with parameters files.
 
    --config CONFIG       The config files that contains the parameter each
                        experiment.Use ':' to use multiple files in one
                        experiment. Repeat the parameter for multiple
                        experiments.
                        
    --common COMMON       A common config for all experiments.May be multiple
                        files separated by ':'
 
** evaluation **
The parameters used during the evaluation
     
    --evaluate            Activates the evaluation.
   
    --report              Activates report system.
    
    --evaluation_script    The full path to evaluation script
       
    --metrics           (Optional) When the evaluation parameter is on, 
                        it is possible to specify the evaluation metric used.
    
    --gold                 The path to the golden corpus
     
    --gold_ext             The extension of the golden corpus files.
     


# Troubleshooting

* Make sure you have *python 2.7.1 or higher*.

        python --version

* If you have *problems using the --user option* you may consider to *update pip*.

        sudo pip install --upgrade pip

* The python dist-package directory might be in different location than:
       
        /usr/local/lib/python2.7/dist-packages/

#Contact information

    Josu Bermúdez
    DeustoTech 
    University of Deusto
    Bilbao
    josu.bermudez at deusto.es

    Rodrigo Agerri
    IXA NLP Group
    University of the Basque Country (UPV/EHU)
    E-20018 Donostia-San Sebastián
    rodrigo.agerri at ehu.es
