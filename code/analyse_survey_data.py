#!/usr/bin/env python3
#
# Code to analyse TSV-formatted Qualtrics survey data.
# Copyright (C) 2017, 2018  Philipp Winter
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

import re
import sys
import csv
import codecs
import collections
import termcolor

METADATA_LINES = 3

# Questions that have multiple choices save the answer as a comma-separated
# list of numbers, e.g.: 1,4,5,9

MULTIPLE_CHOICE_RESPONSE = re.compile("^\d,[\d,]*$")

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

    def remove(self, elem):

        self.responses.remove(elem)

    def filter(self, question, answer):
        """Filter demographic for the given answer to the given question."""

        assert isinstance(question, str)

        filtered = Demographic([])
        for r in self.responses:

            if isinstance(r.__getattribute__(question), list):
                match = lambda x, y: x in y
            elif isinstance(r.__getattribute__(question), str):
                match = lambda x, y: x == y

            if match(answer, r.__getattribute__(question)):
                filtered.responses.append(r)

        return filtered

    def frac(self, question, answer):
        """Return fraction that provided given answer to given question."""

        # Get total number of responses, i.e., responses that didn't select an
        # empty set of answers.

        total = len([r for r in self.responses
                     if r.__getattribute__(question) != ""])

        return float(len(self.filter(question, answer))) / total

    def pct(self, question, answer):
        """Return percentage that provided given answer to given question."""

        return self.frac(question, answer) * 100

    def count(self, question, answer):

        return len([r for r in self.responses
                    if r.__getattribute__(question) == answer])


def log(*args, **kwargs):
    """Generic log function that prints to stderr."""

    print("%s%s%s" % (termcolor.colored("[", "red", attrs=["bold"]),
                      termcolor.colored("+", "red"),
                      termcolor.colored("]", "red", attrs=["bold"])),
          *args, file=sys.stderr, **kwargs)


def parse_data(file_name):
    """Parse survey data from the given file."""

    responses = []

    log("Attempting to open file '%s'." % file_name)

    try:
        fd = codecs.open(file_name, "rb", "utf-16")
    except Exception as err:
        log(err)
        sys.exit(1)

    csvread = csv.reader(fd, delimiter="\t")
    for row in csvread:

        # Turn non-text responses into lists.

        for i, field in enumerate(row):
            if re.match(MULTIPLE_CHOICE_RESPONSE, field.strip()):
                row[i] = field.split(",")

        responses.append(Response(*row))

    # Discard the first three "responses" because they are meta data and not
    # actual responses.

    log("Discarding the first %d meta data lines." % METADATA_LINES)

    responses = responses[METADATA_LINES:]

    log("Parsed %d survey responses." % len(responses))

    return responses


def prune_data(demographic):
    """
    Weed out low-quality and incomplete responses.

    We employ a number of heuristics to remove responses that...
    - ...did not finish the survey.
    - ...did not get at least two out of four attention checks.
    """

    orig_size = len(demographic)
    log("Starting with %d responses before pruning." % orig_size)

    # Weed out responses that did not finish the survey.

    demographic = demographic.filter("finished", "1")
    log("%d (%.2f%%) responses left after pruning non-finished responses." %
        (len(demographic), float(len(demographic)) / orig_size * 100))

    # Analyse attention checks.  Responses must have gotten at least two out of
    # four attention checks correct to be considered valid.

    min_correct = 2
    attention_checks = [("q2_5",  ["3", "4"]),
                        ("q3_12", "2"),
                        ("q5_8",  "4"),
                        ("q6_8",  "1")]

    for response in demographic:
        correct = 0
        for question, auth_answer in attention_checks:

            # Does the responden't answer match the authoritative answer?

            resp_answer = response.__getattribute__(question)
            correct += resp_answer == auth_answer
        if correct < min_correct:
            demographic.remove(response)

    log("%d (%.2f%%) responses left after pruning failed attention checks." %
        (len(demographic), float(len(demographic)) / orig_size * 100))

    return demographic


def tor_usage(d):
    """
    Analyse questions in the "Tor usage" block of the survey.

    `d' is the given demographic, i.e., our survey responses after they were
    pruned of low-quality responses.
    """

    print("---\nQuestion 2.3:")
    print("%6.2f%% never use Tor Browser."            % d.pct("q2_3", "5"))
    print("%6.2f%% use Tor Browser less than montly." % d.pct("q2_3", "4"))
    print("%6.2f%% use Tor Browser once a month."     % d.pct("q2_3", "3"))
    print("%6.2f%% use Tor Browser once a week."      % d.pct("q2_3", "2"))
    print("%6.2f%% use Tor Browser once a day."       % d.pct("q2_3", "1"))
    print("%6.2f%% use Tor Browser as main browser."  % d.pct("q2_3", "6"))

    print("---\nQuestion 2.4:")
    print("%6.2f%% worry about their government."         % d.pct("q2_4", "1"))
    print("%6.2f%% worry about other governments."        % d.pct("q2_4", "2"))
    print("%6.2f%% worry about their ISP."                % d.pct("q2_4", "3"))
    print("%6.2f%% worry about their school."             % d.pct("q2_4", "4"))
    print("%6.2f%% worry about their employwer."          % d.pct("q2_4", "5"))
    print("%6.2f%% worry about their friends and family." % d.pct("q2_4", "6"))
    print("%6.2f%% worry about ad companies."             % d.pct("q2_4", "7"))
    print("%6.2f%% worry about hackers in open WiFis."    % d.pct("q2_4", "8"))
    print("%6.2f%% worry about other actors."             % d.pct("q2_4", "9"))


def onion_usage(d):
    """
    Analyse questions in the "Onion site usage" block of the survey.

    `d' is the given demographic, i.e., our survey responses after they were
    pruned of low-quality responses.
    """

    print("---\nQuestion 3.3:")
    print("%6.2f%% never used onion sites."    % d.pct("q3_3", "5"))
    print("%6.2f%% use onion sites < monthly." % d.pct("q3_3", "4"))
    print("%6.2f%% use onion sites monthly."   % d.pct("q3_3", "3"))
    print("%6.2f%% use onion sites weekly."    % d.pct("q3_3", "2"))
    print("%6.2f%% use onion sites daily."     % d.pct("q3_3", "1"))

    print("---\nQuestion 3.4:")
    print("%6.2f%% never use OSs for non-browsing."     % d.pct("q3_4", "5"))
    print("%6.2f%% use OSs for non-browsing < monthly." % d.pct("q3_4", "4"))
    print("%6.2f%% use OSs for non-browsing monthly."   % d.pct("q3_4", "3"))
    print("%6.2f%% use OSs for non-browsing weekly."    % d.pct("q3_4", "2"))
    print("%6.2f%% use OSs for non-browsing daily."     % d.pct("q3_4", "1"))

    print("---\nQuestion 3.5:")
    print("%6.2f%% b/c of more anonymity"          % d.pct("q3_5", "1"))
    print("%6.2f%% b/c of more security"           % d.pct("q3_5", "2"))
    print("%6.2f%% b/c some sites are only onions" % d.pct("q3_5", "3"))
    print("%6.2f%% just click on random links"     % d.pct("q3_5", "4"))
    print("%6.2f%% curious about the dark web"     % d.pct("q3_5", "5"))
    print("%6.2f%% b/c of other reasons"           % d.pct("q3_5", "6"))

    print("---\nQuestion 3.6:")
    print("%6.2f%% from social networking"   % d.pct("q3_6", "2"))
    print("%6.2f%% from search engine lists" % d.pct("q3_6", "1"))
    print("%6.2f%% from random encounters"   % d.pct("q3_6", "4"))
    print("%6.2f%% from friends/family"      % d.pct("q3_6", "3"))
    print("%6.2f%% from other"               % d.pct("q3_6", "6"))
    print("%6.2f%% are not interested"       % d.pct("q3_6", "5"))

    print("---\nQuestion 3.8:")
    print("%6.2f%% save list on computer"             % d.pct("q3_8", "1"))
    print("%6.2f%% write them down using pen & paper" % d.pct("q3_8", "2"))
    print("%6.2f%% bookmark in tor browser"           % d.pct("q3_8", "3"))
    print("%6.2f%% use web-based bookmarking service" % d.pct("q3_8", "4"))
    print("%6.2f%% use search engine each time"       % d.pct("q3_8", "5"))
    print("%6.2f%% use trusted sites for onion links" % d.pct("q3_8", "9"))
    print("%6.2f%% memorize some onion domains"       % d.pct("q3_8", "6"))
    print("%6.2f%% don't have a good solution"        % d.pct("q3_8", "7"))
    print("%6.2f%% other"                             % d.pct("q3_8", "8"))

    print("---\nQuestion 3.13:")
    print("%6.2f%% none"            % d.pct("q3_13", "1"))
    print("%6.2f%% one"             % d.pct("q3_13", "2"))
    print("%6.2f%% two"             % d.pct("q3_13", "3"))
    print("%6.2f%% three"           % d.pct("q3_13", "4"))
    print("%6.2f%% four"            % d.pct("q3_13", "5"))
    print("%6.2f%% more than four"  % d.pct("q3_13", "6"))

    print("---\nQuestion 3.14:")
    print("%6.2f%% yes" % d.pct("q3_14", "1"))
    print("%6.2f%% no"  % d.pct("q3_14", "2"))

    print("---\nQuestion 3.15:")
    print("%6.2f%% allows me to open the site more quickly"             % d.pct("q3_15", "1"))
    print("%6.2f%% don’t want to leave any digital traces"              % d.pct("q3_15", "2"))
    print("%6.2f%% can be sure that I end up at the right onion site"   % d.pct("q3_15", "3"))
    print("%6.2f%% automatically start to memorize it"                  % d.pct("q3_15", "4"))
    print("%6.2f%% other"                                               % d.pct("q3_15", "5"))

    '''
    print("---\nQuestion 3.15 txt:")
    for r in d.responses:
        if r.q3_15_text != "":
            print("- %s" % r.q3_15_text)
    '''

    print("---\nQuestion 3.16 (facebookcorewwwi.onion):")
    print("%6.2f%% very easy"                   % d.pct("q3_16_1", "1"))
    print("%6.2f%% somewhat easy"               % d.pct("q3_16_1", "2"))
    print("%6.2f%% neither easy nor difficult"  % d.pct("q3_16_1", "3"))
    print("%6.2f%% somewhat difficult"          % d.pct("q3_16_1", "4"))
    print("%6.2f%% very difficult"              % d.pct("q3_16_1", "5"))

    print("---\nQuestion 3.16 (expyuzz4wqqyqhjn.onion):")
    print("%6.2f%% very easy"                   % d.pct("q3_16_2", "1"))
    print("%6.2f%% somewhat easy"               % d.pct("q3_16_2", "2"))
    print("%6.2f%% neither easy nor difficult"  % d.pct("q3_16_2", "3"))
    print("%6.2f%% somewhat difficult"          % d.pct("q3_16_2", "4"))
    print("%6.2f%% very difficult"              % d.pct("q3_16_2", "5"))

    print("---\nQuestion 3.16 (torproz4wqqyqhjn.onion):")
    print("%6.2f%% very easy"                   % d.pct("q3_16_3", "1"))
    print("%6.2f%% somewhat easy"               % d.pct("q3_16_3", "2"))
    print("%6.2f%% neither easy nor difficult"  % d.pct("q3_16_3", "3"))
    print("%6.2f%% somewhat difficult"          % d.pct("q3_16_3", "4"))
    print("%6.2f%% very difficult"              % d.pct("q3_16_3", "5"))

    print("---\nQuestion 3.16 (torprojectqyqhjn.onion):")
    print("%6.2f%% very easy"                   % d.pct("q3_16_4", "1"))
    print("%6.2f%% somewhat easy"               % d.pct("q3_16_4", "2"))
    print("%6.2f%% neither easy nor difficult"  % d.pct("q3_16_4", "3"))
    print("%6.2f%% somewhat difficult"          % d.pct("q3_16_4", "4"))
    print("%6.2f%% very difficult"              % d.pct("q3_16_4", "5"))

    '''
    print("---\nQuestion 3.17 txt:")
    for r in d.responses:
        if r.q3_17 != "":
            print("- %s" % r.q3_17)
    '''


def onion_operation(d):

    print("---\nQuestion 4.2:")
    print("%6.2f%% set up their own OS"  % d.pct("q4_2", "1"))
    print("%6.2f%% considered it" % d.pct("q4_2", "2"))
    print("%6.2f%% did not consider it" % d.pct("q4_2", "3"))

    print("---\nQuestion 4.4:")
    print("%6.2f%% for anonymity"       % d.pct("q4_4", "1"))
    print("%6.2f%% for e2e security"    % d.pct("q4_4", "2"))
    print("%6.2f%% for 3rd party tools" % d.pct("q4_4", "3"))
    print("%6.2f%% for NAT traversal"   % d.pct("q4_4", "6"))
    print("%6.2f%% out of curiosity"    % d.pct("q4_4", "4"))
    print("%6.2f%% for other reasons"   % d.pct("q4_4", "5"))

    print("---\nQuestion 4.5:")
    print("%6.2f%% for public use"  % d.pct("q4_5", "1"))
    print("%6.2f%% for private use" % d.pct("q4_5", "2"))

    print("---\nQuestion 4.6:")
    print("%6.2f%% not at all" % d.pct("q4_6_3", "1"))
    print("%6.2f%% slightly"   % d.pct("q4_6_3", "2"))
    print("%6.2f%% somewhat"   % d.pct("q4_6_3", "3"))
    print("%6.2f%% moderately" % d.pct("q4_6_3", "4"))
    print("%6.2f%% extremely"  % d.pct("q4_6_3", "5"))


def onion_impersonation(d):

    print("---\nQuestion 5.2:")
    print("%6.2f%% once typed an onion domain"  % d.pct("q5_2", "1"))
    print("%6.2f%% never typed an onion domain" % d.pct("q5_2", "2"))

    print("---\nQuestion 5.5:")
    print("%6.2f%% thought about authenticity"       % d.pct("q5_5", "1"))
    print("%6.2f%% never thought about authenticity" % d.pct("q5_5", "2"))

    print("---\nQuestion 5.6:")
    print("%6.2f%% verify in address bar"            % d.pct("q5_6", "1"))
    print("%6.2f%% use bookmarks"                    % d.pct("q5_6", "2"))
    print("%6.2f%% look at the clearnet site"        % d.pct("q5_6", "3"))
    print("%6.2f%% sometimes cannot tell diff"       % d.pct("q5_6", "4"))
    print("%6.2f%% copy & paste from trusted source" % d.pct("q5_6", "7"))
    print("%6.2f%% check onion site's https cert"    % d.pct("q5_6", "8"))
    print("%6.2f%% don't check"                      % d.pct("q5_6", "5"))
    print("%6.2f%% do other stuff"                   % d.pct("q5_6", "6"))

    print("---\nQuestion 5.7:")
    print("%6.2f%%   1-3" % d.pct("q5_7", "1"))
    print("%6.2f%%   4-6" % d.pct("q5_7", "2"))
    print("%6.2f%%   7-9" % d.pct("q5_7", "3"))
    print("%6.2f%% 10-12" % d.pct("q5_7", "4"))
    print("%6.2f%% 13-16" % d.pct("q5_7", "5"))

    print("---\nQuestion 5.9:")
    print("%6.2f%% sent bitcoins"       % d.pct("q5_9", "1"))
    print("%6.2f%% never sent bitcoins" % d.pct("q5_9", "2"))

    print("---\nQuestion 5.11:")
    print("%6.2f%% useful b/c easy to remember"         % d.pct("q5_11", "1"))
    print("%6.2f%% useful b/c easy to recognise"        % d.pct("q5_11", "2"))
    print("%6.2f%% like them b/c they make site unique" % d.pct("q5_11", "3"))
    print("%6.2f%% dislike b/c domain should be random" % d.pct("q5_11", "4"))
    print("%6.2f%% don't see a benefit"                 % d.pct("q5_11", "5"))
    print("%6.2f%% don't have an opinion"               % d.pct("q5_11", "6"))
    print("%6.2f%% other"                               % d.pct("q5_11", "7"))


def privacy_expectation(d):

    print("---\nQuestion 6.2:")
    print("%6.2f%% Your Internet service provider (ISP)"    % d.pct("q6_2", "1"))
    print("%6.2f%% The ISP of example.com"                  % d.pct("q6_2", "2"))
    print("%6.2f%% Your Tor Exit relay"                     % d.pct("q6_2", "3"))
    print("%6.2f%% Your Tor Guard relay"                    % d.pct("q6_2", "4"))
    print("%6.2f%% Nobody"                                  % d.pct("q6_2", "5"))
    print("%6.2f%% I don't know"                            % d.pct("q6_2", "6"))
    print("%6.2f%% Other"                                   % d.pct("q6_2", "7"))

    '''
    print("---\nQuestion 6.2 txt:")
    for r in d.responses:
        if r.q6_2_text != "":
            print("- %s" % r.q6_2_text)
    '''

    print("---\nQuestion 6.4:")
    print("%6.2f%% very unsafe"     % d.pct("q6_4", "5"))
    print("%6.2f%% somewhat unsafe" % d.pct("q6_4", "4"))
    print("%6.2f%% neutral"         % d.pct("q6_4", "3"))
    print("%6.2f%% somewhat safe"   % d.pct("q6_4", "1"))
    print("%6.2f%% very safe"       % d.pct("q6_4", "2"))

    print("---\nQuestion 6.6:")
    print("%6.2f%% very unsafe"     % d.pct("q6_6", "1"))
    print("%6.2f%% somewhat unsafe" % d.pct("q6_6", "2"))
    print("%6.2f%% neutral"         % d.pct("q6_6", "3"))
    print("%6.2f%% somewhat safe"   % d.pct("q6_6", "4"))
    print("%6.2f%% very safe"       % d.pct("q6_6", "5"))


def demographic_info(d):

    print("---\nQuestion 1.3:")
    print("%3d%6.2f%% are female" % (d.count("q1_3", "1"), d.pct("q1_3", "1")))
    print("%3d%6.2f%% are male"   % (d.count("q1_3", "2"), d.pct("q1_3", "2")))
    print("%3d%6.2f%% other"      % (d.count("q1_3", "3"), d.pct("q1_3", "3")))
    print("%3d%6.2f%% n/a"        % (d.count("q1_3", ""),  d.pct("q1_3", "")))

    print("---\nQuestion 1.4:")
    print("%3d%6.2f%% 18-25" % (d.count("q1_4", "1"), d.pct("q1_4", "1")))
    print("%3d%6.2f%% 26-35" % (d.count("q1_4", "2"), d.pct("q1_4", "2")))
    print("%3d%6.2f%% 36-45" % (d.count("q1_4", "3"), d.pct("q1_4", "3")))
    print("%3d%6.2f%% 46-55" % (d.count("q1_4", "4"), d.pct("q1_4", "4")))
    print("%3d%6.2f%% 56-65" % (d.count("q1_4", "5"), d.pct("q1_4", "5")))
    print("%3d%6.2f%% >65"   % (d.count("q1_4", "6"), d.pct("q1_4", "6")))
    print("%3d%6.2f%% n/a"   % (d.count("q1_4", ""),  d.pct("q1_4", "")))

    print("---\nQuestion 1.5:")
    print("%3d%6.2f%% < high school" % (d.count("q1_5", "1"), d.pct("q1_5", "1")))
    print("%3d%6.2f%% high school"   % (d.count("q1_5", "2"), d.pct("q1_5", "2")))
    print("%3d%6.2f%% graduate"      % (d.count("q1_5", "3"), d.pct("q1_5", "3")))
    print("%3d%6.2f%% post-grad"     % (d.count("q1_5", "4"), d.pct("q1_5", "4")))
    print("%3d%6.2f%% n/a"           % (d.count("q1_5", ""),  d.pct("q1_5", "")))

    print("---\nQuestion 1.6:")
    print("%3d%6.2f%% nothing"  % (d.count("q1_6", "1"), d.pct("q1_6", "1")))
    print("%3d%6.2f%% mildly"   % (d.count("q1_6", "2"), d.pct("q1_6", "2")))
    print("%3d%6.2f%% moderate" % (d.count("q1_6", "3"), d.pct("q1_6", "3")))
    print("%3d%6.2f%% highly"   % (d.count("q1_6", "4"), d.pct("q1_6", "4")))
    print("%3d%6.2f%% expert"   % (d.count("q1_6", "5"), d.pct("q1_6", "5")))
    print("%3d%6.2f%% n/a"      % (d.count("q1_6", ""),  d.pct("q1_6", "")))


def onion_preference(d):
    print("---\nQuestion 3.18:")
    print("%6.2f%% Always the normal web site"              % d.pct("q3_18", "4"))
    print("%6.2f%% Always the onion site"                   % d.pct("q3_18", "2"))
    print("%6.2f%% Other (Please elaborate below.)"         % d.pct("q3_18", "5"))

    '''
    print("---\nQuestion 3.18 txt:")
    for r in d.responses:
        if r.q3_18_text != "":
            print("- %s" % r.q3_18_text)

    print("---\nQuestion 3.19:")
    for r in d.responses:
        if r.q3_19 != "":
            print("- %s" % r.q3_19)
    '''

    print("---\nQuestion 3.20:")
    print("%6.2f%% No, never"                               % d.pct("q3_20", "3"))
    print("%6.2f%% Yes, for some sites"                     % d.pct("q3_20", "2"))
    print("%6.2f%% Yes, always"                             % d.pct("q3_20", "1"))
    print("%6.2f%% Other (Please elaborate below.)"         % d.pct("q3_20", "6"))

    '''
    print("---\nQuestion 3.20 txt:")
    for r in d.responses:
        if r.q3_20_text != "":
            print("- %s" % r.q3_20_text)

    print("---\nQuestion 3.21:")
    for r in d.responses:
        if r.q3_21 != "":
            print("- %s" % r.q3_21)
    '''

def analyse():
    """Analyse the data set."""

    if len(sys.argv) != 2:
        log("Usage: %s FILE_NAME" % sys.argv[0])
        return 1

    population = prune_data(Demographic(parse_data(sys.argv[1])))

    # Select subjects that have either an undergraduate or a graduate degree.

    graduates = Demographic([r for r in population
                             if set(r.q1_5).issubset(set(["3", "4"]))])

    # Select subjects that are either highly knowledgeable or experts in
    # Internet privacy and security.

    experts = Demographic([r for r in population
                           if set(r.q1_6).issubset(set(["4", "5"]))])

    # Select subjects that either use Tor Browser as their main browser or use
    # Tor on average once a day.

    freq_users = Demographic([r for r in population
                              if set(r.q2_3).issubset(set(["1", "6"]))])

    log("Analysing questions about Tor usage.")
    tor_usage(population)

    log("Analysing questions about onion site usage.")
    onion_usage(population)

    log("Analysing questions about onion site operation.")
    onion_operation(population)

    log("Analysing questions about onion site impersonation.")
    onion_impersonation(population)

    log("Analysing questions about privacy expectations.")
    privacy_expectation(population)

    log("Analysing demographic information.")
    demographic_info(population)

    log("Analyzing preference for regular sites vs onion sites.")
    onion_preference(population)

    return 0


if __name__ == "__main__":
    sys.exit(analyse())
