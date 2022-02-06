
#%%
import nltk
from nltk.corpus import words

nltk.data.path.append('/work/words')
nltk.download('words', download_dir='/work/words')
words = words.words()
# prints 236736

#%%
import codecs
from unidecode import unidecode
with codecs.open("palavras/palavras.txt","r", encoding="utf-8") as f:
    words = f.read().split()

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
#%%
import pandas as pd
data = pd.DataFrame(data={
    "1":vecs[:,0],
    "2":vecs[:,1],
    "3":vecs[:,2],
    "4":vecs[:,3],
    "5":vecs[:,4],
    "word":fiveletter
})
print(data)

#%%
print(len(data["word"].unique()))
print(len(data["word"]))

pd.concat(g for _, g in data.groupby("word") if len(g) > 1)
#%%
data = data.drop_duplicates()
#%%
modeword = data.iloc[:,:5].mode().to_numpy().ravel()
print("".join(alphabet[i] for i in modeword))
#%%
from collections import Counter
positions = data.columns[:5]
counts={
    pos: {
        l: 0
        for l in range(len(alphabet))
    }for pos in positions
}

for pos in positions:
    for letter, count in Counter(data[pos]).items():
        counts[pos][letter]=count
#%%
freq_df = pd.DataFrame(counts)
n = len(data)

#%% 
freq_df.iloc[0,0]/n

def prob_in(pos, letter):
    return freq_df.iloc[letter, pos]/n
def prob_not_in(pos,letter):
    return 1-freq_df.iloc[letter, pos]/n
# %%
for pos in positions:
    p = int(pos)-1
    col = f"prob_{pos}"
    data[col]=0
    icol = list(data.columns).index(col)
    for i, letter in enumerate(data[pos]):
        data.iloc[i,icol] = prob_not_in(p, letter)
#%%
np.product(data.iloc[:,-5:], axis=1)
# %%
data["prob_hit"] = 1-np.product(data.iloc[:,-5:], axis=1)
#%%
data.sort_values(by="prob_hit").tail(n=10).loc[:,["word","prob_hit"]].iloc[::-1].reset_index().drop("index", axis=1)
#%%
rel_freq = pd.DataFrame()
for col in freq_df.iloc[:, :5]:
    rel_freq[f"{col}"] = freq_df[col]/n
rel_freq
#%%
def prob_yellow(vec):
    letters = list(set(vec))
    prob_none_byletter = (1 - rel_freq.iloc[letters]).product(axis=1)
    prob_no_letter = prob_none_byletter.product()
    return 1-prob_no_letter
#%%
data["prob_yellow"]=0
icol = list(data.columns).index("prob_yellow")
vecs = data.iloc[:,:5].to_numpy()
#%%
for i, row in enumerate(vecs):
    data.iloc[i,icol] = prob_yellow(row.copy())

# %%
data["prob_greenyellow"] = data["prob_hit"]*data["prob_yellow"]

#%%

# word = "cairo"
green= "--o-e"
yellow_pos= [
    "---et",
    "st---",
]
yellow = [letter for letter in "".join(yellow_pos) if letter !="-"]
gray="carl"

subset = data
for i, char in enumerate(green):
    if char=="-":
        continue

    subset = subset.query(f"`{i+1}`=={alphabet.index(char)}")
# %%
def query_contains(df, letter):
    index = alphabet.index(letter)
    return df.query(f"`1`=={index} or `2`=={index} or `3`=={index} or `4`=={index} or `5`=={index}")

def query_does_not_contain(df, letter):
    index = alphabet.index(letter)
    return df.query(f"`1`!={index} and `2`!={index} and `3`!={index} and `4`!={index} and `5`!={index}")


# %%
for letter in yellow:
    subset = query_contains(subset, letter)
for letter in gray:
    subset = query_does_not_contain(subset, letter)
# %%
for frase in yellow_pos:
    for i, letter in enumerate(frase):
        if letter != "-":
            subset = subset.query(f"`{i+1}` != {alphabet.index(letter)}")

# %%
subset.sort_values(by="prob_greenyellow").tail(n=20)

# %%

# %%
