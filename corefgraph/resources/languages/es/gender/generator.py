__author__ = 'josubg'

import csv
import collections

import logging
logging.basicConfig(level=logging.DEBUG)

threshold = 0.9

total = 0.0
reader = csv.reader(open("female_frequency.csv"))

female_data = [(x[1], int(x[2])) for x in reader]
female_counter = collections.Counter()
for entry in female_data:
    female_counter[entry[0].split()[0].lower()] += entry[1]
    total += entry[1]
logging.debug("%s Female entries loaded", len(female_data))
logging.debug("%s Female single names loaded", len(female_counter))


reader = csv.reader(open("male_frequency.csv"))

male_data = [(x[1], int(x[2])) for x in reader]
male_counter = collections.Counter()
for entry in male_data:
    male_counter[entry[0].split()[0].lower()] += entry[1]
    total += entry[1]

names = set(male_counter.keys() + female_counter.keys())
logging.debug("%s Male entries loaded", len(male_data))
logging.debug("%s Male names loaded", len(male_counter))


with open("names_combine.txt", "w")as out:
    for name in names:
        gender_index = (male_counter[name] - female_counter[name])/(0.0 + male_counter[name] + female_counter[name])
        if gender_index > 0 + threshold:
            out.write(name + "\t" + "MALE" + "\n")
        elif gender_index < 0 - threshold:
            out.write(name + "\t" + "FEMALE" + "\n")
        else:
            out.write(name + "\t" + "UNKNOWN" + "\n")
