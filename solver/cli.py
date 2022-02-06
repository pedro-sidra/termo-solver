import solver.prob as prob
from solver.prob import alphabet
import re
import argparse
import pandas as pd

def printHeader(message):
    print(f"+============={message}=============+")

# %%
def query_contains(df, letter):
    index = alphabet.index(letter)
    # sorry...
    return df.query(f"@df[0]=={index} or @df[1]=={index} or @df[2]=={index} or @df[3]=={index} or @df[4]=={index}")

def query_does_not_contain(df, letter):
    index = alphabet.index(letter)
    # sorry...
    return df.query(f"@df[0]!={index} and @df[1]!={index} and @df[2]!={index} and @df[3]!={index} and @df[4]!={index}")

def filter_words(subset, green, gray, yellow_pos):
    yellow = [letter for letter in "".join(yellow_pos) if letter !="-"]

    # Get words that have green characters in the correct spot
    for i, char in enumerate(green):
        if char=="-":
            continue
        subset = subset.query(f"@subset[{i}]=={alphabet.index(char)}")

    # Get words that have all the yellow letters
    for letter in yellow:
        subset = query_contains(subset, letter)
    
    # Get words that don't have any gray letters
    for letter in gray:
        subset = query_does_not_contain(subset, letter)

    # Get words that don't have any of the yellow letters in the incorrect spots
    for frase in yellow_pos:
        for i, letter in enumerate(frase):
            if letter != "-":
                subset = subset.query(f"@subset[{i}] != {alphabet.index(letter)}")
    
    return subset

def print_best(probs, topN=5):
    print("Here are your best guesses:")
    info = probs[["word", "prob_yellow","prob_green","prob_greenyellow"]]
    yellow = (info.sort_values(by="prob_yellow", ascending=False)
                .head(n=topN)
                .reset_index(drop=True)
                .loc[:,["word", "prob_yellow"]])

    green = (info.sort_values(by="prob_green", ascending=False)
                .head(n=topN)
                .reset_index(drop=True)
                .loc[:,["word", "prob_green"]])

    greenyellow = (info.sort_values(by="prob_greenyellow", ascending=False)
                        .head(n=topN)
                        .reset_index(drop=True)
                        .loc[:,["word", "prob_greenyellow"]])

    printHeader("Best chance of yellow letter:")
    print(yellow)
    printHeader("Best chance of green letter:")
    print(green)
    printHeader("Best chance of one green and one yellow:")
    print(greenyellow)


def replacechar(s, index, new):
    return s[:index] + new + s[index + 1:]

def main():
    parser = argparse.ArgumentParser(description='Helps you play term.ooo!')

    parser.add_argument(
        '-l', '--lang', default="pt",
        help='Language to use, should be "pt" or "en"',)
    
    args = parser.parse_args()

    fiveLetter = re.compile("^[a-zA-Z]{5}$")
    guessRegexp = re.compile("^[yg\-]{5}$")

    words = prob.wordVecDataframe()

    print("press q to quit... ")
    command=""
    printHeader("Open the website and lets begin!")
    green = "-----"
    yellow_pos = []
    gray=""
    subset = words
    while command !="q":

        probs = prob.calcProbabilities(subset)
        print_best(probs)

        print("Type 'g' to input your guess!")
        print("or type a word to get its probabilities")
        print("or type `a` to print all your options")
        print("or type `q` to leave")
        print("or type `r` to reset")

        command = input("> ")

        if fiveLetter.match(command):
            printHeader("")
            print(f"probabilities for {command}:")
            print(probs.query("`word`==@command")[["word", "prob_yellow","prob_green","prob_greenyellow"]])
            continue
        
        if command=="r":
            green="-"*5
            yellow_pos=[]
            gray=""
            subset=words
            continue

        if command=="a":
            print(subset)
            continue

        if command=="g" or command=="guess":
            print("Type the word you guessed:")
            command = input("> ")
            if not fiveLetter.match(command):
                print("Oops, typed wrong!")
                continue
            word = command
            print("Now type your hints:")
            print("-- or type h for help")

            command = input("> ")

            if command=="h":
                print("example: if you got the first letter yellow and the last letter green")
                print("         then type 'y---g'")
                continue

            if not guessRegexp.match(command):
                print("Oops, typed wrong!")
                continue

            guess = command

            yellowItem = '-----'
            for i, char in enumerate(guess):
                if char=="y":
                    yellowItem=replacechar(yellowItem, i, word[i])
                elif char=="g":
                    green=replacechar(green, i, word[i])
                else:
                    gray+=word[i]
            yellow_pos.append(yellowItem)
            subset = filter_words(subset, green, gray, yellow_pos).reset_index(drop=True)

if __name__=="__main__":
    main()
