
#%%
import codecs
from unidecode import unidecode
with codecs.open("pt-br/dicio","r", encoding="utf-8") as f:
    words = f.read().split()


# %%
fiveletter = [unidecode(w) for w in words if len(w)==5]
# %%
fiveletter

#%%
alphabet = "abcdefghijklmnopqrstuvwxyz"
fiveletter = [word for word in fiveletter 
              if all(letter in alphabet for letter in word)]
# %%
import numpy as np
nums = list(map(lambda word: list(map(lambda letter: alphabet.find(letter), word)), fiveletter))
print(nums)
# %%
vecs = np.stack(nums)
print(vecs)
# %%
def to_setvector(wordVec):
    v = np.zeros(len(alphabet))
    letters = list(set(wordVec))
    v[letters] = 1
    return v

def letters(setVector):
    idxs = np.where(setVector !=0)[0]
    return [alphabet[i] for i in idxs]

# %%
setVecs = np.stack([ to_setvector(v) for v in vecs])
# %%
anchor = setVecs[0]

#%% 
def entropy(labels, base=None):
  value,counts = np.unique(labels, return_counts=True)
  norm_counts = counts / counts.sum()
  base = np.e if base is None else base
  return -(norm_counts * np.log(norm_counts)/np.log(base)).sum()


#%%
similarities = anchor*setVecs
bits = 2**np.arange(len(alphabet))
ids = np.sum(bits*similarities, axis=1)
# %%
