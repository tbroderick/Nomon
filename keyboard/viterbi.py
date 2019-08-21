
# from clock_util import SpacedArray
from pickle_util import PickleUtil
import config
import kconfig
import warnings
from matplotlib import pyplot as plt
import multiprocessing as mp
import pandas as pd
import numpy as np
import os

np.seterr(divide='ignore')
np.set_printoptions(linewidth=np.inf)


########################################################################################################################
#                                               Utility Functions                                                      #
########################################################################################################################


def normal_hist(mu, sigma):
    """
    Generates a 1D numpy array of length 80 of normal probabilities. Probabilities wrap and add over edges.

    :param mu: float -- mean
    :param sigma: float -- standard deviation

    :return: array of probabilities
    """
    n_bars = 80
    bars = (np.arange(n_bars) - n_bars//2)
    bars_over = (np.arange(n_bars) + n_bars//2)
    bars_under = (np.arange(n_bars) - n_bars*3//2)
    out = np.exp(-np.square(bars - mu) / (2 * sigma ** 2)) / np.sqrt(2 * np.pi * sigma ** 2)
    out += np.exp(-np.square(bars_over - mu) / (2 * sigma ** 2)) / np.sqrt(2 * np.pi * sigma ** 2)
    out += np.exp(-np.square(bars_under - mu) / (2 * sigma ** 2)) / np.sqrt(2 * np.pi * sigma ** 2)
    return out/np.sum(out)


def get_char_prior(char_index, S, LM, left_context):
    """
    Calculates the prior over the state space (S) aggregated over the entire language model (LM) at a particular
    index (char index) in all words. EG the 'e' in 'hello' is char_index = 1. Will store priors in pickle file to
    minimize computation time.

    :param char_index:  int -- character index in word to compute prior over
    :param S: list -- state space of characters
    :param LM: a Language Model

    :return: numpy array (1, len(S)) -- prior over state space S
    """

    if not os.path.exists("resources"):
        os.mkdir("resources")
    if not os.path.exists("resources\\char_probs"):
        os.mkdir("resources\\char_probs")

    char_prior = PickleUtil('resources\\char_probs\\char_index'+str(char_index)+'.p').safe_load()
    if char_prior is not None:
        return char_prior

    words = LM.get_all_words('', left_context)
    words = [word for word in words if len(word[0]) > char_index]

    words, word_probs = list(zip(*words))

    word_probs = np.array(word_probs)
    index_chars = np.array([word[char_index] for word in words]).T

    char_prior = []
    for s in S:
        state_chars = np.where(index_chars == s)
        state_probs = word_probs[state_chars]

        log_char_prior = -float("inf")
        for log_prob in state_probs:
            log_char_prior = np.logaddexp(log_char_prior, log_prob)

        char_prior += [log_char_prior]

    char_prior = np.array(char_prior)

    char_prior[np.where(np.array(S) == " ")] = np.max(char_prior)

    log_prob_sum = - float("inf")
    for log_prob in char_prior:
        log_prob_sum = np.logaddexp(log_prob_sum, log_prob)

    char_prior = char_prior - log_prob_sum
    char_prior = np.array([char_prior])

    PickleUtil('resources\\char_probs\\char_index' + str(char_index) + '.p').safe_save(char_prior)
    return char_prior


def expand_x_matrix(X, P, S):
    """
    Expands hidden state probability matrix to include zero-probability states

    :param X: array -- non-zero state space
    :param P: array -- non-zero state probabilities
    :param S: list -- full state space

    :return: array (len(S), 1) probability array ordered by S
    """
    Y = np.full(len(S), 0.0)
    S_index_dict = dict([(letter, S.index(letter)) for letter in S])

    for letter, probability in zip(X, P):
        Y[S_index_dict[letter]] = probability
    return Y


def find_words_from_prefix(prefix, left_context, S_given_Y, LM, word_dict=None):
    """
    Recursively finds all words with a given prefix and constructs a dictionary mapping prefix to words (word_dict).

    :param prefix: str -- starting prefix for recursive search
    :param left_context: str -- left context for language model
    :param S_given_Y: list of lists (n, ?) -- non-zero-probability state space given each observation
    :param LM: a Language Model
    :param word_dict: dict -- empty dictionary to store recursive results

    :return: word_dict
    """

    word_length = len(prefix) + len(S_given_Y)

    if word_dict is None:
        word_dict = dict()

    if len(S_given_Y) > 0:
        for letter in S_given_Y[0]:
            new_prefix = prefix + letter
            new_prefix_words = LM.get_all_words(new_prefix, left_context)
            new_prefix_words = [word for word in new_prefix_words if len(word[0]) == word_length]

            if len(new_prefix_words) > 0:
                word_dict[new_prefix] = new_prefix_words

                find_words_from_prefix(prefix+letter, left_context, S_given_Y[1:], LM, word_dict)

    return word_dict


########################################################################################################################
#                                            Markov Chain Functions                                                    #
########################################################################################################################


def gen_transition(X_given_Y, S, LM, left_context):
    """
    Computes the transition matrix (T) for the Markov Chain. Computes all words of length n (n_words).

    :param X_given_Y: list of numpy array tuples (n, 2) -- The posterior distribution over the state space (S) for each
                        observation. All 0 probability events are removed. Tuples take the form:
                        (array_of states, array_of_probabilities)
    :param S: list -- state space of characters
    :param LM: a Language Model
    :param left_context: left context for language model

    :return: tuple -- (transition Matrix, n_words)
    """
    n = len(X_given_Y)
    T = [np.full((len(S), len(S)), -float("inf")) for i in range(n)]
    S_given_Y = [i[0] for i in X_given_Y]

    S_index_dict = dict([(letter, S.index(letter)) for letter in S])

    word_dict = find_words_from_prefix("", left_context, S_given_Y, LM)

    for prefix in word_dict:
        t_index = len(prefix)
        X_i_minus_one = prefix[-1]

        S_i = X_given_Y[t_index][0]

        for X_i in S_i:
            transition_prob = - float('inf')

            for word in word_dict[prefix]:
                if X_i == word[0][t_index]:
                    transition_prob = np.logaddexp(transition_prob, word[1])

            if transition_prob != - float('inf'):
                T[t_index][S_index_dict[X_i_minus_one], S_index_dict[X_i]] = transition_prob

    for t_index in range(1, n):

        for X_i_minus_one in X_given_Y[t_index-1][0]:
            T_row = T[t_index][S_index_dict[X_i_minus_one]]
            T_values = [i for i in T_row.tolist() if i != - float('inf')]

            log_prob_sum = -float("inf")
            for log_prob in T_values:
                log_prob_sum = np.logaddexp(log_prob_sum, log_prob)

            if log_prob_sum != -float("inf"):
                T[t_index][S_index_dict[X_i_minus_one]] -= log_prob_sum
            else:
                T[t_index][S_index_dict[X_i_minus_one]] = np.full(len(S), -np.log(len(S)))
    n_words = word_dict.values()
    n_words = set([i for w in n_words for i in w])  # flatten dictionary values lists

    return T, n_words


def viterbi(X_given_Y, S, T_matrix):
    """
    Finds the most probable sequence of hidden states (X*) given the observations (Y) using the Viterbi algorithm.

    :param X_given_Y: list of numpy array tuples (n, 2) -- The posterior distribution over the state space (S) for each
                        observation. All 0 probability events are removed. Tuples take the form:
                        (array_of states, array_of_probabilities)
    :param S: list -- state space of characters
    :param T_matrix: array (n, len(S), len(S)) transition matrix of probabilities of transitioning from state s-1
                        to state s in each state index.

    :return: tuple -- most probable sequence of hidden states and probability
    """
    n = len(X_given_Y)
    X = np.array([np.log(expand_x_matrix(X_given_Y[i][0], X_given_Y[i][1], S)) for i in range(n)])
    S_index_dict = dict([(letter, S.index(letter)) for letter in S])

    back_pointer = np.full((len(S), n), -float("inf"))
    prob_matrix = np.full((len(S), n), -float("inf"))
    prob_matrix.T[0] = X[0]

    for time in range(1, n):
        for state in range(len(S)):
            prob_matrix[state, time] = np.max(prob_matrix[:, time-1] + T_matrix[time].T[state] + X[time][state])
            back_pointer[state, time] = np.argmax(prob_matrix[:, time - 1] + T_matrix[time].T[state] + X[time][state])

    best_path_prob = np.exp(np.max(prob_matrix[:, n-1]))
    best_path_pointer = np.argmax(prob_matrix[:, n-1])

    best_path = []
    for time in range(n-1, -1, -1):
        if time == n-1:
            best_path = [best_path_pointer] + best_path
        else:
            best_path = [back_pointer[:, time+1][int(best_path[0])]] + best_path

    most_probable_word = "".join([S[int(index)] for index in best_path])

    return most_probable_word, best_path_prob


def modified_viterbi(X_given_Y, S, T_matrix, n_words):
    """
    Finds the most probable sequence of hidden states (X*) given the observations (Y) constrained to the requirement
    that X is a word. Computes all words of length n that contain only characters of non-zero probability in the
    posterior distribution of X (X_given Y) for each index in the word (valid_words). Computes the forward probability
    of each hidden state sequence in valid_words returns the top 4.

    :param X_given_Y: list of numpy array tuples (n, 2) -- The posterior distribution over the state space (S) for each
                        observation. All 0 probability events are removed. Tuples take the form:
                        (array_of states, array_of_probabilities)
    :param S: list -- state space of characters
    :param T_matrix: array (n, len(S), len(S)) transition matrix of probabilities of transitioning from state s-1
                        to state s in each state index.
    :param n_words: set -- all words of length n

    :return: list of tuples -- top 4 most probable sequence of hidden states and probabilities
    """
    n = len(X_given_Y)
    X = np.array([np.log(expand_x_matrix(X_given_Y[i][0], X_given_Y[i][1], S)) for i in range(n)])
    # print([x[0] for x in X_given_Y])
    S_index_dict = dict([(letter, S.index(letter)) for letter in S])

    for char_index in range(n):
        remove_later = set()
        valid_chars = set(X_given_Y[char_index][0])
        for word in n_words:
            if word[0][char_index] not in valid_chars:
                remove_later.add(word)
        n_words -= remove_later

    if len(n_words) == 0:
        return [viterbi(X_given_Y, S, T_matrix)]

    valid_words, word_priors = list(zip(*n_words))
    word_priors = np.array([word_priors]).T

    log_prob_sum = -float("inf")
    for log_prob in word_priors:
        log_prob_sum = np.logaddexp(log_prob_sum, log_prob)
    word_priors -= log_prob_sum

    hmm_probs = []
    for word in valid_words:
        sequence_prob = np.full((n, 1), -float("inf"))
        sequence_prob[0] = X[0][S_index_dict[word[0]]]

        for time in range(1, n):
            prior_state_index = S_index_dict[word[time - 1]]
            state_index = S_index_dict[word[time]]

            sequence_prob[time] = sequence_prob[time - 1] + T_matrix[time][prior_state_index][state_index] + X[time][
                state_index]

        hmm_probs += [sequence_prob[-1]]

    hmm_probs = np.array(hmm_probs)

    log_prob_sum = -float("inf")
    for log_prob in hmm_probs:
        log_prob_sum = np.logaddexp(log_prob_sum, log_prob)
    hmm_probs -= log_prob_sum

    posterior_probs = word_priors + hmm_probs
    posterior_probs = posterior_probs.T[0]

    most_probable_sequences = []

    for i in range(min(4, len(valid_words))):
        max_index = np.argmax(posterior_probs)
        most_probable_sequences += [(valid_words[max_index], posterior_probs[max_index])]
        posterior_probs[max_index] = -float("inf")

    return most_probable_sequences


########################################################################################################################
#                                             Simulation Functions                                                     #
########################################################################################################################


def simulate_presses(target_word, S, LM, left_context, hist):
    char_array = np.array(S)

    prob_array = np.array(np.arange(len(S)) / len(S) * 80, dtype="int64")
    prob_array = np.array([hist[i] for i in prob_array])
    prob_array /= np.sum(prob_array)

    center_index = np.argmax(prob_array)

    X_given_Y = []
    for char_index, char in enumerate(target_word):
        SA = SpacedArray(len(S)-1).arr

        char_prior = get_char_prior(char_index, S, LM, left_context)
        sorting_array = np.append(np.array([S], dtype=object), -char_prior, axis=0).T

        sorted_chars = sorting_array[sorting_array[:, 1].argsort()].T[0]
        char_array = sorted_chars[SA]

        target_index = np.int(np.where(char_array == char)[0])

        noise_index = np.int((np.random.choice(80, 1, p=hist) - 40) / 80 * len(S))

        char_array[[target_index, center_index + noise_index]] = char_array[[center_index + noise_index, target_index]]

        X_given_Y += [[char_array[np.where(prob_array > 0.01)], prob_array[np.where(prob_array > 0.01)]]]

    return X_given_Y


def run_simulation(num_iter, vocab, S, hist, LM, left_context=""):
    vocab_size = len(vocab)

    success_rate = 0
    for i in range(num_iter):
        target_word = vocab[i]
        n = len(target_word)

        X_given_Y = simulate_presses(target_word, S, LM, left_context, hist)

        T, word_dict = gen_transition(X_given_Y, S, LM, left_context)

        mpc = modified_viterbi(X_given_Y, S, T, word_dict)
        words = [i for j in mpc for i in j]
        success_rate += target_word in words

        if i % (num_iter // 20) == 0 and i != 0:
            print(round(i * 100 / num_iter, 0), "%")
    success_rate /= num_iter
    return success_rate


def main():
    lm_filename = 'resources/lm_word_medium.kenlm'
    vocab_filename = 'resources/vocab_100k'
    LM = WordPredictor(lm_filename, vocab_filename)

    S = list("abcdefghijklmnopqrstuvwxyz'")

    hist = PickleUtil("resources/click_distributions/69_hist.p").safe_load()
    # hist = normal_hist(0, 1)
    # plt.plot(hist)
    # plt.show()
    hist /= np.sum(hist)

    left_context = ""

    vocab_file = open("resources/vocab_100k", 'r')
    vocab = np.array(vocab_file.read().split())
    vocab_file.close()
    np.random.shuffle(vocab)
    vocab_size = len(vocab)

    iterations = vocab_size // 100

    pool = mp.Pool(7)
    result = pool.starmap(run_simulation, [(iterations//7, vocab, S, hist, LM, left_context) for i in range(7)])
    final_avg = np.average(result)*100
    final_std = np.std(result)*100
    print("Success Rate: ", final_avg, '+/-', final_std)


if __name__ == '__main__':
    main()
