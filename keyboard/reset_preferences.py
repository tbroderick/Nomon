import pickle
from pickle_util import *

pickle.dump(['default', 1, False, 'alpha', 'off', 12, False], open("user_preferences/user_preferences.p", 'wb'))
up_handel = PickleUtil("user_preferences/user_preferences.p")
first_load_handel = PickleUtil("user_preferences/first_load.p")
first_load_handel.safe_save(True)
print(up_handel.safe_load())