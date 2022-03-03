import re
import argparse
import pandas as pd
import os

file_path = os.path.realpath(__file__)

def printHeader(message):
    print(f"+============={message}=============+")

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

    print("loading...")
    import solver.guess as guess

    print("press q to quit... ")
    command=""
    printHeader("Open the website and lets begin!")
    best_guesses = guess.first_guess()

    guesses = []
    matches = []
    while command !="q":

        print("Your best first guesses are:")
        print(best_guesses)
        print("Type your guess")
        print("or type `q` to leave")
        print("or type `r` to reset")

        command = input("> ")

        if fiveLetter.match(command):
            word = command
            print("Now type your hints (e.g. --yg-):")
            print("   or type h for help")

            command = input("> ")

            if command=="h":
                print("example: if you got the first letter yellow and the last letter green")
                print("         then type 'y---g'")
                continue

            if not guessRegexp.match(command):
                print("Oops, typed wrong!")
                continue

            matches.append(command)
            guesses.append(word)
            best_guesses, subset = guess.get_guess(guesses, matches, return_subset=True)

            if(len(subset) > 10):
                print(f"{ len(subset)= }")
            else:
                print(f"{len(subset)} words left:")
                print(subset)


        
        if command=="r":
            green="-"*5
            yellow_pos=[]
            gray=""
            subset=words
            continue

        if command=="a":
            print(subset)
            continue

if __name__=="__main__":
    main()
