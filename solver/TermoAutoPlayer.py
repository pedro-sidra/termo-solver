from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from pyshadow.main import Shadow
import time


class TermoAutoPlayer:
    """Helper class for playing term.ooo through the browser using selenium.
       Can send words and check the current state of the game"""
    def __init__(self, url:str="https://term.ooo/", headless:bool=True):
        """Open the webpage using selenium, and send an ESCAPE key to close the help window"""

        # Run headless
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
            # Fetch recent ChromeDriver and run headless
            self.driver = ChromeDriver(ChromeDriverManager().install(), chrome_options=options)
        else:
            self.driver = ChromeDriver(ChromeDriverManager().install())


        self.driver.get(url)
        self.driver.implicitly_wait(5)

        self.shadow = Shadow(self.driver)

        self.body = self.driver.find_element_by_xpath("//body")
        self.send_keys(Keys.ESCAPE)

    def send_keys(self, key):
        """Send keypresses to the page through selenium"""
        self.body.send_keys(key)

    def send_word(self, word: str):
        """send_word sends a word query to the game, and checks if the word was valid

        :param word: the 5-letter word to send

        :returns: True if the word was accepted, False otherwise (e.g. invalid word)
        """
        # Get the current state to later check if it changed
        old_state = self.get_state()

        self.send_keys(word)
        self.send_keys(Keys.RETURN)

        time.sleep(0.5)
        # State will only stay the same if the word was invalid
        if(self.get_state() == old_state):
          # If the word was invalid, send some backspaces to clear it
          for i in range(5):
            self.send_keys(Keys.BACKSPACE)
            time.sleep(0.1)
          return False

        # If we got here, the word was valid
        return True

    def get_state(self):
        """ Get the 'board state' of the game, containing all letters and clues
        :returns: state, a string which indicates the state of the game, where:
                  * '⬛' means a wrong letter
                  * '🟨' means a yellow letter
                  * '🟩' means a green letter
                  * '\n' separates lines (`state` always has 6 lines)
                  * empty characters means that that line was not yet reached
        """
        # Letters are all divs with 'letter' in the class attribute
        letters = self.shadow.find_elements("div.letter")

        # Initialize this array so that random indexing is easier
        state = [
            [ "", "", "", "", ""],
            [ "", "", "", "", ""],
            [ "", "", "", "", ""],
            [ "", "", "", "", ""],
            [ "", "", "", "", ""],
            [ "", "", "", "", ""],
        ]
        for letter in letters:
            cls = letter.get_attribute("class")
            letter_row = letter.get_attribute("termo-row")
            # letter id
            letter_idx = letter.get_attribute("lid")
            letter_text = letter.text

            if " place" in cls: # Yellow letters have class = "letter place"
                letterState = "🟨"
            elif " right" in cls:# Green letters have class = "letter right"
                letterState = "🟩"
            elif " wrong" in cls:# Wrong letters have class = "letter wrong"
                letterState = "⬛"
            else:
                letterState = "" # Other letters have class in ["letter empty", "letter edit", "letter"]

            # Assign to corresponding (row, column)
            state[int(letter_row)][int(letter_idx)] = letterState

        # Join the state into a single string for simplicity
        output = []
        for s in state:
          output.append("".join(s))
        return "\n".join(output)


if __name__=="__main__":
  player = TermoAutoPlayer()

  words = ["termo","termx","tests","cairo"]

  for word in words:
    if not player.send_word(word):
      print(f"WARNING: {word=} invalid")

  state = player.get_state()
  print(state)
  time.sleep(1000)
