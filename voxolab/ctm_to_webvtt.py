#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from convert import ctm_to_webvtt
import argparse

def make_ctm_to_webvtt(ctm_file, srt_file, seg_file, stm):
    ctm_to_webvtt(ctm_file, srt_file, seg_file, stm)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create subtitle file from ctm')

    parser.add_argument("ctm_file", help="the ctm file corresponding to the demo_file.")
    parser.add_argument("webvtt_file", help="the file you want to write too.")
    parser.add_argument("--seg_file", help="the segmentation file corresponding to the demo file. Will improve the subtitle segmentation.")
    parser.add_argument("--stm_file", help="the segmentation file corresponding to the demo file. Will improve the subtitle segmentation.")

    args = parser.parse_args()

    make_ctm_to_webvtt(args.ctm_file, args.webvtt_file, args.seg_file, args.stm_file)
