#%%
import nltk
from nltk.corpus import words as nltk_words
import codecs
from unidecode import unidecode
import re
import pandas as pd
import numpy as np
import os


alphabet = "abcdefghijklmnopqrstuvwxyz"

def loadENWords():
    # nltk.data.path.append('/work/words')
    nltk.download('words')
    return nltk_words.words()

def loadPTWords():
    _file_path = os.path.realpath(__file__)
    _folder_path,_ = os.path.split(_file_path)
    with codecs.open(f"{_folder_path}/../pt-br/dicio","r", encoding="utf-8") as f:
        words = f.read().split()
    return words
    
def getNLetterWords(dictionary, n=5):
    # Unidecode gets rid of any ~ ´ or ^
    filtered = [unidecode(w).lower() for w in dictionary]
    # Valid words: only letters a-z, exactly 5
    fiveLetter = re.compile("^[a-zA-Z]{"+str(n)+"}$")
    # Check that there is no weird characters
    return [w for w in filtered if fiveLetter.match(w)]

def letter2num(letter):
    return ord(letter) - ord("a")

def num2leter(index):
    return chr(index + ord("a"))

def wordVecDataframe(language="pt", n_letters=5):
    if language == "en":
        dic = loadENWords()
    elif language=="pt":
        dic = loadPTWords()

    words = getNLetterWords(dic, n=n_letters)

    # Words and vector representation,
    # Example item from the `data` list:
    # {"word":"termo", 0:"t", 1:"e", 2:"r", 3:"m", 4:"o"}
    data = [  {"word":word,
               **{i:l.lower() for i,l in enumerate(word)}}
            for word in words]
    
    df = pd.DataFrame(data)

    # Map the letter columns to a number representation
    # e.g. a-> 0 , b->1, ... z->25
    df.iloc[:,1:] = df.iloc[:,1:].applymap(letter2num)


    df = df.drop_duplicates().reset_index(drop=True)

    return df

def letterFreqs(wordVecDf):
    """
    
    retuns: local, global
    letter frequencies by letter-spot and by letter
    """
    # Get value counts for each letter in each word position
    freqs = [wordVecDf[k].value_counts(normalize=True)
            for k in wordVecDf.iloc[:,1:]]

    # Get dataframe with columns-> positions and index->letter idx
    freqs = (pd.DataFrame(freqs)
            .transpose()
            .sort_index()
            .fillna(0))
    
    freqs = freqs.reindex(range(len(alphabet)))
    
    freqs = freqs.fillna(0)

    # Sum letter frequencies for all spots, divide by total (total = num of letters)
    freqs["global"] = freqs.sum(axis=1)/freqs.sum().sum()

    freqs = freqs.fillna(0)

    return freqs

def letterVec2LetterFreq(df, dfreq=None):
    
    if dfreq is None:
        dfreq = letterFreqs(df)

    def letter_prob(letter, pos):
        return dfreq.iloc[letter, pos]

    return df.iloc[:,1:].apply(lambda col: 
        letter_prob(col.astype(int),col.name)
            .reset_index(drop=True))

def setOfLetters(vec):
    return list(set(vec))

def bagOfLettersVec(vec):
    idxs = setOfLetters(vec)
    vec = np.zeros(len(alphabet), dtype=np.uint8)
    vec[idxs]=1
    return vec

# def codedLettersVec(inp):
#     global _bits

#     if len(_bits)!=len(inp):
#         _bits = 2**(np.arange(len(inp)))

#     idxs = setOfLetters(inp)

#     vec = np.zeros(len(alphabet), dtype=np.uint8)

#     # Bit-encoding of letter placement in word
#     codes = [np.sum(_bits*(inp==i)) for i in idxs]

#     vec[idxs]=codes
#     return vec

_bits = 2**(np.arange(5))
def wordCodes(wordVec):
    global _bits
    n, let = wordVec.shape

    if len(_bits)!=let:
        _bits = 2**(np.arange(let))

    codes = np.zeros((n, let*26))
    offs = np.arange(let)*26

    for i, vec in enumerate(offs+wordVec):
        codes[i, vec]=1

    codes=codes.reshape(-1, let,26)
    return (_bits@codes).astype(np.uint8)
    # return np.stack(words.iloc[:,1:].apply(codedLettersVec, axis=1))

def decodeWord(word):
    idxs = np.where(word!=0)[0]
    
    positions = [np.unpackbits(a,bitorder="little") for a in word[idxs]]
    letters = ["-",]*5

    for idx, pos in zip(idxs, positions):
        for i,p in enumerate(pos):
            if p!=0:
                letters[i] = num2leter(idx)
    return "".join(letters).strip()

def prob_yellow(vec, dfreq):
    """
    given a letter-position vector and letter frequency df,
    return probability that words in the dataset contain at least one of 
    the letters in vec
    """
    letters = setOfLetters(vec)
    probs = dfreq["global"].iloc[letters]
    return 1 - (1-probs).product()

def calcProbabilities(df):

    output = pd.DataFrame(data={"word":df["word"]})
    dfreq = letterFreqs(df)

    p_byLetter = letterVec2LetterFreq(df, dfreq=dfreq)
    p_noHitByLetter = 1 - p_byLetter
    p_noHit = p_noHitByLetter.product(axis=1)
    p_hit = 1 - p_noHit

    p_yellow = df.iloc[:,1:].apply(lambda x: prob_yellow(x, dfreq), axis=1)

    output["prob_green"] = p_hit
    output["prob_yellow"] = p_yellow
    output["prob_greenyellow"] = p_hit*p_yellow

    return output

def lettersOfSet(letterSet):
    return "".join([num2leter(n) for n in np.where(letterSet!=0)[0]])

def lettersOfVec(vec):
    return "".join([num2leter(n) for n in vec])
# %%
