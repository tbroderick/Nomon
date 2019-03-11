#!/usr/bin/python

# This is an example script to run the WordPredictor class and get
# a list of words that begins with the prefix and a each of the valid 
# character in the character list appened to it. For example, given
# a prefix 'a' and if the chracters in the vocabulary are [a,b,c], it 
# will return a list of words that begin with 'aa', 'ab' and 'ac'.

import os, sys
import numpy as np

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from predictor import WordPredictor


class LanguageModel():
    def __init__(self, lm_filename, vocab_filename):
        self.lm_filename = lm_filename
        self.vocab_filename = vocab_filename

        self.word_predictor = WordPredictor(lm_filename, vocab_filename)

        # Define how many predictions you want for each character
        # By default it is set to 0 and will return all possible
        # words
        self.num_predictions = 3
        self.min_log_prob = np.log(0.02)

        # The default vocab_id is ''
        self.vocab_id = ''

    def get_words(self, context, prefix, keys_li):
        self.context = context
        self.prefix = prefix
        print("prefix: ", prefix, ", context: ", context)

        word_preds = []
        word_probs = []

        lm_results = self.word_predictor.get_words_with_context(prefix, context, self.vocab_id, self.num_predictions, self.min_log_prob)
        word_dict = {}
        for word_list in lm_results:
            if len(word_list) > 0:
                word_dict[word_list[0][0][len(prefix)]] = word_list
        for key in keys_li:
            key_word_preds = ["", "", ""]
            key_word_probs = [-float("inf"), -float("inf"), -float("inf")]
            if key in word_dict:
                index = 0
                for word_tuple in word_dict[key]:
                    if word_tuple[1] >= self.min_log_prob:
                        key_word_preds[index] = word_tuple[0]+" "
                        key_word_probs[index] = word_tuple[1]
                    index += 1
            word_preds += [key_word_preds]
            word_probs += [key_word_probs]

        key_probs = self.get_char_probs(word_dict, keys_li)

        return word_preds, word_probs, key_probs

    def get_char_probs(self, word_dict, keys_li):

        key_probs = []
        for key in keys_li:
            log_prob = 0
            if key in word_dict:
                for word in word_dict[key]:
                    if log_prob == 0:
                        log_prob = word[1]
                    else:
                        log_prob = np.logaddexp(log_prob, word[1])
            key_probs += [log_prob]

        return key_probs



def main():

    LM = LanguageModel('../keyboard/resources/lm_word_medium.kenlm', '../keyboard/resources/vocab_100k')
    print(LM.get_words("", "h", list("abcdefghijklmnopqrstuvwxyz' ")))

    # # Provide the name and path of a language model and the vocabulary
    # lm_filename = '../resources/lm_word_medium.kenlm'
    # vocab_filename = '../resources/vocab_100k'
    #
    # # Create an instance of the WordPredictor class
    # word_predictor = WordPredictor(lm_filename, vocab_filename)
    #
    # prefix = ''
    # context = ''
    #
    # # Define how many predictions you want for each character
    # # By default it is set to 0 and will return all possible
    # # words
    # num_predictions = 3
    # min_log_prob = -float('inf')
    #
    # # The default vocab_id is ''
    # vocab_id = ''

    # word_list = word_predictor.get_words_with_context(prefix, context, vocab_id, num_predictions, min_log_prob)

    # Call the print_suggestions method to print all the words
    # word_predictor.print_suggestions(word_list)
    # self.words_li, self.word_freq_li, self.key_freq_li, self.top_freq, self.tot_freq, self.prefix


if __name__ == "__main__":
    main()
