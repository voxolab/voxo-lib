#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os

def make_convert_subtitle(input_file, output_format, subtitle_edit_cli):
    print(input_file)
    print(subtitle_edit_cli)

    os.system("{} /convert {} {}".format(
        subtitle_edit_cli, input_file, output_format))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert subtitle from one format to another. '
        'We are using http://www.nikse.dk/subtitleedit for the conversion')

    parser.add_argument(
        "input_file", 
        help="The subtitle file you want to convert from.")


    # To get the full list :
    # mono SubtitleEdit.exe /convert /list
    parser.add_argument(
        "output_format", 
        help="The subtitle file you want to convert to "
             "(ex: ScenaristClosedCaptions).")

    parser.add_argument(
        "subtitle_edit_cli", 
        help="The full command line to launch SubtitleEdit cli.")

    args = parser.parse_args()

    make_convert_subtitle(
        args.input_file,
        args.output_format,
        args.subtitle_edit_cli)
