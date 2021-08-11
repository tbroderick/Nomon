######################################
#    Copyright 2009 Tamara Broderick
#    This file is part of Nomon Keyboard.
#
#    Nomon Keyboard is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Nomon Keyboard is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Nomon Keyboard.  If not, see <http://www.gnu.org/licenses/>.
######################################


import pickle
from pickle_util import *

pickle.dump(['default', 1, False, 'alpha', 'off', 12, False], open("user_preferences/user_preferences.p", 'wb'))
up_handel = PickleUtil("user_preferences/user_preferences.p")
first_load_handel = PickleUtil("user_preferences/first_load.p")
first_load_handel.safe_save(True)
print(up_handel.safe_load)()