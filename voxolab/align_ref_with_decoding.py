#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging, argparse, sys, os, re, subprocess, datetime
import xml.etree.ElementTree as etree    

logger = logging.getLogger(__name__)

def align_ctm(input_file, corrected_file, mwer_segmenter, ref_file = "align-ref.txt", outfile = sys.stdout):

    timestamped_words = []

    with open(input_file, "r", encoding = 'ISO-8859-1') as lines:
        with open(ref_file, "wt") as out_file:
            for line in lines:
                parts = line.split(' ')
                out_file.write(parts[4]+"\n")
                timestamped_words.append((parts[4], parts[2], parts[3]))
            
    align(timestamped_words, corrected_file, mwer_segmenter, ref_file, outfile)

def align_xml(xml_file, corrected_file, mwer_segmenter, ref_file = "align-ref.txt", outfile = sys.stdout, authot_format=False):

    tree = etree.parse(xml_file)  
    root = tree.getroot()                    

    timestamped_words = []

    # Read the xml file, put one word per line
    # Keep alignment values in a list for later use
    logger.info("Opening ref file {}".format(ref_file))
    with open(ref_file, "wt") as out_file:
        if authot_format:
            for sentence in root:
                i=0
                segment=""
                for word in sentence:
                    out_file.write(word.attrib['sel']+"\n")
                    timestamped_words.append((word.attrib['sel'], word.attrib['start'], word.attrib['length']))
        else:
            #Xml v2 new format
            for sentence in root:
                i=0
                segment=""
                for word in sentence:
                    out_file.write(word.attrib['value']+"\n")
                    timestamped_words.append((word.attrib['value'], word.attrib['start'], word.attrib['length']))


    return align(timestamped_words, corrected_file, mwer_segmenter, ref_file, outfile)


def align(timestamped_words, corrected_file, mwer_segmenter, ref_file, outfile):

    hyp_file = "align-hyp.txt"
    result_file = "align-result.txt"

    # Read the ref file and put one word per line too
    with open(corrected_file, "rt") as in_file:
        data=in_file.read().replace('\n', '').replace('\'', '\' ').replace('.', '. ')
        lines = data.split(' ')
        with open(hyp_file, "wt") as out_file:
            for line in lines:
                if not re.match(r'^\s*$', line):
                    out_file.write(line+"\n")

    # Align the 2 files created above
    with open(result_file, "w") as output:
        p = subprocess.Popen("{} -hypfile {} -mref {}".format(mwer_segmenter, hyp_file, ref_file), shell=True, stdout=output)
        ret_code = p.wait()
        output.flush()
        if(ret_code != 0):
            return ret_code

    nb_lines = 0
    nb_words = len(timestamped_words)

    # Read the result file and put the timestamps
    with open(result_file, "r") as in_file:
        for line in in_file:
            if nb_lines > nb_words:
                break

            (word, start, length) = timestamped_words[nb_lines]
            if not re.match(r'^\s*$', line):
                print("{} {:.2f} {:.2f} {}".format(datetime.timedelta(seconds=float(start)), float(start), float(length), line.replace('\n', '')), file=outfile)
            nb_lines += 1

    if(len(timestamped_words) != nb_lines):
        print("Problem when aligning, ref and hyp lines count is different: {} != {}", nb_lines, len(timestamped_words))

    return 0

if __name__ == '__main__':

    #Parse command line
    parser = argparse.ArgumentParser(description='Align files.')

    parser.add_argument("input_file", help="The input file coming from the decoding process.")
    parser.add_argument("ref", help="The .txt file containing the correct words.")
    parser.add_argument("format", choices=["xml", "xml-authot", "ctm"], help="The format of the input file.")
    parser.add_argument("mwer_segmenter", help="The mwerSegmenter binary executable.")
    parser.add_argument("-a", "--authot", help="XML is using the authot format",
                        action="store_true")

    args = parser.parse_args()

    if(args.format == 'xml'):
        align_xml(args.input_file, args.ref, args.mwer_segmenter, authot_format = False)
    elif(args.format == 'xml-authot'):
        align_xml(args.input_file, args.ref, args.mwer_segmenter, authot_format = True)
    else:
        align_ctm(args.input_file, args.ref, args.mwer_segmenter)

