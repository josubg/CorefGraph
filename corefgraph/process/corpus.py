#!/usr/bin/python
# coding=utf-8
""" This module offers the possibility of process a entire corpus of kaf files
 with corefgraph"""

import sys
import os
import re
import json
import configargparse
import codecs
import logging.config
import datetime
import collections
import logging

try:
    from corefgraph import properties
except ImportError as ie:
    sys.path.append(os.getcwd())
    from corefgraph import properties

import pycorpus
import os.path
import os
from file import generate_parser as generate_parser_for_file, process as process_file

__author__ = 'Josu Bermúdez <josu.bermudez@deusto.es>'
__created__ = '27/06/13'


# Logging
logger = logging.getLogger(__name__)
SPACE_CHAR = "_"
LINE_PATTERN = "{0:<20}\t{1}\t {2}\t {3}"


def generate_parser():
    """The parser used to provide configuration from experiment module to
    coreference module.

    Inherited all the properties from coreference module original parser and add
    more for handle the result store.

    :return The parser
    """
    parser = configargparse.ArgumentParser(
        parents=[generate_parser_for_file()], add_help=False)

    parser.add_argument("--experiment_name", dest='experiment_name',
                        action='store', default='last',
                        help='human friendly name for the experiment')
    parser.add_argument('--result', dest='result',
                        action='append', default=["coref"],
                        help="The extension added to result files.")
    parser.add_argument('--metrics', dest='metrics',
                        action='append', default=[],
                        help="The metric of the evaluation.")
    parser.add_argument('--aggregation_metrics', dest='aggregation_metrics',
                        action='append', default=[],
                        help="The metric aggregation source metrics.")
    parser.add_argument('--aggregation_name', dest='aggregation_name',
                        action='store', default="conll",
                        help="The metric aggregation name .")
    parser.add_argument('--speaker_extension', dest='speaker_extension',
                        action='store', default=None,
                        help="The extension of the speaker files(If exist).")
    parser.add_argument('--treebank_extension', dest='treebank_extension',
                        action='store', default=None,
                        help="The extension of the treebank files(If exist).")
    parser.add_argument('--evaluation_script', dest='evaluation_script',
                        action='store', default=None,
                        help="The script used in evaluation.")
    parser.add_argument('--gold', dest='golden',
                        action='store', default=None,
                        help="The golden corpus.'")
    parser.add_argument('--result_base', dest='result_base',
                        action='store', default=None,
                        help="CSV file with results to compare.'")
    parser.add_argument('--gold_ext', dest='golden_ext',
                        action='store', default="conll",
                        help="The golden files extension.")
    parser.add_argument('--output_ext', dest='output_ext',
                        action='store', default="conll",
                        help="The output files extension.")
    parser.add_argument('--log_base', dest='log_base',
                        action='store', default="./log/",
                        help="The path of the log files")
    parser.add_argument('--meta_base', dest='meta_base',
                        action='store', default="./meta/",
                        help="The path of the meta files")
    parser.add_argument('--output_base', dest='output_base',
                        action='store', default="./output/",
                        help="The path of the coreference output files")
    parser.add_argument('--evaluation_base', dest='evaluation_base',
                        action='store', default="./evaluation/",
                        help="The path of the evaluation result files")
    return parser


def file_processor(file_name, config):
    """ Extract from the base file the name of all the analysis needed for
    coreference analysis. Also if the result is in Conll format retrieve the
    part and de document name from filename.

    :param file_name: The file to bo resolved.
    :param config: The configuration for the coreference module.
    :return NOTHING
    """
    path, full_name = os.path.split(file_name)
    name, ext = os.path.splitext(full_name)
    base_name = os.path.join(path, name)

    friendly_name = os.path.join(config.series_name, config.experiment_name).replace(" ", "_")
    log_dir = os.path.join(config.log_base, friendly_name)
    log_file = os.path.join(log_dir, name + ".log")
    try:
        os.makedirs(log_dir)
    except OSError:
        pass
    try:
        os.remove(log_file)
    except OSError as e:
        pass

    store_dir = os.path.join(config.output_base, friendly_name)
    store_file = os.path.join(store_dir, name + config.output_ext)
    try:
        os.makedirs(store_dir)
    except OSError:
        pass
    try:
        os.remove(store_file)
    except OSError as e:
        pass

    # Redirect logger to file
    formatter = logger.handlers[0].formatter
    file_handler = logging.FileHandler(filename=log_file , mode="w")
    file_handler.setFormatter(formatter)
    for logger_name in iter(logging.Logger.manager.loggerDict):
        if logger_name.startswith("pycorpus"):
            continue
        try:
            lg = logging.Logger.manager.loggerDict[logger_name]
            for handler in lg.handlers:
                lg.removeHandler(handler)
            lg.addHandler(file_handler)
        except AttributeError:
            pass
    # Create the file names in base of original file name
    logger.info("Start processing %s", file_name)
    kaf_filename = base_name + ext
    logger.debug("Reading NAF from: %s", kaf_filename)
    # files
    if config.treebank_extension:
        tree_filename = base_name + config.treebank_extension
        logger.info("Using TreeBank trees: %s", tree_filename)
        try:
            trees = codecs.open(tree_filename, mode="r").read()
        except IOError as ex:
            trees = None
            logger.warning("Error in Treebank file %s : %s", tree_filename, ex)
    else:
        logger.info("Using kaf trees")
        trees = None

    if config.speaker_extension:
        speaker_filename = base_name + config.speaker_extension
        try:
            speakers = codecs.open(speaker_filename, mode="r").read()
        except IOError as ex:
            logger.warning("Error in speaker file %s: %s", speaker_filename, ex)
            speakers = None
    else:
        speakers = None
        logger.debug("NO speaker file")

    # If is a Conll file add the document and part info

    config.__dict__["document_id"] = name

    # Open the files and pass the data to the module
    logger.info("Result stored in %s", store_file)
    with codecs.open(store_file, "w") as output_file:
        statistic = process_file(
            config=config,
            text=codecs.open(kaf_filename, mode="r").read(),
            parse_tree=trees,
            speakers_list=speakers,
            output=output_file
        )
    if statistic:

        meta_dir = os.path.join(config.meta_base, friendly_name)
        meta_file = os.path.join(meta_dir,"meta.json")
        try:
            os.makedirs(meta_dir)
        except OSError:
            pass
        try:
            os.remove(meta_file)
        except OSError:
            pass
        with codecs.open(meta_file, "w") as output_file:
            json.dump(statistic, output_file)


def evaluate(general_config, experiment_config):
    """ Evaluates all the corpus and stores the result in files

    :param general_config: The configuration applicable to all corpus
    :param experiment_config: the configuration applicable to this file.
    """
    logger.info("Evaluating: %s", experiment_config.metrics)
    path, script = os.path.split(experiment_config.evaluation_script)
    friendly_name = os.path.join(experiment_config.series_name, experiment_config.experiment_name).replace(" ", "_")
    coref_dir = os.path.abspath(os.path.join(experiment_config.output_base, friendly_name))
    store_dir = os.path.join(experiment_config.evaluation_base, friendly_name)
    golden_dir = os.path.abspath(experiment_config.golden)
    golden_ext = experiment_config.golden_ext
    coref_ext = experiment_config.output_ext
    try:
        os.makedirs(store_dir)
    except OSError:
        pass
    logger.info("Gold stored in %s as %s", golden_dir, golden_ext)
    logger.info("Responses stored in %s as %s", coref_dir, coref_ext)
    logger.info("Evaluation stored in %s", store_dir)
    pycorpus.CorpusProcessor.launch_parallel(
        function=launch_evaluation,
        parameters_lists=list(experiment_config.metrics),
        common_parameters=(script, coref_dir, coref_ext, golden_dir, golden_ext, store_dir, path, ),
        jobs=len(experiment_config.metrics))
    logger.info("Evaluation end.")


def launch_evaluation(metric, common_parameters):
    script, coref_dir, coref_ext, golden_dir, golden_ext, store_dir, path = common_parameters
    logger.info("Metric: %s", metric)
    command = [
        "sh",
        script,
        metric,
        coref_dir,
        coref_ext,
        golden_dir,
        golden_ext
    ]
    # logger.info("CWD: %s", os.path.abspath(path))
    # logger.info("Command: %s", " ".join(command))
    err, out = pycorpus.CorpusProcessor.launch_with_output(command, cwd=os.path.abspath(path))
    if err:
        sys.stderr.write(err)

    with codecs.open("{}.{}".format(store_dir, metric), "w") as output_file:
        output_file.write(err)
        output_file.write(out)


def report(general_config, common_config, experiment_configs):
    """ Generate a email report of the experiment.

    :param experiment_config: The config.
    :param common_config: The config used in all experiments.
    """
    friendly_name = general_config.series_name.replace(" ", "_")
    eval_dir = os.path.join(common_config.evaluation_base, friendly_name)
    logger.info("Generating report")
    logger.info("reading from: " + eval_dir)
    logger.info("F1 : %s", common_config.aggregation_metrics)   
    with open(eval_dir+".md", "w") as report_file:
        report_file.write("##### {}\n".format(general_config.series_name))
        report_file.write(header(["MD"] + common_config.metrics + [common_config.aggregation_name]))
        for experiment in experiment_configs:
            results = generate_report(
                path=os.path.join(eval_dir, experiment.experiment_name).replace(" ", "_"),
                metrics=common_config.metrics + ["MD"], )
            calculate_aggeration(results, common_config.aggregation_metrics, common_config.aggregation_name)
            report_file.write(table(experiment.experiment_name, results,
                            ["MD"] + common_config.metrics + [common_config.aggregation_name]))


def table(name, results, metrics):
    flat_metric = [(m, k)
                  for m in metrics
                  for k in ("R", "P", "F1")]
    return "| {} | ".format(name) + " | ".join("{0:.2f}".format(results[m]) for m in flat_metric) + " |\n"


def header(metrics):
    return '\n|  | ' + ' |  |  | '.join(metrics ) + ' | | |\n' + \
           '| ' + ' | '.join(["---"] * 19) + ' |\n' + \
           '| ' + ' | '.join(["system"] + ["R", "P", "F1"] * 6) + ' |\n'


def calculate_aggeration(results, aggregation_metrics, aggregation_name):
    try:
        results[(aggregation_name, "R")] = sum([results[(m, "R")] for m in aggregation_metrics])/len(aggregation_metrics)
        results[(aggregation_name, "P")] = sum([results[(m, "P")] for m in aggregation_metrics])/len(aggregation_metrics)
        results[(aggregation_name, "F1")] = sum([results[(m, "F1")] for m in aggregation_metrics])/len(aggregation_metrics)
        return False
    except KeyError:
        results[(aggregation_name, "R")] = float("NaN")
        results[(aggregation_name, "P")] = float("NaN")
        results[(aggregation_name, "F1")] = float("NaN")
        return True


def generate_report(path, metrics):
    """ Find any result files in path and make a report with it.

    :param path: The path of the evaluation directory.
    :param metrics: The metrics showed in the report.

    :return: a dictionary containing the numeric results .

    """
    results = {}
    for metric in metrics:
        if metric == "MD":
            # Calculate mention detection with fastest metric
            m = "muc"
        else:
            m = metric
        with open(path + "." + m, "r") as evaluation_file:
            evaluation = evaluation_file.read()

            if metric == "MD":
                line, r_index, p_index, f1_index = -5, -4, -3, -2
            else:
                line, r_index, p_index, f1_index = -3, -4, -3, -2
            tokens = evaluation.split("\n")[line].split("%")
            results[metric, "R"] = float(tokens[r_index].split(" ")[-1])
            results[metric, "P"] = float(tokens[p_index].split(" ")[-1])
            results[metric, "F1"] = float(tokens[f1_index].split(" ")[-1])
    return results


def main(config_files=False):
    """ Run the corpus processing.

    :param config_files: The name of the parameter file
    """
    experiment_instance = pycorpus.CorpusProcessor(
        generate_parser_function=generate_parser,
        process_file_function=file_processor,
        evaluation_script=evaluate,
        report_script=report)
    experiment_instance.run_corpus(config_files)


if __name__ == "__main__":
    main()
