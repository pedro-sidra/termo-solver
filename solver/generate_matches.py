# %%
import tqdm
import numpy as np

from prob import *

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


if __name__=="__main__":
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