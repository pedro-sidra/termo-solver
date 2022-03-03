import guess
from TermoAutoPlayer import TermoAutoPlayer

def main():
    words = ["cario"] #guess.first_guess()

    player = TermoAutoPlayer(headless=False)


    i = 0
    player.send_word(words[i])
    while i < 6:
        state = player.get_state()
        matches = [match for match in state.split(",") if len(match) > 0]

        print(matches)
        for word in guess.get_guess(words, matches):
            if player.send_word(word):
                words.append(word)
                i+=1
                break
        else:
            print("OOPS")

        



if __name__=="__main__":
    main()