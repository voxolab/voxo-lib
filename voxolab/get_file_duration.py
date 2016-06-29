#!/usr/bin/python
# vim : set fileencoding=utf-8 :

import argparse

from convert import get_duration

def get_file_duration(filename):
    
    (duration, seconds)  = get_duration(filename)
    print(seconds)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Get file duration in seconds using ffmpeg.')

    parser.add_argument(
        "filename",
        help="the input file.")

    args = parser.parse_args()

    get_file_duration(args.filename)
