import pickle

space_char = '_'
mybad_char = 'Undo'
yourbad_char = 'Undo+'
break_chars = [['.', ',', '?'], '\'']
back_char = 'Backspace'
clear_char = 'Clear'
alpha_key_chars = [['a', 'b', 'c', 'd', 'e'],
                   ['f', 'g', 'h', 'i', 'j'],
                   ['k', 'l', 'm', 'n', 'o',],
                   ['p', 'q', 'r', 's', 't'],
                   ['u', 'v', 'w', 'x', 'y'],
                   ['z', space_char, break_chars[1], break_chars[0][0], break_chars[0][1], break_chars[0][2], back_char,
                    clear_char, mybad_char]]
pickle.dump("True", open("user_preferences/first_load.p", 'wb'))
pickle.dump("med", open("user_preferences/font_scale.p", 'wb'))
pickle.dump("default", open("user_preferences/clock_preference.p", 'wb'))
pickle.dump(True, open("user_preferences/first_load.p", 'wb'))
pickle.dump(alpha_key_chars, open("user_preferences/layout_preference.p", 'wb'))
pickle.dump("corpus/merged_ce-0.2.txt", open("user_preferences/profanity_filter_preference.p", 'wb'))
