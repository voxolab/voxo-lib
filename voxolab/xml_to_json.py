#!/usr/bin/python
# vim : set fileencoding=utf-8 :

import xml.etree.ElementTree as etree
 
#
# Create json file (for demo purpose) based on the xml file
#
import sys, codecs, argparse, json, re

def xml_to_json(xml_file, destination):
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
    elif(len(root.findall(".//word[@sel]")) > 0):
        version = 'v1'
        encoding = 'iso-8859-1'
        word_selector = 'sel'
        spk_selector = 'locuteur'
        gender_selector = 'sexe'
    else:
        return []

    previous_speaker = None
    previous_gender = None
    speaker_turns = []
    speaker_sentences = []

    output = codecs.open(destination, 'w', encoding = 'utf-8') if destination else sys.stdout

    try:

        for sentence in root:
            speaker = sentence.attrib[spk_selector]
            words = []

            # Speaker change
            if(previous_speaker is not None and speaker != previous_speaker):
                speaker_turns.append({
                    "id":previous_speaker,
                    "gender":previous_gender,
                    # No speaker id score for now in xml
                    "score": None,
                    "sentences":speaker_sentences
                })
                speaker_sentences = []

            for word in sentence:
                json_word = {
                    "start": word.attrib['start'],
                    "word": word.attrib[word_selector],
                    # No named entity support for now
                    "ne": None
                }
                words.append(json_word)

            speaker_sentences.append(words)

            previous_speaker = speaker
            previous_gender = sentence.attrib[gender_selector]


        # Add the last sentence and last speaker turn
        speaker_turns.append({
            "id":previous_speaker,
            "gender":previous_gender,
            # No speaker id score for now in xml
            "score": None,
            "sentences":speaker_sentences
        })


        #import pprint; pprint.pprint(speaker_turns)

        json_output = {}
        json_output['speaker_turns'] = speaker_turns
        print(json.dumps(json_output), file=output)


    finally:
        if output is not sys.stdout:
            output.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a json file based on an xml.')

    parser.add_argument("xml_file", help="the ctm file corresponding to the demo_file.")
    parser.add_argument("--output_file", help="the file you want to write too.")

    args = parser.parse_args()

    xml_to_json(args.xml_file, args.output_file)
