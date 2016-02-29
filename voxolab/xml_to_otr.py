#!/usr/bin/python
# vim : set fileencoding=utf-8 :

import xml.etree.ElementTree as etree
 
#
# Create json file (for demo purpose) based on the xml file
#
import sys, codecs, argparse, json, re

def xml_to_otr(xml_file, destination, speakers=False):
    """Convert an xml file (v1 or v2) to a json file in the oTranscribe format

    :xml_file: the path of the input xml file
    :destination: the path of the output otr file
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

        json_output = {}

        html = "";
        for i, sentence in enumerate(root):
            if(i != 0):
                html += "</p>";

            html += "<p>";

            speaker = sentence.attrib[spk_selector]
            words = []

            if speakers:
                # Speaker change
                if(speaker != previous_speaker):
                    html += "<p><strong>Locuteur {} :</strong>".format(speaker);
                else:
                    html += "<p>";
            else:
                html += "<p>";

            nb_words = len(sentence)
            for j, word in enumerate(sentence):
                value = word.attrib[word_selector]
                space_after = " "
                if(value.endswith("'") or \
                   (j+1 < nb_words and sentence[j+1].attrib[word_selector].startswith('-'))):
                    space_after=""

                html += "<span class=\"word\" data-start=\"{start}\">{value}{space}</span>".format(start=word.attrib['start'], value=value, space=space_after)

            previous_speaker = speaker
            previous_gender = sentence.attrib[gender_selector]


        html += "</p>"
        #import pprint; pprint.pprint(html)

        json_output['text'] = html
        json_output['media_source'] = ""
        print(json.dumps(json_output), file=output)


    finally:
        if output is not sys.stdout:
            output.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a json file in the oTranscribe format (.otr) based on an xml.')

    parser.add_argument("xml_file", help="the xml input file containing the transcription.")
    parser.add_argument("--output_file", help="the file you want to write too.")
    parser.add_argument('--speakers', dest='speakers', action='store_true')

    args = parser.parse_args()

    xml_to_otr(args.xml_file, args.output_file, args.speakers)
