#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
import os
import subprocess
import sys

import xml.etree.ElementTree as etree
from xml.dom import minidom

number_to_alpha = {
    "0": "zéro",
    "1": "un",
    "2": "deux",
    "3": "trois",
    "4": "quatre",
    "5": "cinq",
    "6": "six",
    "7": "sept",
    "8": "huit",
    "9": "neuf",
    "00": "zéro-zéro",
    "01": "zéro-un",
    "02": "zéro-deux",
    "03": "zéro-trois",
    "04": "zéro-quatre",
    "05": "zéro-cinq",
    "06": "zéro-six",
    "07": "zéro-sept",
    "08": "zéro-huit",
    "09": "zéro-neuf",
    "10": "dix",
    "11": "onze",
    "12": "douze",
    "13": "treize",
    "14": "quatorze",
    "15": "quinze",
    "16": "seize",
    "20": "vingt",
    "21": "vingt-et-un",
    "30": "trente",
    "31": "trente-et-un",
    "40": "quarante",
    "41": "quarante-et-un",
    "50": "cinquante",
    "51": "cinquante-et-un",
    "60": "soixante",
    "61": "soixante-et-un",
    "70": "soixante-dix",
    "71": "soixante-et-onze",
    "72": "soixante-douze",
    "73": "soixante-treize",
    "74": "soixante-quatorze",
    "75": "soixante-quinze",
    "76": "soixante-seize",
    "77": "soixante-dix-sept",
    "78": "soixante-dix-huit",
    "79": "soixante-dix-neuf",
    "80": "quatre-vingt",
    "90": "quatre-vingt-dix",
    "91": "quatre-vingt-onze",
    "92": "quatre-vingt-douze",
    "93": "quatre-vingt-treize",
    "94": "quatre-vingt-quatorze",
    "95": "quatre-vingt-quinze",
    "96": "quatre-vingt-seize",
    "97": "quatre-vingt-dix-sept",
    "98": "quatre-vingt-dix-huit",
    "99": "quatre-vingt-dix-neuf",
    "1000": "mille",
    "100": "cent",
    "1001": "milles",
    "101": "cents",
    "1111": "virgule"
}


# Create the reverse map
alpha_to_number = {}
for number, alpha in number_to_alpha.items():

    alpha_to_number[alpha] = number

    if alpha.endswith('e'):
        alpha_to_number[alpha[0:-1] + "ième"] = number + "ème"
    else:
        alpha_to_number[alpha + "ième"] = number + "ème"

alpha_to_number["cinquième"] = "5ème"
alpha_to_number["neuvième"] = "9ème"

ten_with_and = ['vingt', 'trente', 'quarante', 'cinquante', 'soixante']

# Words you don't want to convert
stop_list = ['zéro', 'un', 'deux', 'trois', 'quatre', 'cinq',
             'six', 'sept', 'huit', 'neuf']


def convert_alpha_to_number(alpha, convert_script, output_encoding):
    # Call the convert script
    script_dir = os.path.dirname(os.path.realpath(convert_script))
    convert = subprocess.Popen([convert_script, alpha],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd=script_dir)

    result, err = convert.communicate()
    if(err != b''):
        # Conversion failed put the words as if
        result = alpha
    else:
        result = result.rstrip().decode(output_encoding)

    return result


def convert_number_to_alpha(number, convert_script, output_encoding):
    # Call the convert script
    script_dir = os.path.dirname(os.path.realpath(convert_script))
    convert = subprocess.Popen([convert_script, alpha],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               cwd=script_dir)

    result, err = convert.communicate()
    if(err != b''):
        # Conversion failed put the words as if
        result = alpha
    else:
        result = result.rstrip().decode(output_encoding)

    return result


def xml_alpha_to_numbers_from_file(
        xml_file, alpha_to_number_script, number_to_alpha_script,
        destination=None, source_encoding='ISO-8859-1',
        output_encoding='ISO-8859-1'):

    with open(xml_file, "r", encoding=source_encoding) as f:
        xml_string = f.read()
        root = etree.fromstring(xml_string)

        if(len(root.findall(".//word[@value]")) > 0):
            # version = 'v2'
            encoding = 'utf-8'
        elif(len(root.findall(".//word[@sel]")) > 0):
            # version = 'v1'
            encoding = 'iso-8859-1'
        else:
            raise Exception("Unknown XML format")

        xml_alpha_to_numbers(
            root, alpha_to_number_script, number_to_alpha_script)

        xml_string = etree.tostring(root)
        reparsed = minidom.parseString(xml_string)
        pretty_xml = '\n'.join(
            [
                line for line in reparsed.toprettyxml(indent=' '*4).split('\n')
                if line.strip()
            ]
        )

        # Write to a file if provided, otherwise write to stdout
        output = codecs.open(destination, 'w', encoding=output_encoding) \
            if destination else sys.stdout

        try:
            pretty_xml = pretty_xml.replace(
                '<?xml version="1.0"',
                '<?xml version="1.0" encoding="{}"'.format(encoding))

            print(pretty_xml, file=output)
        finally:
            if output is not sys.stdout:
                output.close()


def check_special_cases(word, sentence, j, nb_words, word_selector):
    """TODO: Preprocess values to handle special cases like
    "cinquante et un" => "cinquante-et-un",
    "soixante et onze" => "soixante-et-onze".

    :word: The xml object representing a word
    :sentence: The xml object representing a sentence
    :j: the current word index in the sentence
    :nb_words: total of words in the sentence
    :returns: True if we have modified the sentence

    """

    w = word.attrib[word_selector].lower()

    # The current word may be a special case with "et"
    # cinquante et un (51), soixante et onze (71), …

    modified = False
    if(w in ten_with_and and nb_words > j + 2):
        next_word = sentence[j+1].attrib[word_selector].lower()
        next_next_word = sentence[j+2].attrib[word_selector].lower()

        # Change "cinquante et un" to "cinquante-et-un"
        if(next_word == 'et' and next_next_word in ['un', 'onze']):
            new_value = "{}-{}-{}".format(w, next_word, next_next_word)
            word.set(word_selector, new_value)
            sentence.remove(sentence[j+1])
            sentence.remove(sentence[j+1])
            modified = True

    return modified


def is_number(word):
    """TODO: Check if the current word is well-formed number

    :word: The xml object representing a word
    :sentence: The xml object representing a sentence
    :j: the current word index in the sentence
    :nb_words: total of words in the sentence
    :returns: Boolean

    """
    if(word in alpha_to_number):
        return True
    elif('-' in word):
        parts = word.split('-')
        for part in parts:
            if(part in alpha_to_number):
                pass
            else:
                return False

        return True
    else:
        return False


def is_well_formed_number(
        word, alpha_to_number_script, number_to_alpha_script):

    """TODO: Check if the alpha number is a well formed
    one by converting both ways.

    :word: The word to check (alpha number)
    :alpha_to_number_script: the script path to convert from an alpha
        to a number
    :number_to_alpha_script: the script path to convert from a number
        to an alpha
    :returns: Boolean

    """

    to_number = convert_alpha_to_number(
        word, alpha_to_number_script, 'utf-8')

    to_alpha = convert_alpha_to_number(
        to_number, number_to_alpha_script, 'utf-8')

    if(word == to_alpha):
        return True
    else:
        return False

    return True


def xml_alpha_to_numbers(root, alpha_to_number_script, number_to_alpha_script):

    # Check xml version and force encoding for compatibility purpose
    if(len(root.findall(".//word[@value]")) > 0):
        word_selector = 'value'
        # spk_selector = 'speaker'
        # gender_selector = 'gender'
    elif(len(root.findall(".//word[@sel]")) > 0):
        word_selector = 'sel'
        # spk_selector = 'locuteur'
        # gender_selector = 'sexe'
    else:
        raise Exception("Unknown XML format")

    while(True):

        modified = False

        for i, sentence in enumerate(root):
            nb_words = len(sentence)
            for j, word in enumerate(sentence):

                word.set(
                    'length',
                    "{:.2f}".format(float(word.attrib['length'])))

                # Recompute the number of words if we have
                # modified the sentence
                if(check_special_cases(
                        word, sentence, j, nb_words, word_selector)):
                    nb_words = len(sentence)

                # If the current word is a number, let's try to get
                # the next words and see if we can construct a number
                # from it

                w = word.attrib[word_selector].lower()
                idx = j

                number_found = False

                if(is_number(w)):
                    in_number = True
                    number_found = True
                    while(in_number):
                        if(idx+1 < nb_words):
                            next_word = \
                                sentence[idx+1].attrib[word_selector].lower()
                            if(is_number(w + "-" + next_word)):
                                w = w + "-" + next_word
                                idx = idx + 1
                            else:
                                in_number = False
                        else:
                            in_number = False

                # It's seems we found a valid number to transform
                if((number_found or w in alpha_to_number) and
                    w not in stop_list and
                    is_well_formed_number(
                        w, alpha_to_number_script, number_to_alpha_script)):

                    last_word = sentence[idx]
                    last_word_end = float(last_word.attrib['start']) + \
                        float(last_word.attrib['length'])

                    word.set(
                        word_selector,
                        convert_alpha_to_number(
                            w, alpha_to_number_script, 'iso-8859-1'))
                    word.set(
                        'length',
                        "{:.2f}".format(
                            last_word_end - float(word.attrib['start'])))

                    # Delete the next words we want to merge with
                    # the current one
                    for k in range(j+1, idx+1):
                        sentence.remove(sentence[j+1])

                    nb_words = len(sentence)

                    modified = True

        if(not modified):
            break

    return root


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Transform alphanumerics to numbers')

    parser.add_argument("xml_file", help="the xml file.")
    parser.add_argument("xml_file_output", help="the destination xml file.")
    parser.add_argument("alpha_to_number_script",
                        help="path to the script used to convert alphanumerics"
                        " to numbers.")
    parser.add_argument("number_to_alpha_script",
                        help="path to the script used to convert numbers to"
                        " alphanumerics.")

    args = parser.parse_args()

    xml_alpha_to_numbers_from_file(
        args.xml_file,
        os.path.realpath(args.alpha_to_number_script),
        os.path.realpath(args.number_to_alpha_script),
        args.xml_file_output)
