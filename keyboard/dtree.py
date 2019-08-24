#!/usr/bin/python

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


import kconfig
import subWindows


class dtree:
    def __init__(self):
        self.head = {}
        self.sum_all_freq = 0

    def add_word(self, word, freq):
        if (len(word) <= 1):
            if ((word != 'i') and (word != 'I') and (word != 'a') and (word != 'A')):
                return

        word = word + '_'
        self.add_string(word, freq)
        self.sum_all_freq += freq

    def add_string(self, word, freq):
        cur_dict = self.head
        for char in word:
            # if key is already there
            if cur_dict.has_key(char):
                # update frequency table if necessary
                value = cur_dict[char]
                top_word_li = value[1]
                top_freq_li = value[2]
                value[3] += freq  # sum over all frequencies
                n = 0
                while n < kconfig.N_pred:
                    if top_freq_li[n] < freq:
                        top_freq_li.pop(kconfig.N_pred - 1)
                        top_word_li.pop(kconfig.N_pred - 1)
                        top_freq_li.insert(n, freq)
                        top_word_li.insert(n, word)
                        n = kconfig.N_pred
                    else:
                        n += 1
            # if key is not already there
            else:
                # create the new 'value' element for the dictionary
                new_dict = {}
                top_freq_li = []
                top_word_li = []
                if kconfig.N_pred > 0:
                    top_word_li.append(word)
                    top_freq_li.append(freq)
                for n in range(1, kconfig.N_pred):
                    top_word_li.append("")
                    top_freq_li.append(0)
                # dictionary, word list, frequency list, sum over frequencies
                value = [new_dict, top_word_li, top_freq_li, freq]
                # add the new element to the dictionary
                cur_dict[char] = value
            # increment
            value = cur_dict[char]
            cur_dict = value[0]

    def get_words(self, prefix):

        cur_dict = self.head
        tot_freq = self.sum_all_freq
        key_freq = self.sum_all_freq
        is_next_char = True
        index = 0
        N_char = len(prefix)
        while is_next_char:
            char = prefix[index]

            # if key is already there
            if cur_dict.has_key(char):
                # increment
                value = cur_dict[char]
                cur_dict = value[0]
                index += 1
                # finish up if at the end of the word
                if index >= N_char:
                    is_next_char = False
                    top_word_li = value[1]
                    top_freq_li = value[2]
                    loc_freq = value[3]
                else:
                    tot_freq = value[3]
            # if key is not already there
            else:
                is_next_char = False
                top_word_li = ["" for index in range(0, kconfig.N_pred)]
                top_freq_li = [0 for index in range(0, kconfig.N_pred)]
                loc_freq = 0

        return (top_word_li, top_freq_li, loc_freq, tot_freq)


class DTree:
    # file_handle: points to the file with the counts
    # ---each line should be: word\scount
    def __init__(self, file_handle, parent):
        ### process the inputs ###
        ## copy
        self.file_handle = file_handle
        self.parent = parent
        ## text during loading
        self.loading_text = [
            "",
            "Quotes from Nomon users:",
            "",
            ">> \"lots of fun\"",
            ">> \"really useful\"",
            "",
            ">> \"The writing system looks intimidating",
            "when it first comes up on the screen",
            "but is actually very easy to use\"",
            "",
            "",
            "[...finished]********************************************************"]

        ### initialize ###
        ## start tree (as empty dictionary)
        self.dt = dtree()
        ## fill tree in
        self.fill_tree()
        
        
# =============================================================================
#     def set_parent(self, parent):
#         self.parent = parent
#         self.fill_tree()
#         
#     def remove_parent(self):
#         self.parent = None
# =============================================================================

    def fill_tree(self):
        n_line = 0
        for line in self.file_handle.xreadlines():
            # read each line
            toks = line.split()
            # if (len(toks) != 2):
                # print "Error: len(toks) = %d" % (len(toks))

            # add word to the tree
            self.dt.add_word(toks[0], int(toks[1]))

            n_line += 1
            if n_line % 20000 == 0:
                if self.loading_text[n_line / 20000] != "":
                    # print self.loading_text[n_line / 20000]
                    subWindows.loading_text = self.loading_text[n_line / 20000]  # send messages to GUI splash screen

                    self.parent.app.processEvents()  # allow splash screen to refresh
        if self.parent.pause_animation:
            self.parent.pause_animation = False

            self.parent.mainWidgit.text_box.setStyleSheet("background-color:;")
            self.parent.mainWidgit.splitter1.setStyleSheet("background-color:;")
            self.parent.mainWidgit.setStyleSheet("background-color:;")
            self.parent.mainWidgit.in_focus = True


    # returns a list (one for each letter)
    # of top-frequency word lists
    # prob_thresh: probability threshold for inclusion
    def get_words(self, prefix, next_char_li):
        top_word_li_li = []
        top_freq_li_li = []
        loc_freq_li = []
        top_freq = 0
        for char in next_char_li:
            loc_prefix = prefix + char
            (word_li, freq_li, loc_freq, tot_freq) = self.dt.get_words(loc_prefix)
            loc_freq_li.append(loc_freq)  # list of the key frequencies
            top_word_li = []
            top_freq_li = []
            for n in range(0, kconfig.N_pred):
                if freq_li[n] > (tot_freq * kconfig.prob_thres):
                    top_word_li.append(word_li[n])
                    top_freq_li.append(freq_li[n])
                    top_freq = max(top_freq, freq_li[n])
                else:
                    top_word_li.append("")
                    top_freq_li.append(0)
            top_word_li_li.append(top_word_li)
            top_freq_li_li.append(top_freq_li)

        return (top_word_li_li, top_freq_li_li, loc_freq_li, top_freq, tot_freq, prefix)


def main():
    # print "in dtree.py"

    # file
    file_name = kconfig.train_file_name_default
    file_handle = open(file_name, 'r')
    # output object
    #out_name = kconfig.train_obj_name
    #out_handle = open(out_name, 'w')

    # dictionary tree
    dt = DTree(file_handle, None)

    # run some checks
    # li = dt.get_words("",map(chr, range(97, 123)))
    # print str(li)

    # store
    # pickle.dump(dt, out_handle)

    # close stuff
    file_handle.close()
    #out_handle.close()

# =============================================================================
# import threading
# 
# class DTreeDict:
#     pass
# 
# class DtreeThread(threading.Thread):
#     def __init__(self, threadID, threadingDict, load):
#         threading.Thread.__init__(self)
#         self.threadID = threadID
#         self.threadingDict = threadingDict
#         #If True, load if False, save
#         self.load = load
#         
#     def run(self):
#         if self.load:
#             
#             
#             
#             
#         else:
# =============================================================================
            
        

if __name__ == "__main__":
    main()
