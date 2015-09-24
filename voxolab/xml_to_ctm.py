#!/usr/bin/python
# vim : set fileencoding=utf-8 :

import xml.etree.ElementTree as etree
 
#
# Create json file (for demo purpose) based on the xml file
#
import sys, codecs, argparse, json, re

def xml_to_ctm(xml_file, destination):
    """Convert an xml file (v1 or v2) to a json file for web demo

    :xml_file: the path of the input xml file
    :destination: the path of the output xml file
    :returns: side effect 4ever

    """

    tree = etree.parse(xml_file)
    root = tree.getroot()

    # Check xml version and force encoding for compatibility purpose
    if(len(root.findall(".//word[@value]")) > 0):
        version = 'v2'
        encoding = 'utf-8'
        word_selector = 'value'
        spk_selector = 'speaker'
        gender_selector = 'gender'
        score_selector = 'score'
    elif(len(root.findall(".//word[@sel]")) > 0):
        version = 'v1'
        encoding = 'iso-8859-1'
        word_selector = 'sel'
        spk_selector = 'locuteur'
        gender_selector = 'sexe'
        score_selector = 'scoreConfiance'
    else:
        return []

    previous_speaker = None
    previous_gender = None
    speaker_turns = []
    speaker_sentences = []

    output = codecs.open(destination, 'w', encoding = 'utf-8') if destination else sys.stdout

    try:
        words = []

        for sentence in root:

            for word in sentence:

                parts = []

                parts.append(word.attrib['start'])
                parts.append(word.attrib['length'])
                parts.append(word.attrib[word_selector])
                parts.append(word.attrib[score_selector])

                words.append(parts)

        lines = ""
        for word in words:
            lines = lines + root.attrib['name'] + " 1 " + " ".join(word) + "\n"

        print(lines, file=output)

    finally:
        if output is not sys.stdout:
            output.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a ctm file based on an xml.')

    parser.add_argument("xml_file", help="the xml file corresponding.")
    parser.add_argument("--output_file", help="the file you want to write too.")

    args = parser.parse_args()

    xml_to_ctm(args.xml_file, args.output_file)
