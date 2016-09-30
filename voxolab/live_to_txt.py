#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

def make_live_to_txt(live_file, txt_file, source_encoding='UTF-8'):

    """
    Convert a special ctm file (with the segmentation information in it) to a 
    json file used for the web demo
    """

    new_sentence = False
    words = []
    start = None

    with open(live_file, "r", encoding=source_encoding) as live_f:
        live_content = live_f.readlines()
        for line in live_content:
            if "###" in line and len(words) > 0:
                print("{} : {}".format(start," ".join(words)))
                start = None
                words = []
                pass
            else:
                parts = line.split(" ")
                if len(parts) == 2:
                    word_parts = parts[1].replace("(", "").split(",")
                    timestamp = parts[0].strip()
                    if start == None:
                        start = timestamp
                    word = word_parts[0]
                    # Filter fillers
                    if("<" not in word):
                        words.append(word)


        print("{} : {}".format(start, " ".join(words)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create txt file from live output')

    parser.add_argument("live_file", help="the xml (v2) file corresponding to the demo_file.")
    parser.add_argument("txt_file", help="the file you want to write too.")

    args = parser.parse_args()

    make_live_to_txt(args.live_file, args.txt_file)
