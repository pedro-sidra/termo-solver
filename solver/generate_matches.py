# %%
import tqdm
import numpy as np

from solver.word_ops import *



def main():
    words = wordVecDataframe(language="pt")
    codes= wordCodes(words.iloc[:,1:].to_numpy().astype(int))
    print(f"Codes vec: \n{codes}")
    print(f"Shape: {codes.shape}")

    n, let = words.iloc[:,1:].shape

    # Full matrix
    greens = np.zeros((n,n), dtype=np.uint8)
    yellows = np.zeros((n,n), dtype=np.uint8)

    # For each letter
    for i in tqdm.tqdm(range(26)):
        # Check matches between all words and all other words for that letter
        partial_greens = get_green_matches(codes[:,np.newaxis,i:i+1],codes[...,i:i+1])
        # Set bits in `greens` in positions that have matches
        greens +=  partial_greens[...,0]

        # Same for yellow, which depends on greens (green letters don't count for yellow matches)
        partial_yellows = get_yellow_matches(codes[:,np.newaxis,i:i+1],codes[...,i:i+1], partial_greens)
        yellows[...] += partial_yellows[...,0]

    file = "matches"
    np.savez(file, greens=greens, yellows=yellows, words=words.iloc[:,0].to_numpy())

if __name__=="__main__":
    main()