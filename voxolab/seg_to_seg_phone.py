#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import re
import codecs

def make_seg_to_seg_phone(in_seg_file, out_seg_file):
    with open (in_seg_file, "r") as in_file:
        data=in_file.read()
        data_sub = re.sub(r'(^.* 1 \d+ \d+ .? )(.?)( .? .*\n)', r'\1T\3', data, flags=re.MULTILINE)

    with open(out_seg_file, 'w') as f:  
        f.write(data_sub)  

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Force seg file to phone')

    parser.add_argument("in_seg_file", help="the input seg file.")
    parser.add_argument("out_seg_file", help="the output seg file.")

    args = parser.parse_args()

    make_seg_to_seg_phone(args.in_seg_file, args.out_seg_file)
