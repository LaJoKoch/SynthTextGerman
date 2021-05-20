"""
Run this after adding a new text source to generate character model: char_freq.cp
Character Model contains the frequency of each character in a specific text source.
reference: https://github.com/ankush-me/SynthText/pull/191/commits/d300b14a847940621cd36a5a29224a37de96e72b#diff-7ef76e519d100d42f04bcfa47109c0870a4010dfc0c69dd44b97a69d72656d2b
"""

from collections import Counter
import pickle
import os.path as osp

data_dir = 'data'
textBase_path = osp.join(data_dir, 'german_textSource/3M_sentences_LeipzigCorpora.txt') # https://www.kaggle.com/rtatman/3-million-german-sentences
charModel_path = osp.join(data_dir, 'models/char_freq.cp')

cnt = 0
with open(textBase_path, 'r', encoding='utf-8') as f:
    c = Counter()
    for line in f.readlines():
        c += Counter(line.strip())
        cnt += len(line.strip())
        # print c
print(cnt)

for key in c:
    c[key] = float(c[key]) / cnt
    print(key, c[key])

d = dict(c)
# print d
with open(charModel_path, 'wb') as f:
    pickle.dump(d, f) 