#!/usr/bin/python

import os
import kenlm  # pip install https://github.com/kdv123/kenlm/archive/master.zip
import vocabtrie


class WordPredictor:
    def __init__(self, lm_filename, vocab_filename):
        # self.lm_filename = lm_filename
        self.vocab_filename = vocab_filename
        self.language_model = kenlm.LanguageModel(lm_filename)
        self.char_list = {}
        self.char_list[''] = self.create_char_list_from_vocab('', vocab_filename)
        self.trie_table = {}
        self.trie_table[''] = self.create_new_trie(vocab_filename)

        # Omit the first two dots and the slash in the path if you are running predictor.py
        self.token_list = self.get_punctuation_tokens('/keyboard/resources/tokens.txt')

    # Given a filename, this method creates a new trie data
    # structure for the words in the file
    def create_new_trie(self, vocab_filename):
        word_list = []
        new_vocab_trie = vocabtrie.VocabTrie()

        try:
            fp = open(vocab_filename)
            for line in fp:
                line = line.strip()
                word_list.append(line)
                new_vocab_trie.add_word(line)
        except IOError:
            print('Error: Can\'t find or read vocab file')
        return new_vocab_trie

    # Function to update character list
    @staticmethod
    def update_char_list_from_string(char_list, string):
        for char in string:
            char_list.append(char)
        return char_list

    # Given a vocab_id and vocab_filename, the following function adds every
    # unique character of the vocabulary in a character list
    def create_char_list_from_vocab(self, vocab_id, vocab_filename):
        char_list = set()

        try:
            fp = open(vocab_filename)
            for line in fp:
                line = line.strip()
                for char in line:
                    char_list.add(char)
        except IOError:
            print('Error: Can\'t find or read vocab file')

        return char_list

    def get_punctuation_tokens(self, token_filename):
        token_list = dict()

        try:
            fp = open(token_filename)
            # Skip the first 10 lines
            for _ in range(10):
                next(fp)
            for line in fp:
                punc, token = line.split('\t')
                token_list[punc] = token
        except IOError:
            print('Error: Can\'t find or read token file')

        return token_list

    # This method adds a vocabulary to the instance of the class. The vocabulary
    # is saved as a Trie data structure. For multiple vocabularies, the Tries are
    # mapped in a hash table with a vocab_id.
    # The trie can be accessed by the vocab_id provided
    def add_vocab(self, vocab_id, vocab_filename):
        if self.trie_table.has_key(vocab_id):
            print('Vocabulary with id "' + vocab_id + '" already exists, try a new id.')
            return False
        # Create a new trie for the new vocabulary
        new_trie = self.create_new_trie(vocab_filename)
        # Add the new trie to the trie table
        self.trie_table[vocab_id] = new_trie

        # Create a new character list from the vocabulary and add it to the existing table
        self.char_list[vocab_id] = self.create_char_list_from_vocab(vocab_id, vocab_filename)
        print('Vocab with id ' + vocab_id + ' added successfully')
        return True

    # Given a vocab_id, this method returns the trie from the trie table that
    # is referenced by the vocab_id
    def get_vocab_trie(self, vocab_id):
        if vocab_id in self.trie_table:
            return True, self.trie_table[vocab_id]
        else:
            # print('Error! Vocabulary with id "' + vocab_id + ' " has not been found.')
            return False, None

    # This function formats the context so that it is compatible
    # with the language model we use. First, it tokenizes the
    # punctuations then it maps any out of vocabulary words to 'UNK'
    def format_context(self, context, vocab_id):
        tokenize_context = ''
        for character in context:
            if character in self.token_list:
                tokenize_context += ' ' + self.token_list[character] + ' '
            else:
                tokenize_context += character

        # Load the trie with the given vocab_id
        # We want to check if any word in the context
        # is out of vocabulary. If a word is out of the
        # vocabulary, then we replace the word with <unk>
        trie = self.trie_table[vocab_id]

        words = tokenize_context.split()
        new_context = ''
        for word in words:
            if trie.contains_word(word):
                new_context += word + ' '
            else:
                new_context += '<unk>' + ' '
                print('Vocab does not contain word ' + word)

        # print(new_context)
        return new_context

    # This method returns the kenlm states for the given context
    def get_context_state(self, context, model, vocab_id):
        state_in = kenlm.State()
        state_out = kenlm.State()
        context = '<s> ' + self.format_context(context, vocab_id)
        context_words = context.split()
        for w in context_words:
            # print('Context', '{0}\t{1}'.format(model.BaseScore(state_in, w.lower(), state_out), w.lower()))
            print('Context', '{0}\t{1}'.format(model.BaseScore(state_in, w, state_out), w))
            state_in = state_out
            state_out = kenlm.State()

        return state_in, state_out

    def get_words(self, prefix='', vocab_id='', num_predictions=0, min_log_prob=float('inf')):
        return self._get_words(prefix, '', vocab_id, num_predictions, min_log_prob)

    def get_words_with_context(self, prefix='', context='', vocab_id='', num_predictions=0, min_log_prob=float('inf')):
        return self._get_words(prefix, context, vocab_id, num_predictions, min_log_prob)

    def _get_words(self, prefix, context, vocab_id, num_predictions, min_log_prob):
        (state_in, state_out) = self.get_context_state(context, self.language_model, vocab_id)

        flag, current_trie = self.get_vocab_trie(vocab_id)
        if flag == False:
            return []

        most_prob_word = ''
        most_prob_word_log = min_log_prob

        suggestion_list = []
        for char in self.char_list[vocab_id]:
            new_prefix = prefix + char
            # print(new_prefix)
            words_with_logprob = current_trie.get_words_with_prefix(new_prefix, self.language_model, state_in,
                                                                    state_out)

            # update the most probable word
            most_prob_word, most_prob_word_log = self.find_most_probable_word(words_with_logprob, most_prob_word,
                                                                              most_prob_word_log)

            # sort the most probable words for this prefix
            likely_words_with_logprob = sorted(words_with_logprob, key=lambda x: float(x[1]), reverse=True)

            # add the most probable words to the suggestion list for this prefix
            if num_predictions < 1:
                suggestion_list.append(likely_words_with_logprob)
            else:
                suggestion_list.append(likely_words_with_logprob[:num_predictions])

        return suggestion_list

    def get_most_probable_word(self, prefix, context='', vocab_id='', min_log_prob=-float('inf')):
        (state_in, state_out) = self.get_context_state(context, self.language_model, vocab_id)
        most_prob_word = ''
        most_prob_word_log = min_log_prob

        flag, current_trie = self.get_vocab_trie(vocab_id)
        if flag == False:
            return most_prob_word, most_prob_word_log

        words_with_log_prob = current_trie.get_words_with_prefix(prefix, self.language_model, state_in, state_out)
        # Update the most probable word
        most_prob_word, most_prob_word_log = self.find_most_probable_word(words_with_log_prob, most_prob_word,
                                                                          most_prob_word_log)

        # Print the most probable word if needed
        # print('Context: ' + context)
        # print('Prefix: ' + prefix)
        # print('Most likely word: "' + most_prob_word + '" with log probability: ' + str(most_prob_word_log))

        return most_prob_word, most_prob_word_log

    # Input: a list of probable words and their proability for a list of prefix
    # Example: [[0, [['a', -2.04],['aa', -3.04],['ab', -2.04]]], [[1, [['b', -2.04],['ba', -3.04],['bb', -2.04]]] .....]
    def print_suggestions(self, suggestion_list):
        if suggestion_list == None:
            print("Word list is empty.")
            return
        print('--------------------------------------------')
        print('Word\tProbability')
        print('--------------------------------------------')
        for i, word_list in enumerate(suggestion_list):
            for w, p in word_list:
                print('' + w + '\t' + str(p))

    def find_most_probable_word(self, word_list, prob_word, max_log_prob):
        word = prob_word
        log_prob = max_log_prob
        for w, p in word_list:
            if p > log_prob:
                word = w
                log_prob = p
        return word, log_prob


def main():
    lm_filename = 'resources/lm_word_medium.kenlm'
    vocab_filename = 'resources/vocab_100k'
    word_predictor = WordPredictor(lm_filename, vocab_filename)

    # print(predictor.create_char_list_from_vocab(vocab_filename))

    # words = predictor.get_words_with_context('s', 'abra ka dabra', '', 3, -float('inf'))
    # predictor.print_suggestions(words)

    words = word_predictor.get_words_with_context('', 'hello', '', 3, -float('inf'))
    word_predictor.print_suggestions(words)
    # print(predictor.get_most_likely_word(words))
    # predictor.add_vocab('vocab_100k', vocab_filename)

    prefix = 'a'
    context = 'the united states of'
    most_prob_word, log_prob = word_predictor.get_most_probable_word(prefix, context, vocab_id='',
                                                                     min_log_prob=-float('inf'))

    print('Context: ' + context)
    print('Prefix: ' + prefix)
    print('Most probable word: "' + most_prob_word + '" with log probability: ' + str(log_prob))


if __name__ == "__main__":
    main()
