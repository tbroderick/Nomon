######################################
# Copyright 2019 Nicholas Bonaker, Keith Vertanen, Emli-Mari Nel, Tamara Broderick
# This file is part of the Nomon software.
# Nomon is free software: you can redistribute it and/or modify it
# under the terms of the MIT License reproduced below.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY
# OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR
#OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# <https://opensource.org/licenses/mit-license.html>
######################################


import numpy as np
import os
import re
import emoji
import json


class Phrases:
    def __init__(self, phrases_file_name):
        phrases_file = open(phrases_file_name, "r")
        phrases_text = phrases_file.read()
        phrases_file.close()
        self.phrases = []
        if "twitter" in phrases_file_name or "watch" in phrases_file_name:
            phrases = [phrase[phrase.index("\t") + 1:] for phrase in phrases_text.split("\n") if "\t" in phrase]
            for phrase in phrases:
                if 5 <= len(phrase.split(" ")) <= 10:
                    phrase = re.sub(r"[^a-z \']+", '', phrase.lower())
                    phrase = re.sub(r"  ", ' ', phrase.lower())
                    self.phrases.append(phrase)
        else:
            for phrase in phrases_text.split("\n"):
                if 'emoji' not in phrases_file_name:
                    if 5 <= len(phrase.split(" ")) <= 10:
                        phrase = re.sub(r"[^a-z \']+", '', phrase.lower())
                        phrase = re.sub(r"  ", ' ', phrase.lower())
                        self.phrases.append(phrase)
                else:
                    if phrase not in ['#','_','$','@']:
                        self.phrases.append(emoji.emojize(phrase, use_aliases=True))

            if 'emoji' in phrases_file_name:
                phrase_locs = np.random.choice(np.array(self.phrases), (100, 5)).tolist()
                phrase_locs = [''.join(phrase) for phrase in phrase_locs]
                self.phrases = phrase_locs


        self.num_phrases = len(self.phrases)
        # print("loaded "+str(self.num_phrases)+" phrases")

        self.cur_phrase = None
        self.sample()

    def sample(self):
        self.cur_phrase = self.phrases[np.random.randint(0, self.num_phrases)]
        # self.cur_phrase = "hello my name is nick"
        return self.cur_phrase

    def compare(self, input_phrase, target=None):
        input_words = input_phrase.split(" ")
        # if "" in input_words:
        #     input_words.remove("")
        if target is None:
            target = self.cur_phrase

        cur_phrase_words = target.split(" ")

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
                base_typed = target
                finished = True

        else:
            base_typed = target
            finished = True
        if len(base_typed) > 0:
            if base_typed[0] == " ":
                base_typed = base_typed[1:]
        return base_typed, finished

    def highlight(self, input_phrase):
        cur_phrase_words = self.cur_phrase.split(" ")
        input_phrase_words = input_phrase.split(" ")

        highlighted_text = ""
        for word_index in range(len(cur_phrase_words)):
            phrase_word = cur_phrase_words[word_index]

            if word_index < len(input_phrase_words):
                input_word = input_phrase_words[word_index]
                if phrase_word == input_word:
                    highlighted_text += "<t>" + phrase_word + " </t>"
                elif input_word == "":
                    highlighted_text += "<y>" + phrase_word + " </y>"
                else:
                    highlighted_text += "<f>" + phrase_word + " </f>"
            else:
                highlighted_text += "<b>" + phrase_word + " </b>"

        highlighted_text = re.sub("</t><t>", "", highlighted_text)
        highlighted_text = re.sub("</f><f>", "", highlighted_text)
        highlighted_text = re.sub("</b><b>", "", highlighted_text)

        highlighted_text = re.sub("<t>", "<span style='color:#00dd00;'>", highlighted_text)
        highlighted_text = re.sub("</t>", "</span>", highlighted_text)
        highlighted_text = re.sub("<f>", "<span style='color:#dd0000;'>", highlighted_text)
        highlighted_text = re.sub("</f>", "</span>", highlighted_text)
        highlighted_text = re.sub("<b>", "<span style='color:#000000;'>", highlighted_text)
        highlighted_text = re.sub("</b>", "</span>", highlighted_text)
        highlighted_text = re.sub("<y>", "<span style='color:#dd9900;'>", highlighted_text)
        highlighted_text = re.sub("</y>", "</span>", highlighted_text)

        return highlighted_text


def main():
    phrases = Phrases("resources/twitter-phrases/watch-iv.txt")
    print(json.dumps(phrases.phrases))
    print(phrases.num_phrases)
    # phrases.cur_phrase = "hello my name is nicholas ryan bonaker"
    # print(phrases.highlight("hello my name is n"))


if __name__ == "__main__":
    main()
