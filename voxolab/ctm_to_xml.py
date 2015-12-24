#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from voxolab.sphinx import Sphinx
from voxolab import convert

def ctm_to_xml(ctm_file, recasing_path = "/home/vjousse/usr/fac/decodeur/majAuto", recase = False):

    convert.recase_ctm(ctm_file, ctm_file_maj, recasing_path)
    s.make_xml(latp5_dir, iv_seg_file, xml_file, ctm_file_maj)
    pass

if __name__ == '__main__':

    #Parse command line
    parser = argparse.ArgumentParser(description='Convert a ctm to xml format. Optionnally recase the ctm.')

    parser.add_argument("ctm", help="The ctm file coming from the decoding process.")
    parser.add_argument("-r", "--recase", help="Recase the ctm file.",
                        action="store_true")

    args = parser.parse_args()

    ctm_to_xml(args.ctm, args.recase)
