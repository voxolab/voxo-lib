#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
from convert import recase_ctm

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Recase ctm')

    parser.add_argument("ctm_file", help="the ctm file you want to recase.")
    parser.add_argument("output_file", help="the file you want to write too.")

    parser.add_argument("recase_path",
                        help="path containing sphinx.jar and all the "
                        "recasing files.")

    args = parser.parse_args()

    recase_ctm(os.path.abspath(args.ctm_file),
               os.path.abspath(args.output_file),
               args.recase_path)
