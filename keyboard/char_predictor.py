import os
import kenlm  # pip install https://github.com/kdv123/kenlm/archive/master.zip

class CharacterPredictor:
    def __init__(self, lm_filename, character_filename):
        self.language_model = kenlm.LanguageModel(lm_filename)
        self.character_filename = character_filename
        self.char_list = self.create_char_list_from_charfile(character_filename)


    def create_char_list_from_charfile(self, character_filename):
        char_list = set()
        try:
            fp = open(character_filename)
            # Skip the first 5 lines
            for _ in range(5):
                next(fp)
            for line in fp:
                line = line.strip()
                for char in line:
                    char_list.add(char)
        except:
            print('Error: Can\'t find or read token file')

        return char_list

    def get_context_state(self, context, model):
        state_in = kenlm.State()
        state_out = kenlm.State()
        context = '<s> ' + context
        context_words = context.split()
        for w in context_words:
            print('Context', '{0}\t{1}'.format(model.BaseScore(state_in, w, state_out), w))
            state_in = state_out
            state_out = kenlm.State()

        return state_in, state_out

    def format_context(self, context):
        new_context = ''
        for character in context:
            if character == ' ':
                new_context += '<sp> '
            else:
                new_context += character + ' '

        #print(new_context)
        return new_context


    def get_characters(self, context = '', num_predictions = 0, min_log_prob = -float('inf')):
        #context = context + ' ' + prefix
        context = self.format_context(context)
        state_in, state_out = self.get_context_state(context, self.language_model)
        char_list = self.char_list
        char_list.add(' ')

        character_list_probs = []

        for character in char_list:
            if character == ' ':
                log_prob = self.language_model.BaseScore(state_in, '<sp>', state_out)
            else:
                log_prob = self.language_model.BaseScore(state_in, character, state_out)
            character_list_probs.append((character, log_prob))

        nbest_char_list_probs = sorted(character_list_probs, key=lambda x: float(x[1]), reverse=True)

        if num_predictions < 1:
            return nbest_char_list_probs
        else:
            return nbest_char_list_probs[:num_predictions]

    def get_most_probable_character(self, context = '', vocab_id = '', min_log_prob = -float('inf')):
        #context = context + ' ' + prefix
        context = self.format_context(context)
        state_in, state_out = self.get_context_state(context, self.language_model)
        char_list = self.char_list
        char_list.add(' ')

        #print(char_list[vocab_id])
        max_prob_char = ''
        max_log_prob = min_log_prob

        for character in char_list:
            #print(character)
            if character == ' ':
                log_prob = self.language_model.BaseScore(state_in, '<sp>', state_out)
            else:
                log_prob = self.language_model.BaseScore(state_in, character, state_out)

            if log_prob > max_log_prob:
                max_log_prob = log_prob
                max_prob_char = character
            #print(character, log_prob)

        return max_prob_char, max_log_prob

    def print_probable_char_list(self, char_list_with_logprobs):
        if char_list_with_logprobs == None:
            return
        print('Character \t| Log probability')
        for char, prob in char_list_with_logprobs:
            print('' + char + '\t|' + str(prob))


def main():
    lm_filename = 'resources/mix4_opt_min_lower_12gram_6e-9_prob9_bo4_compress255.kenlm'
    character_filename = 'resources/char_set.txt'

    char_predictor = CharacterPredictor(lm_filename, character_filename)
    # print(char_predictor.get_most_probable_character('the united states of '))
    # char_list_with_logprobs = char_predictor.get_characters('the united states of ')
    # char_predictor.print_probable_char_list(char_list_with_logprobs)

    print(char_predictor.get_characters('hello there my name is nick'))


if __name__ == "__main__":
    main()