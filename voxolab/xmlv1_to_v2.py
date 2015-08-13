#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from convert import xmlv1_to_v2
import argparse

def make_xmlv1_to_v2(input_file, output_file, input_encoding='ISO8859-1', output_encoding='utf-8'):
    xmlv1_to_v2(input_file, output_file, input_encoding=input_encoding, output_encoding=output_encoding)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert legacy format to the new one.')

    parser.add_argument("xmlv1_file", help="the legacy XML file usually encoded in ISO8859-1.")
    parser.add_argument("xmlv2_file", help="the new XML file you want to write too.")
    parser.add_argument("--input_encoding", help="the encoding of the xmlv1 file.", default='ISO8859-1')
    parser.add_argument("--output_encoding", help="the encoding of the xmlv2 file.", default='UTF-8')

    args = parser.parse_args()

    make_xmlv1_to_v2(args.xmlv1_file, args.xmlv2_file, args.input_encoding, args.output_encoding)

