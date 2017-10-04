# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 20:19:18 2017

@author: kyleh
"""

from nltk.corpus import wordnet as wn
from nltk.corpus import semcor
import argparse
import random
import semcor_chunk as sc

parser=argparse.ArgumentParser()
parser.add_argument('ndx', type=int, action='store', default='1')
parser.add_argument('-nym', dest='nym', action='store', default='synonym')
args = parser.parse_args()

nym=args.nym
ndx=int(args.ndx)

sents=semcor.tagged_sents(tag='sem')
#random.seed(8)
sent=sents[ndx]
print(' '.join(semcor.sents()[ndx]))

newSent=[]
for word in sent:
    if(type(word)==list):
        newSent.append(word[0])
        continue
    if type(word.label())==str:
        continue
    chunk=sc.semcor_chunk(word).get_syn_set()
#    print(chunk)
    if chunk is None:
        newSent.append(word.lemmas()[0].name())
#        print(newSent)
        continue
#    print(nyms)
    if nym=='synonym':
        nyms=wn.synsets(chunk.lemmas()[0].name())
        if len(nyms)==0:
            newSent.append(word.lemmas()[0].name())
            continue
        newSent.append(nyms[random.randint(0,len(nyms)-1)].lemmas()[0].name())
#        print(newSent)
    elif nym=='hypernym':
        nyms=chunk.hypernyms()
        if len(nyms)==0:
            newSent.append(word.label().name())
            continue
#        print(nyms)
        newSent.append(nyms[random.randint(0,len(nyms)-1)].lemmas()[0].name())
    elif nym=='hyponym':
        nyms=chunk.hyponyms()
        if len(nyms)==0:
            newSent.append(word.label().name())
            continue
#        print(nyms)
        newSent.append(nyms[random.randint(0,len(nyms)-1)].lemmas()[0].name())
print(' '.join(newSent))