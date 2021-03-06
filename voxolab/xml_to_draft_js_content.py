#!/usr/bin/python
# vim : set fileencoding=utf-8 :

import xml.etree.ElementTree as etree

#
# Create json file (for demo purpose) based on the xml file
#

import argparse
import codecs
import json
import sys
import os

def get_word_value(word, previous_word):
    if previous_word == "" \
            or not previous_word \
            or previous_word.endswith("'"):
        return word
    else:
        return " " + word


def write_json(blocks, entity_map, output):
    json_output = {}
    json_output['blocks'] = blocks
    json_output['entityMap'] = entity_map
    print(json.dumps(json_output, indent=2, sort_keys=True), file=output)


def get_json_filename(spk_turn, filename):
    (base, ext) = os.path.splitext(filename)
    return base + "." + str(spk_turn) + ext

def xml_to_draft_js_content(xml_file, destination, one_file_per_turn):
    """Convert an xml file (v1 or v2) to a json file for web demo
    This json file can be used as rawContent of
    https://facebook.github.io/draft-js/.

    :xml_file: the path of the input xml file
    :destination: the path of the output json file
    :returns: side effect 4ever

    """

    tree = etree.parse(xml_file)
    root = tree.getroot()

    # Check xml version and force encoding for compatibility purpose
    if(len(root.findall(".//word[@value]")) > 0):
        word_selector = 'value'
        spk_selector = 'speaker'
        gender_selector = 'gender'
    elif(len(root.findall(".//word[@sel]")) > 0):
        word_selector = 'sel'
        spk_selector = 'locuteur'
        gender_selector = 'sexe'
    else:
        return []

    previous_speaker = None
    previous_gender = None
    spk_turn = 0
    blocks = []
    entity_map = {}
    entity_key = 1

    try:

        for sentence in root:
            entity_start = 0
            entity_length = 0
            block_text = ""
            block_ranges = []
            previous_word = ""

            speaker = sentence.attrib[spk_selector]

            # Speaker change, write the previous speaker
            if(previous_speaker is not None \
                    and speaker != previous_speaker \
                    and one_file_per_turn):

                output = \
                    codecs.open(get_json_filename(spk_turn, destination), 'w', encoding='utf-8') \
                    if destination else sys.stdout

                write_json(blocks, entity_map, output)

                if output is not sys.stdout:
                    output.close()

                blocks = []
                entity_map = {}
                entity_key = 1

                spk_turn = spk_turn + 1

            for word in sentence:
                word_text = get_word_value(
                    word.attrib[word_selector],
                    previous_word)

                entity_start = len(block_text)
                entity_length = len(word_text)

                # Don't highlight spaces
                if(word_text.startswith(' ')) :
                    entity_start = entity_start + 1
                    entity_length = entity_length - 1

                block_text = block_text + word_text
                block_ranges.append({
                    'offset': entity_start,
                    'length': entity_length,
                    'key': str(entity_key)
                })

                entity_map[entity_key] = {
                    'type': 'WORD',
                    'mutability': 'MUTABLE',
                    'data': {
                        'start': float(word.attrib['start']),
                        'duration': float(word.attrib['length'])
                    }
                }

                entity_key = entity_key + 1
                previous_word = word_text

            block = {
                "text": block_text,
                "type": "unstyled",
                # No named entity support for now
                "entityRanges": block_ranges
            }

            blocks.append(block)

            previous_speaker = speaker
            previous_gender = sentence.attrib[gender_selector]



        if one_file_per_turn:
            destination = get_json_filename(spk_turn, destination)

        output = \
            codecs.open(destination, 'w', encoding='utf-8') \
            if destination else sys.stdout

        write_json(blocks, entity_map, output)

        if output is not sys.stdout:
            output.close()

    finally:
        if output is not sys.stdout:
            output.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create a json file to be used as rawContent '
                    'of https://facebook.github.io/draft-js/')

    parser.add_argument(
        "xml_file",
        help="the xml input file containing the transcription.")

    parser.add_argument(
        "--output_file",
        help="the file you want to write too.")

    parser.add_argument(
        "--one_file_per_turn",
        action="store_true",
        help="split json using one file per speaker turn")

    args = parser.parse_args()

    xml_to_draft_js_content(args.xml_file,
                            args.output_file,
                            args.one_file_per_turn)
