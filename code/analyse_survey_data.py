#!/usr/bin/env python3
#
# Code to analyse TSV-formatted Qualtrics survey data.
# Copyright (C) 2017  Philipp Winter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import csv
import codecs
import collections
import termcolor

# A Response tuple enables intuitive access to specific questions, e.g., by
# writing resp.q5_4 to access question 4 in Section 5.

Response = collections.namedtuple("Response", ["start_date", "end_date",
    "status", "ip_addr", "progress", "duration", "finished", "recorded_date",
    "id", "last_name", "first_name", "email", "ext_ref", "latitude",
    "longitude", "dist_channel", "language",
    "q1_1", "q1_3", "q1_4", "q1_5", "q1_6",
    "q2_1", "q2_2", "q2_3", "q2_4", "q2_4_text", "q2_5", "q2_5_text",
    "q3_3", "q3_4", "q3_5", "q3_5_text", "q3_6", "q3_6_text", "q3_7",
    "q3_7_text", "q3_8", "q3_8_text", "q3_9", "q3_9_text_1", "q3_9_text_2",
    "q3_10", "q3_11", "q3_12", "q3_13", "q3_14", "q3_15", "q3_15_text",
    "q3_16_1", "q3_16_2", "q3_16_3", "q3_16_4", "q3_17", "q3_18", "q3_18_text",
    "q3_19", "q3_20", "q3_20_text", "q3_21", "q3_22_1", "q3_22_2", "q3_22_3",
    "q3_22_4", "q3_22_5", "q3_22_6", "q4_2", "q4_3", "q4_3_text", "q4_4",
    "q4_4_text", "q4_5", "q4_6_1", "q4_6_3", "q4_6_2",
    "q5_2", "q5_3", "q5_4", "q5_4_text", "q5_5", "q5_6", "q5_6_text", "q5_7",
    "q5_8", "q5_9", "q5_11", "q5_11_text", "q6_2", "q6_2_text", "q6_3",
    "q6_3_text", "q6_4", "q6_5", "q6_6", "q6_7", "q6_8", "q6_9", "q6_9_text",
    "q6_10_1", "q6_10_2", "q6_10_3", "q7_2",
    "bogus1", "bogus2", "bogus3", "bogus4"])


class Demographic(object):
    """
    Represents a demographic, i.e., a subset of all responses.
    """

    def __init__(self, responses):
        self.responses = responses

    def __iter__(self):
        for x in self.responses:
            yield x

    def __len__(self):

        return len(self.responses)

    def filter(self, question, answer):
        """Filter demographic for the given answer to the given question."""

        return Demographic([r for r in self.responses
                            if r.__getattribute__(question) in answer])

    def frac(self, question, answer):
        """Return fraction that provided given answer to given question."""

        return float(len(self.filter(question, answer))) / len(self.responses)

    def pct(self, question, answer):
        """Return percentage that provided given answer to given question."""

        return self.frac(question, answer) * 100


def log(*args, **kwargs):
    """Generic log function that prints to stderr."""

    print("%s%s%s" % (termcolor.colored("[", "red", attrs=["bold"]),
                      termcolor.colored("+", "red"),
                      termcolor.colored("]", "red", attrs=["bold"])),
          *args, file=sys.stderr, **kwargs)


def parse_data(file_name=sys.argv[1]):
    """Parse survey data from the given file."""

    responses = []

    log("Opening file %s" % file_name)

    try:
        fd = codecs.open(sys.argv[1], "rb", "utf-16")
    except Exception as err:
        log(err)
        sys.exit(1)

    csvread = csv.reader(fd, delimiter="\t")
    for row in csvread:
        responses.append(Response(*row))

    log("Parsed %d responses" % len(responses))

    return responses


def analyse():
    """Analyse the data set."""

    population = Demographic(parse_data())

    # Select subjects that have either an undergraduate or a graduate degree.

    educated = Demographic([r for r in population if r.q1_5 in ["3", "4"]])

    # Select subjects that are either highly knowledgeable or experts in
    # Internet privacy and security.

    experts = Demographic([r for r in population if r.q1_6 in ["4", "5"]])

    # Select subjects that either use Tor Browser as their main browser or use
    # Tor on average once a day.

    freq_users = Demographic([r for r in population if r.q2_3 in ["1", "6"]])

    print("%.2f%% of frequent Tor users use onion sites frequently." %
          freq_users.pct("q3_3", ["1", "2"]))

    print("%.2f%% of Tor users use onion sites frequently." %
          population.pct("q3_3", ["1", "2"]))

    return 0


if __name__ == "__main__":
    sys.exit(analyse())
