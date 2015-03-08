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

def ne_to_string(ne):
    if ne is None:
        return ne

    parts = ne.split('-')
    name = parts[-1]

    if name.startswith('func'):
        name = 'Fonction'
    elif name.startswith('pers'):
        name = 'Personne'
    elif name.startswith('loc.adm.town'):
        name = 'Ville'
    elif name.startswith('loc.adm.reg'):
        name = 'Région'
    elif name.startswith('loc'):
        name = 'Lieu'
    elif name.startswith('time.date'):
        name = 'Date'
    else:
        name = 'Entitée nommée'

    parts[-1] = name

    return '-'.join(parts)

def seg_ctm_to_json(seg_file, ctm_file, out_file = None, ne_file = None, stm_file = None, input_encoding = 'iso-8859-1', output_encoding = 'iso-8859-1'):

    word_list = []
    named_entities = {}

    # Read ne file if any to add Named Entities information
    if(ne_file):
        with open(ne_file, 'r', encoding=input_encoding) as lines:
            in_ne = False
            previous_start = None
            for line in lines:
                values = line.split(' ')
                word = values[4]
                start = values[2]
                parts = word.split('--')
                ne = parts[1]

                if(ne == 'O' or ne == '-O'):
                    if(in_ne):
                        previous = named_entities[previous_start]
                        named_entities[previous_start] = "E-{}".format(previous)

                    in_ne = False
                    ne = None
                elif(ne.startswith('B-') and in_ne):
                    ne = ne[2:]
                else:
                    in_ne = True

                named_entities[start] = ne_to_string(ne)
                previous_start = start

            # Handle last case
            if(in_ne):
                previous = named_entities[previous_start]
                named_entities[previous_start] = "E-{}".format(previous)

    # Read stm segmentation if any (to cut subtitles)
    cuts = []
    if stm_file:
        stm_input_file = codecs.open(stm_file, 'r', encoding = input_encoding)

        try:
            # For each frame, we will create an entry in a dictionnary
            # It will help the lookup later on
            # We don't really care about memory issues here, should we?
            for line in stm_input_file:
                if line.startswith(';;'):
                    continue

                values = line.split()
                start = int(float(values[3])*100)
                cuts.append(start)
        finally:
            stm_input_file.close()

    cut_index = 0
    nb_cuts = len(cuts)
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
                    if(gender == 'F'):
                        gender = 'Femme'
                    else:
                        gender = 'Homme'

                    for i in range(start, start + duration):
                        frames[i] = gender, values[5], values[7]


                previous_speaker = None
                speaker_turns = []
                speaker_sentences = []
                sentence = []

                for line in ctm:
                    should_cut = False
                    values = line.split()
                    # Use the same start format than in the .seg file
                    start_str = values[2]
                    start = int(float(values[2])*100)

                    speaker_id = frames[start][2].replace('_', ' ').title()
                    speaker_score = None
                    if(speaker_id in scores):
                        speaker_score = float(scores[speaker_id])

                    ne = None
                    if(start_str in named_entities):
                        ne = named_entities[start_str]

                    # New line
                    if(cut_index < nb_cuts):
                        if(start > cuts[cut_index]):
                            should_cut = True 
                            cut_index += 1

                    json_word = {
                        "start":values[2],
                        "word":values[4],
                        "ne": ne
                    }

                    word_list.append(json_word)

                    # Speaker change
                    if(previous_speaker is not None and previous_speaker != speaker_id):
                        speaker_sentences.append(sentence)
                        speaker_turns.append({
                            "id":previous_speaker,
                            "gender":previous_gender,
                            "score": previous_score,
                            "sentences":speaker_sentences
                        })
                        speaker_sentences = []
                        sentence = []
                    elif(should_cut and previous_speaker is not None):
                        #No speaker change but we should put the word on a new line
                        speaker_sentences.append(sentence)
                        sentence = []

                    sentence.append(json_word)
                    previous_speaker = speaker_id
                    previous_gender = frames[start][0]
                    previous_score = speaker_score

                # Add the last sentence and last speaker turn
                speaker_sentences.append(sentence)
                speaker_turns.append({
                    "id":previous_speaker,
                    "gender":previous_gender,
                    "score": previous_score,
                    "sentences":speaker_sentences
                })

                json_output = {}
                #json_output['words'] = word_list
                json_output['speaker_turns'] = speaker_turns

                print(json.dumps(json_output), file=output)


            finally:
                if output is not sys.stdout:
                    output.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a standalone demo (HTML pages).')

    parser.add_argument("ctm_file", help="the ctm file corresponding to the demo_file.")
    parser.add_argument("seg_file", help="the seg file corresponding to the demo_file.")
    parser.add_argument("--output_file", help="the file you want to write too.")
    parser.add_argument("--ne_file", help="the ctm file with named entities.")
    parser.add_argument("--stm_file", help="used to adjoust boundaries.")

    args = parser.parse_args()

    seg_ctm_to_json(args.seg_file, args.ctm_file, args.output_file, args.ne_file, args.stm_file)
