import solver.guess as guess
import time
from solver.TermoAutoPlayer import TermoAutoPlayer

def play_termo(player:TermoAutoPlayer):
    words = ["cario"] #guess.first_guess()

    i = 0
    player.send_word(words[i])
    time.sleep(0.5)
    while i < 6:
        state = player.get_state()

        matches = state["hints"]

        if matches[-1] == "🟩🟩🟩🟩🟩":
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
        



def main():
    print(play_termo(TermoAutoPlayer(headless=False)))
if __name__=="__main__":
    main()
