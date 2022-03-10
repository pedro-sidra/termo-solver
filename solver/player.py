import solver.guess as guess
import time
from solver.TermoAutoPlayer import TermoAutoPlayer

def main():
    words = ["cario"] #guess.first_guess()

    player = TermoAutoPlayer(headless=False)


    i = 0
    player.send_word(words[i])
    time.sleep(0.5)
    while i < 6:
        state = player.get_state().split(",")

        matches = [match for match in state if len(match) > 0]

        if matches[-1] == "ggggg":
            print("you won!")
            return state
            
        for word in guess.get_guess(words, matches):
            if player.send_word(word):
                words.append(word)
                i+=1
                break
        else:
            print("failed to input all words in guess... giving up!")
            return None
        



if __name__=="__main__":
    print(main())
