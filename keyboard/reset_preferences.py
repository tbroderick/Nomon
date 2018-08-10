import pickle
from pickle_util import *

pickle.dump(['default', 1, False, 'alpha', 'off', 12, False], open("user_preferences/user_preferences.p", 'wb'))
up_handel = PickleUtil("user_preferences/user_preferences.p")
print (up_handel.safe_load())