#!/usr/bin/python
# vim : set fileencoding=utf-8 :
 
#
# mergeSegToCtm.py
#
# Enhance the CTM file by adding extra fields with the diarisation
# information
#
# First argument is the seg file
# Second argument is the ctm file
#
import sys, codecs, argparse, json, re

def seg_ctm_to_txt(seg_file, ctm_file, out_file = None, input_encoding = 'iso-8859-1', output_encoding = 'utf-8'):

    word_list = []
    nb_seg = 0
    segs = []

    with open(seg_file, 'r', encoding=input_encoding) as seg:

        for line in seg:
            # This is a comment line with some information about the scores
            if line.startswith(';;'):
                continue

            values = line.split()
            start = int(values[2])/100
            end = (int(values[2]) + int(values[3]))/100
            gender = values[4]
            if(gender == 'F'):
                gender = 'Femme'
            else:
                gender = 'Homme'

            speaker = values[7]

            segs.append((start, end, gender, speaker))


    # Sort by start
    segs.sort(key=lambda seg: seg[0])

    with open(ctm_file, 'r', encoding=input_encoding) as ctm:

        output = codecs.open(out_file, 'w', encoding = output_encoding) if out_file else sys.stdout

        try:
            previous_speaker = None
            sentence = []
            last_seg = 0
            nb_word = 0
            previous_word = None

            for line in ctm:

                if(last_seg >= len(segs)):
                    break

                seg = segs[last_seg]
                values = line.split()

                # Use the same start format than in the .seg file
                start_str = values[2]
                start = int(float(values[2]))
                end_str = values[3]
                end = int(float(values[3]))
                middle = (start + end)/2
                word = values[4]

                if(word == 'euh' or (word.startswith('<') and word.endswith('>'))):
                    continue

                speaker_id = segs[last_seg][3].replace('_', ' ').title()

                # Speaker change
                if(previous_speaker != speaker_id):
                    print("\n\n– " + speaker_id + " :", file=output)

                if(middle >= seg[0] and middle <= seg[1]):
                    # Handle spaces after ' and before -
                    if(previous_word is not None and word is not None and not previous_word.endswith("'") and not word.startswith("-")):
                        print(" ", file=output, end="")
                    print(word, file=output, end="")
                else:
                    while(middle > seg[1] and last_seg < len(segs)):
                        last_seg = last_seg + 1
                        seg = segs[last_seg]


                    if(middle >= seg[0] and middle <= seg[1]):
                        print("\n" + word + " ", file=output, end="")


                #sentence.append(word)

                previous_speaker = speaker_id
                previous_gender = segs[last_seg][2]
                previous_word = word


            #print(previous_speaker, file=output)
            #print(' '.join(sentence), file=output)

        finally:
            if output is not sys.stdout:
                output.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a txt file.')

    parser.add_argument("ctm_file", help="the ctm file corresponding to the demo_file.")
    parser.add_argument("seg_file", help="the seg file corresponding to the demo_file.")
    parser.add_argument("--output_file", help="the file you want to write too.")

    args = parser.parse_args()

    seg_ctm_to_txt(args.seg_file, args.ctm_file, args.output_file)
