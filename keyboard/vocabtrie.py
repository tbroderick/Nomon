#!/usr/bin/python
import kenlm

class VocabTrieNode:
    def __init__(self, info = None):
        self.children = dict()
        self.info = info


class VocabTrie(object):
    def __init__(self):
        self.root = VocabTrieNode()

    def add_word(self, word):
        current = self.root
        for character in word:
            # char_id = ord(character)
            # If character is in the current node's children list,
            # then make the child with the character as current node
            if character in current.children:
                current = current.children[character]

            # Character is not a child of current node, add this character
            # to the children list and make new child as the current node
            else:
                current.children[character] = VocabTrieNode()
                current = current.children[character]
        # We are at the end of a word. Save the word as the info for the
        # current node. It is better than assigning a boolean since we will
        # be able to access a word by checking if info is a non-None value
        current.info = word

    def contains_word(self, word):
        current = self.root
        for character in word:
            if character in current.children:
                current = current.children[character]
                if current.info == word:
                    return True
            else:
                return False
        return False





    def get_words_with_prefix(self, prefix, model, state_in, state_out):
        suggestion_list = []
        words = []
        log_probs = []

        current = self.root
        for character in prefix:
            # char_id = ord(character)
            # If character is a valid entry in the trie data strucutre
            # then make it the current node
            if character in current.children:
                current = current.children[character]

            # Character X is not a valid entry in the trie. It means there are no
            # suggestions starting with prefix *X [e.g. a5, where a is in trie,
            # but 5 is not]. In this case return an empty list.
            else:
                return suggestion_list

        queue = []
        if current == self.root:
            # If current node is the root node then add all the children of
            # the root node to the queue
            for key, item in current.children.iteritems():
                queue.append(item)
        # Else add just the current node in the queue
        else:
            queue.append(current)

        while queue:
            # Pop an item from the queue
            temp = queue.pop()

            # If the node popped from queue is the end of a valid word i.e. if
            # the node popped has a word that we saved as info
            if temp.info != None:
                word = temp.info
                #words.append(word)
                # Calculate word log probability using kenlm
                log_prob = model.BaseScore(state_in, word, state_out)
                #log_probs.append(log_prob)

                # Make a pair of the word and its associated log probability
                # and add them to the suggestion list
                pair = (word, log_prob)
                suggestion_list.append(pair)

            # Add all the children of the node to the queue
            for key, item in temp.children.items():
                queue.append(item)

        return suggestion_list



def main():
    vt = VocabTrie()

    state_in = kenlm.State()
    state_out = kenlm.State()
    model = kenlm.LanguageModel('resources/lm_word_medium.kenlm')

    vt.add_word('hel')
    vt.add_word('help')
    vt.add_word('hi')
    vt.add_word('hello')
    vt.add_word('hellboy')
    vt.add_word('helen')

    print(vt.contains_word('hell'))

    print(vt.get_words_with_prefix('he', model, state_in, state_out))



if __name__ == "__main__":
    main()
