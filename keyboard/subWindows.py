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


from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia

from widgets import ClockWidget, OldClockWidget, VerticalSeparator, HorizontalSeparator
from pretraininginference import PreBroderClocks

import sys
import os
from numpy import pi, zeros, array
import time
import config
import kconfig
from pickle_util import PickleUtil

sys.path.insert(0, os.path.realpath('../KernelDensityEstimation'))


class StartWindow(QtWidgets.QMainWindow):
    def __init__(self, screen_res, help_screen):
        super(StartWindow, self).__init__(parent=None)
        self.screen_res = screen_res
        self.help_screen = help_screen
        self.central_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.screen_num = 0
        self.next_screen()

        w = 700
        h = 500

        self.setGeometry((self.screen_res[0] - w) / 2, (self.screen_res[1] - h) / 2, w, h)
        self.setWindowTitle('Nomon SimulatedUser')
        self.setWindowIcon(QtGui.QIcon('icons/nomon.png'))

    def next_screen(self):
        self.screen_num += 1
        if self.screen_num == 1:
            self.mainWidget = WelcomeScreen1(self)
        elif self.screen_num == 2:
            self.mainWidget = WelcomeScreen2(self)
        elif self.screen_num == 3:
            self.mainWidget = WelcomeScreen3(self)
        elif self.screen_num == 4:
            if self.help_screen:
                self.saved_data = True
                self.close()
            self.mainWidget = PretrainScreen1(self)
        elif self.screen_num == 5:
            self.setGeometry(self.screen_res[0] * 0.05, self.screen_res[1] * 0.0675, self.screen_res[0] * 0.9,
                             self.screen_res[1] * 0.85)
            self.mainWidget = PretrainScreen(self)
        else:
            raise IndexError("Screen index "+str(self.screen_num)+" out of range for dim 5")
        self.central_widget.addWidget(self.mainWidget)
        self.central_widget.setCurrentWidget(self.mainWidget)


    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Space:
            if self.screen_num < 5:
                self.next_screen()
            else:
                self.on_press()
        e.accept()


class WelcomeScreen1(QtWidgets.QWidget):
    def __init__(self, parent):
        super(WelcomeScreen1, self).__init__(parent)
        self.size_factor = 1
        self.high_contrast = False
        self.alignment = 'cr'
        self.color_index = 0
        self.in_focus = True

        # mainwindow.setWindowIcon(QtGui.QIcon('PhotoIcon.png'))

        vbox = QtWidgets.QVBoxLayout()

        hbox = QtWidgets.QHBoxLayout()

        self.loading_clock = OldClockWidget('a', self)
        self.loading_clock.highlighted = True
        self.loading_clock.setMinimumSize(200, 200)

        self.timer = QtCore.QBasicTimer()
        self.timer.start(15, self)
        self.step = 0

        self.sub_label_1 = QtWidgets.QLabel(
            "To select an option, find the adjacent clock and press when the moving hand "
            "is near Noon.")
        self.sub_label_2 = QtWidgets.QLabel("<i>(press to continue)</i>")

        self.sub_label_1.setWordWrap(True)
        loading_label = QtWidgets.QLabel("<b>Welcome to the Nomon SimulatedUser!</b>")
        loading_label.setFont(config.welcome_main_font[1])

        self.sub_label_1.setFont(config.welcome_sub_font[1])
        self.sub_label_2.setFont(config.welcome_sub_font[1])

        hbox.addStretch(1)
        hbox.addWidget(self.loading_clock, 2)
        hbox.addStretch(1)
        vbox.addWidget(loading_label)
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        vbox.addWidget(self.sub_label_1, 1)
        vbox.addWidget(self.sub_label_2, 1, QtCore.Qt.AlignRight)

        self.setLayout(vbox)

    def timerEvent(self, e):
        self.step += pi / 64

        if self.step >= pi * 2:
            self.step = -pi
            self.loading_clock.angle = 0
            self.loading_clock.update()

        if self.step > 0:
            self.loading_clock.angle = self.step
            self.loading_clock.update()
#
#
# noinspection PyArgumentList


class WelcomeScreen2(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(WelcomeScreen2, self).__init__(parent)
        self.size_factor = 1
        self.high_contrast = False
        self.alignment = 'cr'
        self.color_index = 0
        self.in_focus = True

        self.header_label = QtWidgets.QLabel("<b>There are 2 types of clocks..</b>")
        self.sub_label_1 = QtWidgets.QLabel("<b>Highlighted</b>")
        self.sub_label_2 = QtWidgets.QLabel("<b>Regular</b>")
        self.sub_label_3 = QtWidgets.QLabel("<b>&</b>")
        self.sub_label_4 = QtWidgets.QLabel("<i>(press to continue)</i>")

        self.header_label.setFont(config.welcome_main_font[1])
        self.sub_label_1.setFont(config.welcome_main_font[1])
        self.sub_label_2.setFont(config.welcome_main_font[1])
        self.sub_label_3.setFont(config.welcome_main_font[1])

        self.highlighted_clock = OldClockWidget('', self)
        self.highlighted_clock.highlighted = True
        self.highlighted_clock.angle = 1
        self.highlighted_clock.setMinimumSize(150, 150)

        self.regular_clock = OldClockWidget('', self)
        self.regular_clock.angle = 1
        self.regular_clock.setMinimumSize(150, 150)

        self.main_text_label = QtWidgets.QLabel(
            "Nomon believes <b>highlighted clocks</b> have a higher probability of being "
            "selected next--so they take <b>fewer presses</b> to select. If you wish to "
            "select a <b>regular clock</b>, then you should press as <b>accurately</b> as "
            "possible!")

        self.main_text_label.setFont(config.welcome_sub_font[1])
        self.main_text_label.setWordWrap(True)
        self.sub_label_4.setFont(config.welcome_sub_font[1])

        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.header_label, 0, 0, 1, 5)

        grid.addWidget(self.highlighted_clock, 1, 1)
        grid.addWidget(self.sub_label_3, 1, 2, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
        grid.addWidget(self.regular_clock, 1, 3, QtCore.Qt.AlignHCenter)

        grid.addWidget(self.sub_label_1, 2, 1, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
        grid.addWidget(self.sub_label_2, 2, 3, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

        grid.addWidget(self.main_text_label, 3, 0, 1, 5)
        grid.addWidget(self.sub_label_4, 4, 3, 1, 2)
        grid.setRowStretch(2, 1)
        grid.setRowStretch(3, 1)
        self.setLayout(grid)


class WelcomeScreen3(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(WelcomeScreen3, self).__init__(parent)
        self.size_factor = 1
        self.high_contrast = False
        self.alignment = 'cr'
        self.color_index = 0
        self.in_focus = True
        self.parent = parent

        self.header_label = QtWidgets.QLabel("<b>Alternate Clock designs are located in the View Menu</b>")

        self.header_label.setFont(config.welcome_main_font[1])
        self.header_label.setWordWrap(True)

        self.picture_timer = QtCore.QTimer()
        self.picture_timer.start(4000)
        self.picture_timer.timeout.connect(self.change_picture)
        self.picture_label = QtWidgets.QLabel()
        self.menu_picture = QtGui .QPixmap('icons/clock_menu.png')
        self.pic_width = self.parent.geometry().width()*0.95
        self.pic_cycle = 0
        self.menu_picture = self.menu_picture.scaledToWidth(self.pic_width)

        self.picture_label.setPixmap(self.menu_picture)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.header_label, 1)
        vbox.addWidget(self.picture_label, 10)
        self.setLayout(vbox)

    def change_picture(self):
        self.pic_cycle += 1
        if self.pic_cycle > 2:
            self.pic_cycle = 0
        if self.pic_cycle == 0:
            self.header_label.setText("<b>Alternate clock designs are located in the View Menu</b>")
            self.menu_picture = QtGui.QPixmap('icons/clock_menu.png')
            self.menu_picture = self.menu_picture.scaledToWidth(self.pic_width)
            self.picture_label.setPixmap(self.menu_picture)
        elif self.pic_cycle == 1:
            self.header_label.setText("<b>Alternate keyboard layouts are also located in the View Menu</b>")
            self.menu_picture = QtGui .QPixmap('icons/layout_menu.png')
            self.menu_picture = self.menu_picture.scaledToWidth(self.pic_width)
            self.picture_label.setPixmap(self.menu_picture)
        elif self.pic_cycle == 2:
            self.header_label.setText("<b>A profanity filter and retrain option are available in the Tools Menu</b>")
            self.menu_picture = QtGui .QPixmap('icons/tools_menu.png')
            self.menu_picture = self.menu_picture.scaledToWidth(self.pic_width)
            self.picture_label.setPixmap(self.menu_picture)

        self.picture_timer.start(4000)


class PretrainScreen1(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PretrainScreen1, self).__init__(parent)
        self.size_factor = 1
        self.high_contrast = False
        self.alignment = 'cr'
        self.color_index = 0
        self.in_focus = True
        self.parent = parent
        self.header_label = QtWidgets.QLabel("<b>You're almost ready to start using Nomon!</b>")
        self.sub_label_1 = QtWidgets.QLabel(
            "<b>>></b>Before we begin, we need some information about your pressing accuracy "
            "so that we can better predict your selections.")
        self.sub_label_2 = QtWidgets.QLabel(
            "<b>>></b>A grid of clocks will appear on the next screen, please press when "
            "the <span style='color:#00aa00;'>GREEN CLOCK</span> reaches Noon in each round.")
        self.sub_label_3 = QtWidgets.QLabel("<i>(press to continue)</i>")

        self.header_label.setFont(config.welcome_main_font[self.parent.font_scale])
        self.header_label.setWordWrap(True)
        self.sub_label_1.setFont(config.welcome_sub_font[self.parent.font_scale])
        self.sub_label_1.setWordWrap(True)
        self.sub_label_2.setFont(config.welcome_sub_font[self.parent.font_scale])
        self.sub_label_2.setWordWrap(True)
        self.sub_label_3.setFont(config.welcome_sub_font[self.parent.font_scale])

        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.header_label, 0, 0, 1, 10)
        grid.addWidget(self.sub_label_1, 1, 1, 1, 8)
        grid.addWidget(self.sub_label_2, 3, 1, 1, 8)
        grid.addWidget(self.sub_label_3, 5, 8, 1, 2)
        grid.setRowStretch(2, 1)
        grid.setRowStretch(4, 3)
        self.setLayout(grid)


# noinspection PyUnresolvedReferences
class PretrainScreen(QtWidgets.QWidget):

    def __init__(self, parent):
        super(PretrainScreen, self).__init__()
        self.parent = parent
        self.screen_res = self.parent.screen_res
        self.size_factor = min(self.screen_res) / 1080.
        self.alignment = 'cr'
        self.start_pretrain = False
        self.color_index = self.parent.high_contrast
        self.highlight_clock = False
        self.init_ui()

    def init_ui(self):

        vbox = QtWidgets.QVBoxLayout()

        self.key_grid = QtWidgets.QGridLayout()

        self.clock = OldClockWidget('', self)
        self.clock.highlighted = True

        self.generate_dummy_clocks()
        self.layout_clocks()

        self.main_label = QtWidgets.QLabel("Please press when the moving hand on the <span style='color:#00aa00;'>"
                                       "GREEN CLOCK</span> reaches Noon <b>" + str(
            self.parent.total_presses) + "</b> more"
                                         " times...")
        self.sub_label_1 = QtWidgets.QLabel("<i>(or press to continue)</i>")
        self.main_label.setFont(config.welcome_main_font[self.parent.font_scale])
        self.main_label.setWordWrap(True)
        self.sub_label_1.setFont(config.welcome_sub_font[self.parent.font_scale])

        self.start_button = QtWidgets.QPushButton("Start Training!")
        self.start_button.pressed.connect(self.start_buttton_func)

        vbox.addWidget(self.main_label, 1)
        vbox.addStretch(1)
        vbox.addLayout(self.keyboard_grid, 20)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.start_button, 1)
        hbox.addStretch(1)

        vbox.addLayout(hbox, 1)
        vbox.addStretch(2)
        vbox.addWidget(self.sub_label_1, 1, QtCore.Qt.AlignRight)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def generate_dummy_clocks(self):
        self.dummy_clocks = [ClockWidget("", self) for i in range(80)]

    def layout_clocks(self):

        def make_grid_unit(main_clock, sub_clocks=None):
            key_grid = QtWidgets.QGridLayout()
            key_grid.addWidget(VerticalSeparator(), 0, 0, 5, 1)
            key_grid.addWidget(VerticalSeparator(), 0, 3, 5, 1)
            key_grid.addWidget(HorizontalSeparator(), 0, 0, 1, 4)
            key_grid.addWidget(HorizontalSeparator(), 4, 0, 1, 4)
            key_grid.addWidget(main_clock, 1, 1, 3, 1)
            clock_index = 0
            for sub_clock in sub_clocks:
                key_grid.addWidget(sub_clock, 1 + clock_index, 2)
                key_grid.setRowStretch(1 + clock_index, 2)
                clock_index += 1
            key_grid.setColumnStretch(1, 4)
            key_grid.setColumnStretch(2, 3)
            return key_grid

        self.keyboard_grid = QtWidgets.QGridLayout()

        self.grid_units = [make_grid_unit(self.dummy_clocks[4*i], self.dummy_clocks[4*i + 1:4*i + 4]) for i in
                           range(len(self.dummy_clocks) // 4)]
        self.layout_from_target(kconfig.pretrain_target_layout)

    def layout_from_target(self, target_layout):
        row_num = 0
        for row in target_layout:
            col_num = 0
            for key in row:
                self.keyboard_grid.addLayout(self.grid_units[key], row_num, col_num)
                col_num += 1
            self.keyboard_grid.setRowStretch(row_num, 2)
            self.keyboard_grid.setRowStretch(col_num, 2)
            row_num += 1

    def highlight(self):
        if time.time()-self.start_time < .500:
            self.dummy_clocks[self.parent.pbc.clock_inf.pre_clock_util.selected_clock].background = True
        else:
            self.dummy_clocks[self.parent.pbc.clock_inf.pre_clock_util.selected_clock].background = False
            self.highlight_clock = False

    def start_buttton_func(self):
        if self.parent.num_presses >= self.parent.total_presses:
            self.parent.on_finish()
        else:
            self.parent.on_start()


class Pretraining(StartWindow):

    def __init__(self, sister, screen_res, help_screen=False):
        super(Pretraining, self).__init__(screen_res, help_screen)
        """

        :param screen_res: screen resolution from QApplication
        :param sister: An instance of SimulatedUser() that represents the main window
        """
        self.sister = sister
        self.sister.pretrain = True
        self.pretrain_window = True
        self.saved_data = False
        self.is_simulation = self.sister.is_simulation

        self.clock_type, self.font_scale, self.high_contrast, self.layout_preference, self.pf_preference, \
            self.start_speed, self.is_write_data = self.sister.up_handel.safe_load()

        self.num_presses = 0
        self.total_presses = 10

        # just for initialization
        self.pbc = None
        self.mainWidget = PretrainScreen(self)
        self.mainWidget.init_ui()
        self.radius = self.mainWidget.clock.radius
        self.time_rotate = self.sister.time_rotate

        self.pbc = PreBroderClocks(self)
        #
        self.in_pause = False
        self.deactivate_press = False
        # whether training has actually started
        self.started = 0
        self.training_ended = 0
        self.consent = True
        self.retrain = False

        self.clock_params = zeros((80, 8))
        self.clock_spaces = zeros((80, 2))

        self.sister.update()
        self.show()


    def re_init(self):
        """

        :return: None
        """
        self.sister.pretrain = True
        self.setGeometry(self.screen_res[0] * 0.05, self.screen_res[1] * 0.0675, self.screen_res[0] * 0.9,
                         self.screen_res[1] * 0.85)

        self.num_presses = 0
        self.total_presses = 10

        # just for initialization
        self.pbc = None
        self.mainWidget.init_ui()
        self.radius = self.mainWidget.clock.radius
        self.time_rotate = self.sister.time_rotate

        self.pbc = PreBroderClocks(self)

        self.in_pause = False
        self.deactivate_press = False
        # whether training has actually started
        self.started = 0
        self.training_ended = 0
        self.consent = True

        self.pbc.clock_inf.pre_clock_util.redraw_clocks()
        self.init_clocks()

    def init_clocks(self):
        self.update_clock_radii()

        self.pbc.clock_inf.pre_clock_util.calcualte_clock_params(self.clock_type, recompute=True)
        for clock in range(len(self.mainWidget.dummy_clocks)):
            self.mainWidget.dummy_clocks[clock].calculate_clock_size()
            self.mainWidget.dummy_clocks[clock].set_params(self.clock_params[clock, :], recompute=True)
            self.mainWidget.dummy_clocks[clock].draw = True
            self.mainWidget.dummy_clocks[clock].redraw_text = True

    def update_clock_radii(self):
        for clock in range(len(self.mainWidget.dummy_clocks)):
            self.clock_spaces[clock, :] = array([self.mainWidget.dummy_clocks[clock].w, self.mainWidget.dummy_clocks[clock].h])
        self.pbc.clock_inf.pre_clock_util.calcualte_clock_params(self.clock_type, recompute=True)
        self.update_radii = False

        for clock in range(len(self.mainWidget.dummy_clocks)):
            self.mainWidget.dummy_clocks[clock].redraw_text = True

    def play(self):
        sound_file = "icons/bell.wav"
        QtMultimedia.QSound(sound_file).play()

    def on_press(self):

        if self.started == 1:
            self.num_presses += 1
            self.mainWidget.main_label.setText("Please press when the moving hand on the <span style='color:#00aa00;'>"
                                               "GREEN CLOCK</span> reaches Noon <b>" +
                                               str(self.total_presses - self.num_presses) + "</b> more times...")
            # Log press time
            if (not self.in_pause) and self.deactivate_press == False:
                # if config.is_write_data:
                self.pbc.select()

            if self.num_presses == self.total_presses:
                print("finished calculating density")

                self.pbc.clock_inf.calculate_density()
                self.mainWidget.main_label.setText("Training has finished!")

                self.mainWidget.start_button.setText("Start Nomon")
                self.mainWidget.start_button.setFocus()

                self.mainWidget.start_button.show()
                self.deactivate_press = True

            elif self.num_presses > self.total_presses:
                print("finished calculating density")
                self.mainWidget.main_label.setText("Training has finished!")

                self.mainWidget.start_button.setText("Start Nomon")
                self.mainWidget.start_button.setFocus()

                self.mainWidget.start_button.show()
                self.start_button_func()
                self.deactivate_press = True

        if self.deactivate_press:
            self.on_finish()
        self.on_start()
        self.play()

    def on_start(self):
        self.mainWidget.main_label.setFocus()  # focus on not toggle-able widget to allow keypress event
        if not self.mainWidget.start_pretrain:
            self.mainWidget.start_pretrain = True

        if self.started == 0:
            self.train_timer = QtCore.QTimer()
            self.train_timer.timeout.connect(self.on_timer)
            self.train_timer.start(config.ideal_wait_s * 1000)
            self.started = 1
            self.mainWidget.start_button.hide()
            self.pbc.clock_inf.pre_clock_util.redraw_clocks()

        for clock in self.mainWidget.dummy_clocks:
            clock.redraw_text = True
            clock.calculate_clock_size()
        self.init_clocks()

    def on_timer(self):
        if not (self.in_pause) and not (self.deactivate_press) and self.num_presses < self.total_presses:
            self.pbc.clock_inf.pre_clock_util.increment()

        elif self.num_presses == self.total_presses:

            # print "Training Ended"
            self.deactivate_press = True

    def load_saved_density_keyboard(self):
        self.sister.bc.get_prev_data()

    def resizeEvent(self, event):
        if isinstance(self.mainWidget, PretrainScreen):
            self.init_clocks()
        QtWidgets.QMainWindow.resizeEvent(self, event)

    def save(self):
        if self.consent and self.is_write_data:
            self.pbc.quit_pbc()
        else:
            pass

    def on_finish(self):
        print("quitting")
        self.saved_data = True
        self.training_ended = 1

        if self.retrain == False:
            self.save()
            self.load_saved_density_keyboard()
        elif self.retrain == True and self.pbc.clock_inf.calc_density_called == True:
            self.sister.bc.save_when_quit()

            self.save()
            self.load_saved_density_keyboard()

        else:
                pass

        self.sister.pretrain = False
        self.sister.draw_histogram(bars=None)
        self.sister.mainWidget.histogram.update()
        self.sister.mainWidget.update()

        self.close()

    def closeEvent(self, event):
        if not self.saved_data:
            self.on_finish()
        else:
            self.sister.pretrain = False
        event.accept()
