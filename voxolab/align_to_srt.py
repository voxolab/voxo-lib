#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
from convert import align_to_srt

if __name__ == '__main__':

    #Parse command line
    parser = argparse.ArgumentParser(description='Create srt from aligned file.')

    parser.add_argument("input_file", help="The input file coming from the alignement process.")
    args = parser.parse_args()

    align_to_srt(args.input_file)
