import numpy as np
import pandas as pd
import os
from pathlib import Path

file_path = Path(os.path.realpath(__file__))
read = np.load(f"matches.npz", allow_pickle=True)

greens = read["greens"]
yellows = read["yellows"]
words = pd.DataFrame(data=dict(words=read["words"]))

M = greens.astype(np.uint16) + (yellows.astype(np.uint16) << 5)
del greens
del yellows

def freqs(M):
    if M.ndim > 1:
        counts = [np.unique(m, return_counts=True)[1] for m in M]
        return [c/np.sum(c) for c in counts]
        # return [c for c in counts]
    else:
        counts = np.unique(M, return_counts=True)[1]
        s = np.sum(counts)
        return counts/s
            

def first_guess():
    global M
    global words

    information = [ np.sum(f*-np.log2(f)) for f in freqs(M) ]
    words["information"] = information
    return words.sort_values(by="information", ascending=False).head(n=5).reset_index(drop=True)

_bitValues = 2**np.arange(5)
def match_to_code(matchstring):
    green = 1*np.asarray([l=="🟩" for l in matchstring])
    yellow = 1*np.asarray([l=="🟨" for l in matchstring])
    return np.sum(_bitValues*green) + (np.sum(_bitValues*yellow) << 5)

def get_guess(guesses, matches, return_subset=False):
    global M
    global words

    subWords = words
    subM = M
    for guess, matchstr in zip(guesses,matches):
        match = match_to_code(matchstr)

        indexQuery = words.query("words==@guess").index[0]

        sub = np.where(subM[indexQuery]==match)[0]
        subM = subM[:,sub]

        subWords = subWords.iloc[sub]


    information = [ np.sum(f*-np.log2(f)) for f in freqs(subM) ]
    words["information"] = information
    words["inSubset"] = 0
    words.loc[subWords.index,"inSubset"] = 1

    subWords.loc[:,"information"] = words.loc[subWords.index,"information"]
    

    if return_subset:
        best_guesses = words.sort_values(by=[ "information","inSubset" ], ascending=False).head(n=5)
        subset = subWords.sort_values(by= "information", ascending=False)
        return best_guesses, subset
    else:
        best_guesses = words.sort_values(by=[ "information","inSubset" ], ascending=False).head(n=5)["words"]
        return best_guesses

if __name__=="__main__":
    print("first guess:")
    print(first_guess())
