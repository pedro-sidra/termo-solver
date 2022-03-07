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

def lettersOfSet(letterSet):
    return "".join([num2leter(n) for n in np.where(letterSet!=0)[0]])

def lettersOfVec(vec):
    return "".join([num2leter(n) for n in vec])

def decodeToBits(c):
    return np.asarray([np.unpackbits(i, bitorder="little")[:5] for i in c])

def match_code(arr):
    return np.sum(_bitValues*arr, axis=1)

_bitValues = 2**np.arange(5)
def get_green_matches(codeword, codeset):
    greens = codeword&codeset
    return greens

def codify_matches(codedMatches):
    n = len(codedMatches)
    bits = (np.unpackbits(codedMatches.flatten(),bitorder="little")
        .reshape( (n, 26, 8) )
        [:,:,:5]
        )
    matches =  np.sum(bits, axis=1)
    # return [str(m) for m in matches]
    # return matches
    return match_code(matches)

    
def log2impl(x):
    output = np.zeros_like(x)
    vals = 2**np.arange(8)
    itr = list(enumerate(vals))
    for i, num in (itr):
        output[ x - num >= 0 ] = i
    
    return output

def bit_count(arr):
     # Make the values type-agnostic (as long as it's integers)
     t = arr.dtype.type
     mask = t(-1)
     s55 = t(0x5555555555555555 & mask)  # Add more digits for 128bit support
     s33 = t(0x3333333333333333 & mask)
     s0F = t(0x0F0F0F0F0F0F0F0F & mask)
     s01 = t(0x0101010101010101 & mask)

     arr = arr - ((arr >> 1) & s55)
     arr = (arr & s33) + ((arr >> 2) & s33)
     arr = (arr + (arr >> 4)) & s0F
     return (arr * s01) >> (8 * (arr.itemsize - 1))

def get_yellow_matches(codeword, codeset, greens):
    # ~codeset: has a 5-bit mask for each letter, 
    #           with 1s where that letter is not located on the word
    #           (consequently the 5-bit mask=11111 for letters not in the word)
    # ~codeset * codeset!=0: eliminates the erroneous 5-bit masks for letters that are not in the word
    # yellow: has 1s where the letter in the codeword matches a letter in the codeset,
    #         but not in the same position
    # nongreen = codeset & ((~greens)*(greens!=0))
    # codeset = codeset 
    nongreen = codeset & ~greens
    yellow = (((~codeset)*(codeset!=0)))&codeword
    yellow = yellow & ~greens

    # Yellow is not as expected
    # Example:
    #    codeword   = traca
    #    codeset[i] = pavos
    #    yellow =     --y-y
    #should be  =     --y--
    # Because the count of letters should be considered. 
    # E.g. --y-y implies there are two 'a's in the match

    # Correct for different count of matches

    # Popcount = number of nonzero bits in each letter
    # if there are more nonzero bits in the match than in the original word,
    # correct it
    wrong = bit_count(yellow.astype(np.uint8)) > bit_count(nongreen.astype(np.uint8))
    while np.any(wrong):

        # This MIGHT be better performance
        # highestbits = 1<<log2impl(yellow.astype(int))
        # highestbits[yellow==0] = 0

        highestbits = 2**np.floor(np.log2(yellow))

        corrections = wrong * highestbits
        corrections = corrections.astype(np.uint8)

        yellow = (yellow & (~corrections))
        # Recompute the `wrong` mask (corrections only clears one bit, there might be more)
        wrong = bit_count(yellow.astype(np.uint8)) > bit_count(nongreen.astype(np.uint8))
        yellow=yellow.astype(np.uint8)

    return yellow
# %%
