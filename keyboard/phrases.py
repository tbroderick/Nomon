import numpy as np
import os


class Phrases:
    def __init__(self, phrases_file):
        phrases_file = open(phrases_file, "r")
        phrases_text = phrases_file.read()
        phrases_file.close()
        self.phrases = []
        for phrase in phrases_text.split("\n"):
            if 3 <= len(phrase.split(" ")) <= 10:
                self.phrases.append(phrase)
        self.num_phrases = len(self.phrases)
        self.cur_phrase = None
        self.sample()

    def sample(self):
        self.cur_phrase = self.phrases[np.random.randint(0, self.num_phrases)]
        # self.cur_phrase = "hello my name is nick"
        return self.cur_phrase

    def compare(self, input_phrase):
        input_words = input_phrase.split(" ")
        # if "" in input_words:
        #     input_words.remove("")
        cur_phrase_words = self.cur_phrase.split(" ")

        finished = False
        if len(input_words) == 0:
            base_typed = ""

        elif len(input_words) < len(cur_phrase_words):
            cur_phrase_word = cur_phrase_words[len(input_words)-1]
            cur_input_word = input_words[-1]

            if len(cur_input_word) < len(cur_phrase_word):
                base_typed = ' '.join(cur_phrase_words[:len(input_words)-1])
                base_typed += ' '+cur_phrase_word[:len(cur_input_word)]

            else:
                base_typed = ' '.join(cur_phrase_words[:len(input_words)])


        elif len(input_words) == len(cur_phrase_words):
            cur_phrase_word = cur_phrase_words[len(input_words) - 1]
            cur_input_word = input_words[-1]

            if len(cur_input_word) < len(cur_phrase_word):
                base_typed = ' '.join(cur_phrase_words[:len(input_words) - 1])
                base_typed += ' ' + cur_phrase_word[:len(cur_input_word)]

            else:
                base_typed = self.cur_phrase
                finished = True

        else:
            base_typed = curbase_typed = self.cur_phrase
            finished = True
        if len(base_typed) > 0:
            if base_typed[0] == " ":
                base_typed = base_typed[1:]
        return base_typed, finished



def main():
    phrases = Phrases("resources/all_lower_nopunc.txt")
    print(phrases.sample())
    print(phrases.compare("hello my name issdf "))


if __name__ == "__main__":
    main()
