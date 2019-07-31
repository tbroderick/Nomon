#!/usr/bin/python

# This is an example script to run the WordPredictor class and get
# a list of words that begins with the prefix and a each of the valid 
# character in the character list appened to it. For example, given
# a prefix 'a' and if the chracters in the vocabulary are [a,b,c], it 
# will return a list of words that begin with 'aa', 'ab' and 'ac'.

import os, sys
import numpy as np
import kconfig

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from predictor import WordPredictor


class LanguageModel():
    def __init__(self, lm_filename, vocab_filename, parent=None):
        self.lm_filename = lm_filename
        self.vocab_filename = vocab_filename

        self.word_predictor = WordPredictor(lm_filename, vocab_filename)

        # Define how many predictions you want for each character
        # By default it is set to 0 and will return all possible
        # words
        if parent is not None:
            self.parent = parent
            self.num_predictions = self.parent.N_pred
            self.prob_thres = self.parent.prob_thres
            self.num_words_total = self.parent.num_words_total
        else:
            self.parent = None
            self.num_predictions = kconfig.N_pred
            self.prob_thres = 0
            self.num_words_total = 26*self.num_predictions
        self.min_log_prob = -float("inf")

        # The default vocab_id is ''
        self.vocab_id = ''

    def get_words(self, context, prefix, keys_li, num_words_total=kconfig.num_words_total):
        if self.parent is not None:
            self.num_predictions = self.parent.N_pred
            self.prob_thres = self.parent.prob_thres
            self.num_words_total = self.parent.num_words_total

        self.context = context
        self.prefix = prefix
        print("prefix: ", prefix, ", context: ", context)

        word_preds = []
        word_probs = []

        lm_results = self.word_predictor.get_words_with_context(prefix, context, self.vocab_id, self.num_predictions,
                                                                self.min_log_prob)
        flattened_results = [freq for sublist in lm_results for freq in sublist]
        flattened_results.sort(key=lambda x: -x[1])
        flattened_results = [word_pair[0] for word_pair in flattened_results[:num_words_total]]

        # print(flattened_results)

        word_dict = {}
        for word_list in lm_results:
            if len(word_list) > 0:
                cur_word_list = []
                for word_pair in word_list:
                    if word_pair[0] in flattened_results:
                        cur_word_list.append(word_pair)
                word_dict[word_list[0][0][len(prefix)]] = cur_word_list

        for key in keys_li:
            key_word_preds = ["", "", ""]
            key_word_probs = [-float("inf"), -float("inf"), -float("inf")]
            if key in word_dict:
                index = 0
                for word_tuple in word_dict[key]:
                    if word_tuple[1] >= self.min_log_prob:
                        key_word_preds[index] = word_tuple[0] + " "
                        key_word_probs[index] = word_tuple[1]
                    index += 1
            word_preds += [key_word_preds]
            word_probs += [key_word_probs]

        key_probs, total_log_prob = self.get_char_probs(word_dict, keys_li)
        word_probs = np.array(word_probs) - total_log_prob

        # nth_min_log_prob = np.partition(word_probs.flatten(), num_words_total)[num_words_total]
        #
        # word_probs = np.where(word_probs >= nth_min_log_prob, word_probs, -float("inf"))
        word_preds = np.where(word_probs != -float("inf"), word_preds, "")
        # word_preds = np.where(word_probs >= nth_min_log_prob, word_preds, "")

        return word_preds.tolist(), word_probs.tolist(), key_probs

    def get_char_probs(self, word_dict, keys_li):
        total_log_prob = -float("inf")
        key_probs = []
        for key in keys_li:
            log_prob = -float("inf")
            if key in word_dict:
                for word in word_dict[key]:
                    log_prob = np.logaddexp(log_prob, word[1])
            if log_prob == -float("inf"):
                log_prob = np.log(kconfig.prob_thres*0.5)
            total_log_prob = np.logaddexp(log_prob, total_log_prob)
            key_probs += [log_prob]

        return key_probs, total_log_prob



def main():

    LM = LanguageModel('../keyboard/resources/lm_word_medium.kenlm', '../keyboard/resources/vocab_100k')
    print(LM.get_words("hello there and ", "", list("abcdefghijklmnopqrstuvwxyz' ")))

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
