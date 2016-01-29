#!/bin/env python
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
from lxml import etree

def seg_ctm_to_xml(seg_file, ctm_file, out_file = None, input_encoding = 'utf-8', output_encoding = 'utf-8'):

    word_list = []
    named_entities = {}

    # Read stm segmentation if any (to cut subtitles)
    cuts = []
    cut_index = 0
    first_frame = None
    show = ""

    with open(seg_file, 'r', encoding=input_encoding) as seg:
        with open(ctm_file, 'r', encoding=input_encoding) as ctm:

            output = codecs.open(out_file, 'w', encoding = output_encoding) if out_file else sys.stdout

            try:
                # For each frame, we will create an entry in a dictionnary
                # It will help the lookup later on
                # We don't really care about memory issues here, should we?
                frames = {}
                scores = {}

                for line in seg:

                    # Skip empty lines
                    if(line.rstrip() == ''):
                        continue

                    # This is a comment line with some information about the scores
                    if line.startswith(';;'):
                        match_obj = re.match(r'^;; cluster (\S+).*neuralScore = (\S+).*', line)
                        if(match_obj):
                            cluster = match_obj.group(1)
                            neural_score = match_obj.group(2)
                            scores[cluster] = neural_score
                        continue

                    values = line.split()
                    start = int(values[2])
                    duration = int(values[3])
                    gender = values[4]

                    # We consider that one entry in the seg file should be one "sentence"
                    cuts.append(start)

                    if(gender == 'F'):
                        gender = 'Female'
                    else:
                        gender = 'Male'

                    if(first_frame is None):
                        first_frame = start

                    for i in range(start, start + duration):
                        frames[i] = gender, values[5], values[7]


                previous_speaker = None
                speaker_turns = []
                speaker_sentences = []
                sentence = []
                nb_cuts = len(cuts)

                for line in ctm:


                    if(line.rstrip() == ''):
                        continue 

                    should_cut = False
                    values = line.split()

                    if(values[4] == '<unk>' or values[4] == '<eps>'):
                        continue 

                    # Use the same start format than in the .seg file
                    show = values[0]
                    start_str = values[2]
                    start = int(float(values[2])*100)

                    length_str = values[3]
                    length = int(float(length_str)*100)

                    # Skip words if we don't have the seg for it
                    if(start < first_frame):
                        continue

                    # Get the speaker if we have an entry for it in the .seg file
                    if(start in frames):
                        speaker_id = frames[start][2].replace('_', ' ').title()
                        quality = frames[start][1]
                    else:
                        speaker_id = None
                        quality = None

                    speaker_score = None
                    if(speaker_id in scores):
                        speaker_score = float(scores[speaker_id])

                    # New line
                    if(cut_index < nb_cuts):
                        if(start > cuts[cut_index]):
                            should_cut = True 
                            cut_index += 1

                    word = {
                        "start":values[2],
                        "length":values[3],
                        "word":values[4],
                        "score":values[5]
                    }

                    word_list.append(word)

                    # Speaker change
                    if(previous_speaker is not None and previous_speaker != speaker_id):
                        speaker_sentences.append(sentence)
                        speaker_turns.append({
                            "id":previous_speaker,
                            "gender":previous_gender,
                            "score": previous_score,
                            "quality": previous_quality,
                            "sentences":speaker_sentences
                        })
                        speaker_sentences = []
                        sentence = []
                    elif(should_cut and previous_speaker is not None):
                        #No speaker change but we should put the word on a new line
                        speaker_sentences.append(sentence)
                        sentence = []

                    sentence.append(word)
                    previous_speaker = speaker_id
                    previous_quality = quality
                    if(start in frames):
                        previous_gender = frames[start][0]
                    else:
                        previous_gender = None

                    previous_score = speaker_score

                # Add the last sentence and last speaker turn
                speaker_sentences.append(sentence)
                speaker_turns.append({
                    "id":previous_speaker,
                    "gender":previous_gender,
                    "score": previous_score,
                    "quality": previous_quality,
                    "sentences":speaker_sentences
                })

                json_output = {}

                root = etree.Element('show', name=show)

                for turn in speaker_turns:
                    speaker = turn['id']
                    gender = turn['gender']
                    score = turn['score']
                    sentences = turn['sentences']
                    quality = turn['quality']

                    if(quality == 'T'):
                        quality='Phone'
                    else:
                        quality='Studio'

                    for sentence in sentences:
                        # another child with text
                        #<sentence end="32.61" speaker="S105" gender="Female" start="15.12" type="Studio">
                        child_sentence = etree.Element('sentence', speaker=speaker, gender=gender, type=quality)
                        root.append(child_sentence)
                        for word in sentence:
                            child_word = etree.Element('word', length=word['length'], start=word['start'], value=word['word'], score=word['score'])
                            child_sentence.append(child_word)

                # pretty string
                s = """<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE SHOW PUBLIC "-//VOXOLAB//DTD XML v2.0//EN"
        "http://docs.voxolab.com/voxolab-xmlv2.dtd">
"""
                s += etree.tostring(root, pretty_print=True, encoding='unicode')
                print(s, file=output)

            finally:
                if output is not sys.stdout:
                    output.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a standalone demo (HTML pages).')

    parser.add_argument("ctm_file", help="the ctm file corresponding to the demo_file.")
    parser.add_argument("seg_file", help="the seg file corresponding to the demo_file.")
    parser.add_argument("--output_file", help="the file you want to write too.")

    args = parser.parse_args()

    seg_ctm_to_xml(args.seg_file, args.ctm_file, args.output_file)
