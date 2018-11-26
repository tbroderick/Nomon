from PyQt4.QtCore import Qt, QBasicTimer, QTimer
from PyQt4.QtGui import QMainWindow, QWidget, QIcon, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPixmap, QSound, \
    QPushButton

from widgets import ClockWidgit, OldClockWidgit, VerticalSeparator, HorizontalSeparator
from pretraininginference import PreBroderClocks

import sys
import os
from numpy import pi, zeros, array
import time
import config
import kconfig
from pickle_util import PickleUtil

sys.path.insert(0, os.path.realpath('../KernelDensityEstimation'))


class StartWindow(QMainWindow):

    def __init__(self, screen_res, splash):
        super(StartWindow, self).__init__()
        global loading_text
        loading_text = '****************************\n****************************\n[Loading...]'

        self.screen_res = screen_res

        # self.clock_type = PickleUtil("user_preferences/clock_preference.p").safe_load()
        # self.high_contrast = PickleUtil("user_preferences/high_contrast.p").safe_load()

        self.clock_type, self.font_scale, self.high_contrast, self.layout_preference, self.pf_preference, self.start_speed, self.is_write_data = ['default', 1, False, 'alpha', 'off', 12, True]

        self.splash = splash
        self.help_screen = False  # if triggered under help menu adjust number of follow up screens
        self.screen_num = 0  # start at first screen if welcome screen

        if self.splash:  # display splash screen if triggered
            self.initUI_splash()
        else:
            self.initUI_welcome()

    def initUI_splash(self):
        self.mainWidgit = SplashScreen(self)
        self.setCentralWidget(self.mainWidgit)

        w = 700
        h = 500

        self.setGeometry((self.screen_res[0] - w) / 2, (self.screen_res[1] - h) / 2, w, h)
        self.setWindowTitle('Nomon Keyboard')
        self.setWindowIcon(QIcon('icons/nomon.png'))

        self.show()

    def initUI_welcome(self):
        self.mainWidgit = WelcomeScreen(self)
        self.mainWidgit.init_ui1()
        self.setCentralWidget(self.mainWidgit)

        w = 700
        h = 500

        self.setGeometry((self.screen_res[0] - w) / 2, (self.screen_res[1] - h) / 2, w, h)

        self.setWindowTitle('Nomon Keyboard')
        self.setWindowIcon(QIcon('icons/nomon.png'))

        self.show()

    def keyPressEvent(self, e):
        if not self.splash:
            if e.key() == Qt.Key_Space:
                self.screen_num += 1  # cycle through the multiple welcome/help screens
                if self.screen_num == 1:
                    self.mainWidgit.close()
                    self.mainWidgit = WelcomeScreen(self)
                    self.mainWidgit.init_ui2()
                    self.setCentralWidget(self.mainWidgit)
                elif self.screen_num == 2:
                    self.mainWidgit.close()
                    self.mainWidgit = WelcomeScreen(self)
                    self.mainWidgit.init_ui3()
                    self.setCentralWidget(self.mainWidgit)
                elif self.screen_num == 3:
                    if self.help_screen:  # if help screen, don't re-train histogram
                        self.close()
                    else:
                        self.mainWidgit.close()
                        self.mainWidgit = WelcomeScreen(self)
                        self.mainWidgit.init_ui4()
                        self.setCentralWidget(self.mainWidgit)
                # I think here
                elif self.screen_num == 4:
                    self.mainWidgit.close()
                    self.re_init()
                    # self.mainWidgit = PretrainScreen(self)
                    # self.mainWidgit.init_ui()
                    # self.pbc = PreBroderClocks(self)
                    self.setCentralWidget(self.mainWidgit)
                    self.setGeometry(self.sister.geometry())
                else:

                    # =============================================================================
                    #                     if self.num_presses >= self.total_presses:
                    #                         self.on_finish()
                    # =============================================================================
                    self.on_press()


class SplashScreen(QWidget):

    def __init__(self, parent):
        super(SplashScreen, self).__init__()
        self.parent = parent
        self.screen_res = self.parent.screen_res
        self.size_factor = min(self.screen_res) / 1080.
        self.alignment = 'cr'
        self.color_index = self.parent.high_contrast

        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()

        hbox = QHBoxLayout()

        self.loading_clock = OldClockWidgit('', self)
        self.loading_clock.highlighted = True
        self.loading_clock.setMinimumSize(200, 200)

        self.quotes_label = QLabel(loading_text)
        self.quotes_label.setWordWrap(True)

        loading_label = QLabel("LOADING NOMON...")

        self.quotes_label.setFont(config.splash_font[self.parent.font_scale])
        loading_label.setFont(config.splash_font[self.parent.font_scale])

        self.timer = QBasicTimer()
        self.timer.start(100, self)
        self.step = 0

        hbox.addStretch(1)
        hbox.addWidget(self.loading_clock)
        hbox.addStretch(1)
        vbox.addWidget(loading_label)
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        vbox.addWidget(self.quotes_label, 1)

        self.setLayout(vbox)

    def timerEvent(self, e):
        if self.step >= pi * 2:
            self.parent.close()

        self.step += pi / 7 * 2
        self.loading_clock.angle = self.step
        self.quotes_label.setText(loading_text)
        self.loading_clock.update()


class WelcomeScreen(QWidget):

    def __init__(self, parent):
        super(WelcomeScreen, self).__init__()
        self.parent = parent
        self.screen_res = self.parent.screen_res
        self.size_factor = min(self.screen_res) / 1080.
        self.alignment = 'cr'
        self.color_index = self.parent.high_contrast

    def init_ui1(self):
        vbox = QVBoxLayout()

        hbox = QHBoxLayout()

        self.loading_clock = OldClockWidgit('a', self)
        self.loading_clock.highlighted = True
        self.loading_clock.setMinimumSize(200, 200)
        self.sub_label_1 = QLabel("To select an option, find the adjacent clock and press when the moving hand "
                                        "is near Noon.")
        self.sub_label_2 = QLabel("<i>(press to continue)</i>")

        self.sub_label_1.setWordWrap(True)
        loading_label = QLabel("<b>Welcome to the Nomon Keyboard!</b>")
        loading_label.setFont(config.welcome_main_font[self.parent.font_scale])

        self.sub_label_1.setFont(config.welcome_sub_font[self.parent.font_scale])
        self.sub_label_2.setFont(config.welcome_sub_font[self.parent.font_scale])
        self.timer = QBasicTimer()
        self.timer.start(30, self)
        self.step = 0

        hbox.addStretch(1)
        hbox.addWidget(self.loading_clock, 2)
        hbox.addStretch(1)
        vbox.addWidget(loading_label)
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        vbox.addWidget(self.sub_label_1, 1)
        vbox.addWidget(self.sub_label_2, 1, Qt.AlignRight)

        self.setLayout(vbox)

    def init_ui2(self):
        self.header_label = QLabel("<b>There are 2 types of clocks..</b>")
        self.sub_label_1 = QLabel("<b>Highlighted</b>")
        self.sub_label_2 = QLabel("<b>Regular</b>")
        self.sub_label_3 = QLabel("<b>&</b>")
        self.sub_label_4 = QLabel("<i>(press to continue)</i>")

        self.header_label.setFont(config.welcome_main_font[self.parent.font_scale])
        self.sub_label_1.setFont(config.welcome_main_font[self.parent.font_scale])
        self.sub_label_2.setFont(config.welcome_main_font[self.parent.font_scale])
        self.sub_label_3.setFont(config.welcome_main_font[self.parent.font_scale])

        self.highlighted_clock = OldClockWidgit('', self)
        self.highlighted_clock.highlighted = True
        self.highlighted_clock.angle = 1
        self.highlighted_clock.setMinimumSize(150, 150)

        self.regular_clock = OldClockWidgit('', self)
        self.regular_clock.angle = 1
        self.regular_clock.setMinimumSize(150, 150)

        self.main_text_label = QLabel(
            "Nomon believes <b>highlighted clocks</b> have a higher probability of being "
            "selected next--so they take <b>fewer presses</b> to select. If you wish to "
            "select a <b>regular clock</b>, then you should press as <b>accurately</b> as "
            "possible!")

        self.main_text_label.setFont(config.welcome_sub_font[self.parent.font_scale])
        self.main_text_label.setWordWrap(True)
        self.sub_label_4.setFont(config.welcome_sub_font[self.parent.font_scale])

        grid = QGridLayout()
        grid.addWidget(self.header_label, 0, 0, 1, 5)

        grid.addWidget(self.highlighted_clock, 1, 1)
        grid.addWidget(self.sub_label_3, 1, 2, Qt.AlignHCenter | Qt.AlignBottom)
        grid.addWidget(self.regular_clock, 1, 3, Qt.AlignHCenter)

        grid.addWidget(self.sub_label_1, 2, 1, Qt.AlignHCenter | Qt.AlignBottom)
        grid.addWidget(self.sub_label_2, 2, 3, Qt.AlignHCenter | Qt.AlignBottom)

        grid.addWidget(self.main_text_label, 3, 0, 1, 5)
        grid.addWidget(self.sub_label_4, 4, 3, 1, 2)
        grid.setRowStretch(2, 1)
        grid.setRowStretch(3, 1)
        self.setLayout(grid)

    def init_ui3(self):
        self.header_label = QLabel("<b>Alternate Clock designs are located in the View Menu</b>")

        self.header_label.setFont(config.welcome_main_font[self.parent.font_scale])
        self.header_label.setWordWrap(True)

        self.picture_timer = QTimer()
        self.picture_timer.start(4000)
        self.picture_timer.timeout.connect(self.change_picture)
        self.picture_label = QLabel()
        self.menu_picture = QPixmap('icons/clock_menu.png')
        self.pic_width = self.geometry().width()
        self.pic_cycle = 0
        self.menu_picture = self.menu_picture.scaledToWidth(self.pic_width)

        self.picture_label.setPixmap(self.menu_picture)

        vbox = QVBoxLayout()
        vbox.addWidget(self.header_label, 1)
        vbox.addWidget(self.picture_label, 10)
        self.setLayout(vbox)

    def change_picture(self):
        self.pic_cycle += 1
        if self.pic_cycle > 2:
            self.pic_cycle = 0
        if self.pic_cycle == 0:
            self.header_label.setText("<b>Alternate clock designs are located in the View Menu</b>")
            self.menu_picture = QPixmap('icons/clock_menu.png')
            self.menu_picture = self.menu_picture.scaledToWidth(self.pic_width)
            self.picture_label.setPixmap(self.menu_picture)
        elif self.pic_cycle == 1:
            self.header_label.setText("<b>Alternate keyboard layouts are also located in the View Menu</b>")
            self.menu_picture = QPixmap('icons/layout_menu.png')
            self.menu_picture = self.menu_picture.scaledToWidth(self.pic_width)
            self.picture_label.setPixmap(self.menu_picture)
        elif self.pic_cycle == 2:
            self.header_label.setText("<b>A profanity filter and retrain option are available in the Tools Menu</b>")
            self.menu_picture = QPixmap('icons/tools_menu.png')
            self.menu_picture = self.menu_picture.scaledToWidth(self.pic_width)
            self.picture_label.setPixmap(self.menu_picture)

        self.picture_timer.start(4000)

    def init_ui4(self):
        self.header_label = QLabel("<b>You're almost ready to start using Nomon!</b>")
        self.sub_label_1 = QLabel(
            "<b>>></b>Before we begin, we need some information about your pressing accuracy "
            "so that we can better predict your selections.")
        self.sub_label_2 = QLabel("<b>>></b>A grid of clocks will appear on the next screen, please press when "
                                        "the <span style='color:#00aa00;'>GREEN CLOCK</span> reaches Noon in each round.")
        self.sub_label_3 = QLabel("<i>(press to continue)</i>")

        self.header_label.setFont(config.welcome_main_font[self.parent.font_scale])
        self.header_label.setWordWrap(True)
        self.sub_label_1.setFont(config.welcome_sub_font[self.parent.font_scale])
        self.sub_label_1.setWordWrap(True)
        self.sub_label_2.setFont(config.welcome_sub_font[self.parent.font_scale])
        self.sub_label_2.setWordWrap(True)
        self.sub_label_3.setFont(config.welcome_sub_font[self.parent.font_scale])

        grid = QGridLayout()
        grid.addWidget(self.header_label, 0, 0, 1, 10)
        grid.addWidget(self.sub_label_1, 1, 1, 1, 9)
        grid.addWidget(self.sub_label_2, 3, 1, 1, 9)
        grid.addWidget(self.sub_label_3, 5, 8, 1, 2)
        grid.setRowStretch(2, 1)
        grid.setRowStretch(4, 3)
        self.setLayout(grid)

    def timerEvent(self, e):  # timer to redraw clock for animation
        self.step += pi / 32

        if self.step >= pi * 2:
            self.step = -pi
            self.loading_clock.angle = 0
            self.loading_clock.update()

        if self.step > 0:
            self.loading_clock.angle = self.step
            self.loading_clock.update()


# noinspection PyUnresolvedReferences
class PretrainScreen(QWidget):

    def __init__(self, parent):
        super(PretrainScreen, self).__init__()
        self.parent = parent
        self.screen_res = self.parent.screen_res
        self.size_factor = min(self.screen_res) / 1080.
        self.alignment = 'cr'
        self.start_pretrain = False
        self.color_index = self.parent.high_contrast
        self.highlight_clock = False

    def init_ui(self):

        vbox = QVBoxLayout()

        self.key_grid = QGridLayout()

        self.clock = OldClockWidgit('', self)
        self.clock.highlighted = True

        self.generate_dummy_clocks()
        self.layout_clocks()

        self.main_label = QLabel("Please press when the moving hand on the <span style='color:#00aa00;'>"
                                       "GREEN CLOCK</span> reaches Noon <b>" + str(
            self.parent.total_presses) + "</b> more"
                                         " times...")
        self.sub_label_1 = QLabel("<i>(or press to continue)</i>")
        self.main_label.setFont(config.welcome_main_font[self.parent.font_scale])
        self.main_label.setWordWrap(True)
        self.sub_label_1.setFont(config.welcome_sub_font[self.parent.font_scale])

        self.start_button = QPushButton("Start Training!")
        self.start_button.pressed.connect(self.start_buttton_func)

        vbox.addWidget(self.main_label, 1)
        vbox.addStretch(1)
        vbox.addLayout(self.keyboard_grid)
        vbox.addStretch(3)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.start_button, 1)
        hbox.addStretch(1)

        vbox.addLayout(hbox, 1)
        vbox.addStretch(2)
        vbox.addWidget(self.sub_label_1, 1, Qt.AlignRight)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def generate_dummy_clocks(self):
        self.dummy_clocks = [ClockWidgit("a", self) for i in range(80)]

    def layout_clocks(self):
        index = 0
        # for row in range(4):
        #     self.key_grid.addWidget(HorizontalSeparator(), row * 4, 0, 1, 13)
        #     for col in range(4):
        #         for sub_index in range(4):
        #             if sub_index == 0:
        #                 self.key_grid.addWidget(VerticalSeparator(), row * 4, col * 3, 5, 1)
        #                 self.key_grid.addWidget(self.dummy_clocks[index], row * 4 + 1, col * 3 + 1, 3, 1)
        #                 index += 1
        #             else:
        #                 self.key_grid.addWidget(self.dummy_clocks[index], row * 4 + sub_index, col * 3 + 2)
        #                 index += 1
        #         if col == 3:
        #             self.key_grid.addWidget(VerticalSeparator(), row * 4, col * 4, 5, 1)
        # self.key_grid.addWidget(HorizontalSeparator(), row * 5 + 1, 0, 1, 13)

        def make_grid_unit(main_clock, sub_clocks=None):
            key_grid = QGridLayout()
            key_grid.addWidget(VerticalSeparator(), 0, 0, 4, 1)
            key_grid.addWidget(VerticalSeparator(), 0, 3, 4, 1)
            key_grid.addWidget(HorizontalSeparator(), 0, 0, 1, 3)
            key_grid.addWidget(HorizontalSeparator(), 4, 0, 1, 3)
            key_grid.addWidget(main_clock, 1, 1, 3, 1)
            clock_index = 0
            for sub_clock in sub_clocks:
                key_grid.addWidget(sub_clock, 1+clock_index, 2)
                clock_index += 1
            key_grid.setColumnStretch(1, 4)
            key_grid.setColumnStretch(2, 5)
            return key_grid

        self.keyboard_grid = QGridLayout()

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
            self.keyboard_grid.setRowStretch(row_num, 1)
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

    def __init__(self, screen_res, sister):
        super(Pretraining, self).__init__(screen_res, False)
        self.sister = sister
        self.sister.pretrain = True
        self.pretrain_window = True
        self.saved_data = False

        self.clock_type, self.font_scale, self.high_contrast, self.layout_preference, self.pf_preference, \
            self.start_speed, self.is_write_data = self.sister.up_handel.safe_load()

        self.num_presses = 0
        self.total_presses = 10

        # just for initialization
        self.pbc = None
        self.mainWidgit = PretrainScreen(self)
        self.mainWidgit.init_ui()
        self.radius = self.mainWidgit.clock.radius
        self.time_rotate = self.sister.time_rotate

        self.pbc = PreBroderClocks(self)

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


    def re_init(self):
        self.sister.pretrain = True

        self.num_presses = 0
        self.total_presses = 10

        # just for initialization
        self.pbc = None
        self.mainWidgit = PretrainScreen(self)
        self.mainWidgit.init_ui()
        self.radius = self.mainWidgit.clock.radius
        self.time_rotate = self.sister.time_rotate

        self.pbc = PreBroderClocks(self)

        self.in_pause = False
        self.deactivate_press = False
        # whether training has actually started
        self.started = 0
        self.training_ended = 0
        self.consent = True
        self.init_clocks()

    def init_clocks(self):
        self.update_clock_radii()

        self.pbc.clock_inf.pre_clock_util.calcualte_clock_params(self.clock_type, recompute=True)
        for clock in range(len(self.mainWidgit.dummy_clocks)):
            self.mainWidgit.dummy_clocks[clock].calculate_clock_size()
            self.mainWidgit.dummy_clocks[clock].set_params(self.clock_params[clock, :], recompute=True)
            self.mainWidgit.dummy_clocks[clock].draw = True
            self.mainWidgit.dummy_clocks[clock].redraw_text = True

    def update_clock_radii(self):
        for clock in range(len(self.mainWidgit.dummy_clocks)):
            self.clock_spaces[clock, :] = array([self.mainWidgit.dummy_clocks[clock].w, self.mainWidgit.dummy_clocks[clock].h])
        self.pbc.clock_inf.pre_clock_util.calcualte_clock_params(self.clock_type, recompute=True)
        self.update_radii = False

        for clock in range(len(self.mainWidgit.dummy_clocks)):
            self.mainWidgit.dummy_clocks[clock].redraw_text = True

    def play(self):
        sound_file = "icons/bell.wav"
        QSound(sound_file).play()

    def on_press(self):

        if self.started == 1:
            self.num_presses += 1
            self.mainWidgit.main_label.setText("Please press when the moving hand on the <span style='color:#00aa00;'>"
                                               "GREEN CLOCK</span> reaches Noon <b>" +
                                               str(self.total_presses - self.num_presses) + "</b> more times...")
            # Log press time
            if (not self.in_pause) and self.deactivate_press == False:
                # if config.is_write_data:
                self.pbc.select()

            if self.num_presses == self.total_presses:
                print "finished calculating density"

                self.pbc.clock_inf.calculate_density()
                self.mainWidgit.main_label.setText("Training has finished!")

                self.mainWidgit.start_button.setText("Start Nomon")
                self.mainWidgit.start_button.setFocus()

                self.mainWidgit.start_button.show()
                self.deactivate_press = True

            elif self.num_presses > self.total_presses:
                print "finished calculating density"
                self.mainWidgit.main_label.setText("Training has finished!")

                self.mainWidgit.start_button.setText("Start Nomon")
                self.mainWidgit.start_button.setFocus()

                self.mainWidgit.start_button.show()
                self.start_button_func()
                self.deactivate_press = True

        if self.deactivate_press:
            self.on_finish()
        self.on_start()
        self.play()

    def on_start(self):
        self.mainWidgit.main_label.setFocus()  # focus on not toggle-able widget to allow keypress event
        if not self.mainWidgit.start_pretrain:
            self.mainWidgit.start_pretrain = True

        if self.started == 0:
            self.train_timer = QTimer()
            self.train_timer.timeout.connect(self.on_timer)
            self.train_timer.start(config.ideal_wait_s * 1000)
            self.started = 1
            self.mainWidgit.start_button.hide()
        self.init_clocks()

    def on_timer(self):
        if not (self.in_pause) and not (self.deactivate_press) and self.num_presses < self.total_presses:
            self.pbc.clock_inf.pre_clock_util.increment()

        elif self.num_presses == self.total_presses:

            # print "Training Ended"
            self.deactivate_press = True

    def load_saved_density_keyboard(self):
        self.sister.bc.get_prev_data()

    def save(self):
        if self.consent and self.is_write_data:
            self.pbc.quit_pbc()
        else:
            pass

    def on_finish(self):
        print "quitting"
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
        self.sister.mainWidgit.histogram.update()
        self.sister.mainWidgit.update()

        self.close()

    # Is this used at all?
    def closeEvent(self, event):
        if not self.saved_data:
            self.on_finish()
        event.accept()
