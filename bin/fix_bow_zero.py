#!/usr/bin/env python3
import sys

filename = sys.argv[1]

in_bigram = False
in_trigram = False

bigrams_without_bow = {}
bigrams_to_fix = {}


# First pass to get the bigrams that need to be fixed
with open(filename, 'r') as arpa_file:
    for line in arpa_file:
        entry = line.rstrip()

        if(entry == "\\2-grams:"):
            in_bigram = True

        if(entry == "\\3-grams:"):
            in_bigram = False
            in_trigram = True

        if in_bigram:
            entries = entry.split()
            if len(entries) < 4:
                bigrams_without_bow[' '.join(entries[1:3])] = entries

        if in_trigram:
            entries = entry.split()

            if len(entries) >= 4:
                bigram = ' '.join(entries[1:3])

                if bigram in bigrams_without_bow:
                    bigrams_to_fix[bigram] = True

# Second pass to actually fix the ngram

in_bigram = False
in_trigram = False

with open(filename, 'r') as arpa_file:
    for line in arpa_file:
        entry = line.rstrip()

        if(entry == "\\2-grams:"):
            in_bigram = True

        if(entry == "\\3-grams:"):
            in_bigram = False
            in_trigram = True

        if(in_bigram):
            entries = entry.split()
            bigram = ' '.join(entries[1:3])
            if bigram in bigrams_to_fix:
                print("{}\t{} {}\t 0"
                      .format(entries[0], entries[1], entries[2]))
            else:
                print(entry)
        else:
            print(entry)

