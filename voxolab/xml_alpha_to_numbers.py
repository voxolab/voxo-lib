#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, subprocess, sys, os, codecs, copy
import xml.etree.ElementTree as etree    
from xml.dom import minidom

number_to_alpha = {
        "0":"zéro",
        "1":"un",
        "2":"deux",
        "3":"trois",
        "4":"quatre",
        "5":"cinq",
        "6":"six",
        "7":"sept",
        "8":"huit",
        "9":"neuf",
        "10":"dix",
        "11":"onze",
        "12":"douze",
        "13":"treize",
        "14":"quatorze",
        "15":"quinze",
        "16":"seize",
        "20":"vingt",
        "21":"vingt-et-un",
        "30":"trente",
        "31":"trente-et-un",
        "40":"quarante",
        "41":"quarante-et-un",
        "50":"cinquante",
        "51":"cinquante-et-un",
        "60":"soixante",
        "70":"soixante-dix",
        "71":"soixante-et-onze",
        "72":"soixante-douze",
        "73":"soixante-treize",
        "74":"soixante-quatorze",
        "75":"soixante-quinze",
        "76":"soixante-seize",
        "77":"soixante-dix-sept",
        "78":"soixante-dix-huit",
        "79":"soixante-dix-neuf",
        "80":"quatre-vingt",
        "90":"quatre-vingt-dix",
        "91":"quatre-vingt-onze",
        "92":"quatre-vingt-douze",
        "93":"quatre-vingt-treize",
        "94":"quatre-vingt-quatorze",
        "95":"quatre-vingt-quinze",
        "96":"quatre-vingt-seize",
        "97":"quatre-vingt-dix-sept",
        "98":"quatre-vingt-dix-huit",
        "99":"quatre-vingt-dix-neuf",
        "1000":"mille",
        "100":"cent",
        "1001":"milles",
        "101":"cents",
        "1111":"virgule"
}


# Create the reverse map
alpha_to_number = {}
for number, alpha in number_to_alpha.items():

    alpha_to_number[alpha] = number

    if alpha.endswith('e'):
        alpha_to_number[alpha[0:-1] + "ième"] = number + "ème"
    else:
        alpha_to_number[alpha + "ième"] = number + "ème"

alpha_to_number["cinquième"]="5ème";
alpha_to_number["neuvième"]="9ème";

ten_with_and = ['vingt', 'trente', 'quarante', 'cinquante', 'soixante']

def convert_alpha_to_number(alpha, convert_script, output_encoding):
    # Call the convert script
    script_dir = os.path.dirname(os.path.realpath(convert_script))
    convert = subprocess.Popen([convert_script, alpha], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=script_dir)       
    result, err = convert.communicate()
    if(err != b''):
        # Conversion failed put the words as if
        result = alpha
    else:
        result = result.rstrip().decode(output_encoding)
                    

    return result

def xml_alpha_to_numbers_from_file(xml_file, convert_script, destination = None, source_encoding = 'ISO-8859-1', output_encoding = 'ISO-8859-1'):
    with open(xml_file, "r", encoding=source_encoding) as f:
        xml_string = f.read()
        root = etree.fromstring(xml_string)  
        xml_alpha_to_numbers(root, convert_script)


def xml_alpha_to_numbers(root, convert_script):


    def check_special_cases(word, sentence, j, nb_words):
        """TODO: Preprocess values to handle special cases like
        "cinquante et un" => "cinquante-et-un", 
        "soixante et onze" => "soixante-et-onze".

        :word: The xml object representing a word
        :sentence: The xml object representing a sentence
        :j: the current word index in the sentence
        :nb_words: total of words in the sentence
        :returns: side effect 4ever

        """

        w = word.attrib['sel']

        # The current word may be a special case with "et"
        # cinquante et un (51), soixante et onze (71), …
        if(w in ten_with_and and \
                nb_words > j + 2):
            next_word = sentence[j+1].attrib['sel']
            next_next_word = sentence[j+2].attrib['sel']

            # Change "cinquante et un" to "cinquante-et-un"
            if(next_word == 'et' and next_next_word in ['un', 'onze']):
                new_value = "{}-{}-{}".format(w, next_word, next_next_word)
                word.set('sel', new_value)
                sentence.remove(sentence[j+1])
                sentence.remove(sentence[j+1])

    def is_number(word):
        """TODO: Check if the current word is well-formed number

        :word: The xml object representing a word
        :sentence: The xml object representing a sentence
        :j: the current word index in the sentence
        :nb_words: total of words in the sentence
        :returns: TODO

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

    while(True):

        modified = False

        for i, sentence in enumerate(root):
            nb_words = len(sentence)
            for j, word in enumerate(sentence):

                word.set('length', "{:.2f}".format(float(word.attrib['length'])))
                check_special_cases(word, sentence, j, nb_words)

                # If the current word is a number, let's try to get
                # the next words and see if we can construct a number
                # from it

                w = word.attrib['sel']
                idx = j

                if(is_number(w)):
                    in_number = True
                    while(in_number):
                        if(idx+1 < nb_words):
                            next_word = sentence[idx+1].attrib['sel']
                            if(is_number(w + "-" + next_word)):
                                w = w + "-" + next_word
                                idx = idx + 1
                            else:
                                in_number = False
                        else:
                            in_number = False
                # It's seems we found a valid number to transform
                if(w in alpha_to_number):
                    print("{} is different from {}".format(w, word.attrib['sel']))
                    print("we took {} words {} {}".format(idx - j, j, idx))

                    last_word = sentence[idx]
                    last_word_end = float(last_word.attrib['start']) + float(last_word.attrib['length'])
                    word.set('sel', alpha_to_number[w])
                    word.set('length', "{:.2f}".format(last_word_end - float(word.attrib['start'])))
                    # Delete the next words we want to merge with the current one
                    for k in range(j+1, idx+1):
                        print("Removing {}".format(sentence[k].attrib['sel']))
                        sentence.remove(sentence[k])

                    modified = True

        if(not modified):
            break

    xml_string = etree.tostring(root)
    reparsed = minidom.parseString(xml_string)
    print('\n'.join([line for line in reparsed.toprettyxml(indent=' '*2).split('\n') if line.strip()]))

    return root

def ctm_alpha_to_numbers(ctm_file, convert_script, destination = None, source_encoding = 'ISO-8859-1', output_encoding = 'ISO-8859-1'):

    # Just read the input ctm
    ctm_lines = []
    with open(ctm_file, "r", encoding=source_encoding) as lines:
        for line in lines:
            parts = line.rstrip().split(' ')
            show = parts[0]
            chan = parts[1]
            start = parts[2]
            duration = parts[3]
            word = parts[4]
            score = parts[5]
            ctm_lines.append((show, chan, start, duration, word, score))

    # This is what we will put in our new ctm
    new_ctm_lines = []

    is_in_alpha=False
    alpha_to_transform=''
    alpha_start_index=-1

    next_show=next_chan=next_start=next_duration=next_word=next_score=None
    nb_lines = len(ctm_lines)

    for i, line in enumerate(ctm_lines):
        
        # The current line
        show, chan, start, duration, word, score = line

        # If the current word is an alpha number
        if(word in alpha_to_number):
            # We were already in an alpha number
            if(is_in_alpha):
                alpha_to_transform += "-"
            else:
                alpha_start_index=i

            alpha_to_transform += word
            is_in_alpha=True
        # If the current word is not an alpha number
        else:
            # We were in an alpha number before
            if(is_in_alpha):
                a_show, a_chan, a_start, a_duration, a_word, a_score = ctm_lines[alpha_start_index]
                result = convert_alpha_to_number(alpha_to_transform, convert_script, output_encoding)

                add_result = True
                # Checking for pour cent/%
                if(result == "100"):
                    if(len(new_ctm_lines) > 1):
                        p_show, p_chan, p_start, p_duration, p_word, p_score = new_ctm_lines[-1]
                        if(p_word == "pour"):
                            pp_show, pp_chan, pp_start, pp_duration, pp_word, pp_score = new_ctm_lines[-2]
                            # It's a small number that we should convert again
                            if(pp_word in alpha_to_number):
                                pp_word = convert_alpha_to_number(pp_word, convert_script, output_encoding)
                            try:
                                # Check if we can convert it to a number
                                value = float(pp_word.replace(',','.'))

                                # Don't convert value > to 1000
                                # it's certainly an error
                                if(value < 1000):
                                    # Remove the last entry that contains "pour"
                                    new_ctm_lines.pop()
                                    # Add % to the number
                                    new_ctm_lines[-1] = (pp_show, pp_chan, pp_start, pp_duration, pp_word + '%', pp_score)

                                    # We should not add the current word
                                    add_result = False


                            except:
                                pass



                # Don't convert small numbers
                if(len(result) == 1 and int(result) < 10):
                    result = alpha_to_transform


                # Add the new word
                if(add_result):
                    new_ctm_lines.append((a_show, a_chan, a_start, a_duration, result, a_score))

                # Reset values
                alpha_to_transform=""
                alpha_start_index_at=-1

            new_ctm_lines.append(line)
            is_in_alpha=False

    # Write to a file if provided, otherwise write to stdout
    output = codecs.open(destination, 'w', encoding = output_encoding) if destination else sys.stdout

    try:
        for new_line in new_ctm_lines:
            show, chan, start, duration, word, score = new_line
            print(' '.join(str(i) for i in new_line), file=output)
    finally:
        if output is not sys.stdout:
            output.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transform alphanumerics to numbers')

    parser.add_argument("xml_file", help="the xml file.")
    parser.add_argument("xml_file_output", help="the destination xml file.")
    parser.add_argument("convert_script", help="path to the script used to convert alphanumerics to numbers.")

    args = parser.parse_args()

    xml_alpha_to_numbers_from_file(args.xml_file, os.path.realpath(args.convert_script), args.xml_file_output)

