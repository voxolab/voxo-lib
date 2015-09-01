#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from convert import xml_to_srt
import argparse

def make_xml_to_srt(xml_file, srt_file):
    xml_to_srt(xml_file, srt_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create subtitle file from xml v2')

    parser.add_argument("xml_file", help="the xml (v2) file corresponding to the demo_file.")
    parser.add_argument("srt_file", help="the file you want to write too.")

    args = parser.parse_args()

    make_xml_to_srt(args.xml_file, args.srt_file)
