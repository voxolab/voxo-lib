#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
import os
import subprocess
import sys

from lxml import etree

from voxolab.convert import xml_to_txt


PUNCTUATION_CMD = \
    ("/home/vjousse/usr/src/python/punctuator2/punctuate.sh " +
     "/home/vjousse/usr/src/python/punctuator2/"
     "Model_authot_h256_lr0.02.pcl "
     "{}")


def xml_to_xml_cleaned(source, destination=None, source_encoding='utf-8'):

    # Write to a file if provided, otherwise write to stdout
    output = codecs.open(destination, 'w', encoding='utf-8') \
        if destination else sys.stdout

    # We load the full tree in memory as files should not be too big
    # another solution could be to use the iterparse function
    # Cf. http://effbot.org/zone/element-iterparse.htm
    tree = etree.parse(source)
    root = tree.getroot()
    for sentence in root:
        # sa = sentence.attrib
        last_word = None
        for word in sentence:
            wa = word.attrib

            # Concatenate words with '
            if(last_word is not None and
                    (last_word.attrib['value'].endswith("'")
                        or wa['value'].startswith("'"))):
                wa['value'] = last_word.attrib['value'] + wa['value']
                wa['start'] = last_word.attrib['start']
                wa['length'] = \
                    "{0:.2f}".format(
                        float(last_word.attrib['length']) +
                        float(wa['length']))

                last_word.getparent().remove(last_word)

            last_word = word

    # pretty string
    xml_string = """<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE SHOW PUBLIC "-//VOXOLAB//DTD XML v2.0//EN"
"http://docs.voxolab.com/voxolab-xmlv2.dtd">
"""
    xml_string += etree.tostring(root, pretty_print=True, encoding='unicode')

    print(xml_string, file=output)

    if output is not sys.stdout:
        output.close()

    return xml_string


def parse_output_entries(output, xml_file, resegment=True):

    words_punctuated = output.split(" ")
    total_words = len(words_punctuated)

    tree = etree.parse(xml_file)
    root = tree.getroot()

    nb_xml_words = 0
    current_index = 0

    if not resegment:
        for sentence in root:
            for word in sentence:

                if current_index >= total_words:
                    continue

                current_punctuated_word = words_punctuated[current_index]

                word.attrib['value'] = current_punctuated_word

                current_index += 1
                nb_xml_words += 1
    else:
        new_sentences = []
        current_sentence = {}
        current_speaker = None
        previous_speaker = None
        for sentence in root:
            current_speaker = sentence.attrib['speaker']

            for word in sentence:

                if current_index >= len(words_punctuated):
                    continue

                current_punctuated_word = words_punctuated[current_index]

                if current_index == 0:
                    current_sentence['start'] = float(word.attrib['start'])
                    current_sentence['gender'] = sentence.attrib['gender']
                    current_sentence['speaker'] = current_speaker
                    current_sentence['type'] = sentence.attrib['type']
                    current_sentence['end'] = \
                        float(word.attrib['start']) + \
                        float(word.attrib['length'])
                    new_word = {}
                    new_word['value'] = current_punctuated_word.capitalize()
                    new_word['start'] = word.attrib['start']
                    new_word['length'] = word.attrib['length']
                    new_word['score'] = word.attrib['score']
                    current_sentence['words'] = [new_word]
                    current_index += 1
                    nb_xml_words += 1
                    previous_speaker = current_speaker
                    continue

                previous_punctuated_word = words_punctuated[current_index-1]

                if previous_punctuated_word.endswith("?") or\
                        previous_punctuated_word.endswith("!") or\
                        previous_punctuated_word.endswith(".") or\
                        (previous_speaker is not None and
                         previous_speaker != current_speaker):

                    last_word = current_sentence['words'][-1]['value']
                    if not last_word.endswith("?") and\
                            not last_word.endswith("!") and\
                            not last_word.endswith("."):
                        current_sentence['words'][-1]['value'] = \
                            last_word + "."

                    new_sentences.append(current_sentence)

                    current_sentence = {}
                    current_sentence['gender'] = sentence.attrib['gender']
                    current_sentence['speaker'] = current_speaker
                    current_sentence['type'] = sentence.attrib['type']
                    current_sentence['words'] = []

                new_word = {}

                if len(current_sentence['words']) == 0:
                    current_punctuated_word =\
                        current_punctuated_word.capitalize()

                new_word['value'] = current_punctuated_word
                new_word['start'] = word.attrib['start']
                new_word['length'] = word.attrib['length']
                new_word['score'] = word.attrib['score']
                current_sentence['words'].append(new_word)

                current_sentence['end'] = \
                    float(word.attrib['start']) + float(word.attrib['length'])

                if 'start' not in current_sentence:
                    current_sentence['start'] = float(word.attrib['start'])

                current_index += 1
                nb_xml_words += 1

                previous_speaker = current_speaker

        # Add last sentence if it has words in it
        if len(current_sentence['words']) != 0:
                new_sentences.append(current_sentence)

        new_root = etree.Element('show', name=root.attrib['name'])

        # Now, let's rewrite the XML
        for sentence in new_sentences:
            child_sentence = etree.Element(
                'sentence',
                speaker=sentence['speaker'],
                gender=sentence['gender'],
                type=sentence['type'],
                start="{0:.2f}".format(sentence["start"]),
                end="{0:.2f}".format(sentence["end"]))

            for word in sentence["words"]:
                child_word = etree.Element(
                    'word',
                    length=word['length'],
                    start=word['start'],
                    value=word['value'],
                    score=word['score'])

                child_sentence.append(child_word)

            new_root.append(child_sentence)

    if nb_xml_words != total_words:
        print("Words number in xml {} != {} words punctuated"
              .format(nb_xml_words, total_words), file=sys.stderr)

    # pretty string
    xml_string = """<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE SHOW PUBLIC "-//VOXOLAB//DTD XML v2.0//EN"
"http://docs.voxolab.com/voxolab-xmlv2.dtd">
"""
    xml_string += etree.tostring(
        new_root, pretty_print=True, encoding='unicode')

    return xml_string


def punctuate_xml(xml_file, punctuation_cmd):

    tmp_txt_file = xml_file + ".txt-to-punctuate"
    tmp_xml_file = xml_file + ".xml-from-entries"

    xml_to_xml_cleaned(xml_file, tmp_xml_file)
    xml_to_txt(tmp_xml_file, tmp_txt_file)

    full_punctuation_cmd = \
        punctuation_cmd.format(os.path.abspath(tmp_txt_file))

    output = subprocess.check_output(
        full_punctuation_cmd,
        shell=True)\
        .decode("utf-8")\
        .rstrip()

    xml_string = parse_output_entries(output, tmp_xml_file)

    os.remove(tmp_txt_file)
    os.remove(tmp_xml_file)

    return xml_string


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Add punctuation to XML using punctuator2.')

    parser.add_argument("xml_file", help="the unpunctuated XML file.")

    args = parser.parse_args()

    print(punctuate_xml(args.xml_file, PUNCTUATION_CMD))
