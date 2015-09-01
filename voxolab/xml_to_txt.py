#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from convert import xml_to_txt
import argparse

def make_xml_to_txt(xml_file, txt_file):
    xml_to_txt(xml_file, txt_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create subtitle file from xml v2')

    parser.add_argument("xml_file", help="the xml (v2) file corresponding to the demo_file.")
    parser.add_argument("txt_file", help="the file you want to write too.")

    args = parser.parse_args()

    make_xml_to_txt(args.xml_file, args.txt_file)
