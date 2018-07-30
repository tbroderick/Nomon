from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QSound
import config
import pickle, time
import pre_broderclocks_pyqt
import string
import broderclocks
from widgets import *
import sys
import random


class StartWindow(QtGui.QMainWindow):

    def __init__(self, screen_res, splash):
        super(StartWindow, self).__init__()
        global loading_text
        loading_text = '****************************\n****************************\n[Loading...]'

        self.screen_res = screen_res

        self.clock_type = pickle.load(open("user_preferences/clock_preference.p", "rb"))
        self.high_contrast = pickle.load(open("user_preferences/high_contrast.p", "rb"))
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
        self.setWindowIcon(QtGui.QIcon('icons/nomon.png'))

        self.show()

    def initUI_welcome(self):
        self.mainWidgit = WelcomeScreen(self)
        self.mainWidgit.initUI1()
        self.setCentralWidget(self.mainWidgit)

        w = 700
        h = 500

        self.setGeometry((self.screen_res[0] - w) / 2, (self.screen_res[1] - h) / 2, w, h)

        self.setWindowTitle('Nomon Keyboard')
        self.setWindowIcon(QtGui.QIcon('icons/nomon.png'))

        self.show()

    def keyPressEvent(self, e):
        if not self.splash:
            if e.key() == QtCore.Qt.Key_Space:
                self.screen_num += 1  # cycle through the multiple welcome/help screens
                if self.screen_num == 1:
                    self.mainWidgit.close()
                    self.mainWidgit = WelcomeScreen(self)
                    self.mainWidgit.initUI2()
                    self.setCentralWidget(self.mainWidgit)
                elif self.screen_num == 2:
                    self.mainWidgit.close()
                    self.mainWidgit = WelcomeScreen(self)
                    self.mainWidgit.initUI3()
                    self.setCentralWidget(self.mainWidgit)
                elif self.screen_num == 3:
                    if self.help_screen:  # if help screen, don't re-train histogram
                        self.close()
                    else:
                        self.mainWidgit.close()
                        self.mainWidgit = WelcomeScreen(self)
                        self.mainWidgit.initUI4()
                        self.setCentralWidget(self.mainWidgit)
                elif self.screen_num == 4:
                    self.mainWidgit.close()
                    self.mainWidgit = PretrainScreen(self)
                    self.mainWidgit.initUI()
                    self.setCentralWidget(self.mainWidgit)
                    self.setGeometry(self.sister.geometry())
                else:

# =============================================================================
#                     if self.num_presses >= self.total_presses:
#                         self.on_finish()
# =============================================================================
                    self.on_press()


class SplashScreen(QtGui.QWidget):

    def __init__(self, parent):
        super(SplashScreen, self).__init__()
        self.parent = parent
        self.screen_res = self.parent.screen_res
        self.size_factor = min(self.screen_res) / 1080.
        self.alignment = 'cr'

        self.initUI()

    def initUI(self):
        vbox = QtGui.QVBoxLayout()

        hbox = QtGui.QHBoxLayout()

        self.loading_clock = ClockWidgit('', self)
        self.loading_clock.highlighted = True
        self.loading_clock.setMinimumSize(200, 200)

        self.quotes_label = QtGui.QLabel(loading_text)
        self.quotes_label.setWordWrap(True)

        loading_label = QtGui.QLabel("LOADING NOMON...")

        self.quotes_label.setFont(splash_font)
        loading_label.setFont(splash_font)

        self.timer = QtCore.QBasicTimer()
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
        if self.step >= math.pi * 2:
            self.parent.close()

        self.step += math.pi / 7 * 2
        self.loading_clock.angle = self.step
        self.quotes_label.setText(loading_text)
        self.loading_clock.repaint()


class WelcomeScreen(QtGui.QWidget):

    def __init__(self, parent):
        super(WelcomeScreen, self).__init__()
        self.parent = parent
        self.screen_res = self.parent.screen_res
        self.size_factor = min(self.screen_res) / 1080.
        self.alignment = 'cr'

    def initUI1(self):
        vbox = QtGui.QVBoxLayout()

        hbox = QtGui.QHBoxLayout()

        self.loading_clock = ClockWidgit('a', self)
        self.loading_clock.highlighted = True
        self.loading_clock.setMinimumSize(200, 200)
        self.sub_label_1 = QtGui.QLabel("To select an option, find the adjacent clock and press when the moving hand "
                                        "is near Noon.")
        self.sub_label_2 = QtGui.QLabel("<i>(press to continue)</i>")

        self.sub_label_1.setWordWrap(True)
        loading_label = QtGui.QLabel("<b>Welcome to the Nomon Keyboard!</b>")
        loading_label.setFont(welcome_main_font)

        self.sub_label_1.setFont(welcome_sub_font)
        self.sub_label_2.setFont(welcome_sub_font)
        self.timer = QtCore.QBasicTimer()
        self.timer.start(30, self)
        self.step = 0

        hbox.addStretch(1)
        hbox.addWidget(self.loading_clock, 2)
        hbox.addStretch(1)
        vbox.addWidget(loading_label)
        vbox.addLayout(hbox)
        vbox.addStretch(1)
        vbox.addWidget(self.sub_label_1, 1)
        vbox.addWidget(self.sub_label_2, 1, QtCore.Qt.AlignRight)

        self.setLayout(vbox)

    def initUI2(self):
        self.header_label = QtGui.QLabel("<b>There are 2 types of clocks..</b>")
        self.sub_label_1 = QtGui.QLabel("<b>Highlighted</b>")
        self.sub_label_2 = QtGui.QLabel("<b>Regular</b>")
        self.sub_label_3 = QtGui.QLabel("<b>&</b>")
        self.sub_label_4 = QtGui.QLabel("<i>(press to continue)</i>")

        self.header_label.setFont(welcome_main_font)
        self.sub_label_1.setFont(welcome_main_font)
        self.sub_label_2.setFont(welcome_main_font)
        self.sub_label_3.setFont(welcome_main_font)

        self.highlighted_clock = ClockWidgit('', self)
        self.highlighted_clock.highlighted = True
        self.highlighted_clock.angle = 1
        self.highlighted_clock.setMinimumSize(150, 150)

        self.regular_clock = ClockWidgit('', self)
        self.regular_clock.angle = 1
        self.regular_clock.setMinimumSize(150, 150)

        self.main_text_label = QtGui.QLabel(
            "Nomon believes <b>highlighted clocks</b> have a higher probability of being "
            "selected next--so they take <b>fewer presses</b> to select. If you wish to "
            "select a <b>regular clock</b>, then you should press as <b>accurately</b> as "
            "possible!")

        self.main_text_label.setFont(welcome_sub_font)
        self.main_text_label.setWordWrap(True)
        self.sub_label_4.setFont(welcome_sub_font)

        grid = QtGui.QGridLayout()
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

    def initUI3(self):
        self.header_label = QtGui.QLabel("<b>Alternate Clock designs are located in the View Menu</b>")

        self.header_label.setFont(welcome_main_font)
        self.header_label.setWordWrap(True)

        self.picture_timer = QtCore.QTimer()
        self.picture_timer.start(4000)
        self.picture_timer.timeout.connect(self.change_picture)
        self.picture_label = QtGui.QLabel()
        self.menu_picture = QtGui.QPixmap('icons/clock_menu.png')
        self.pic_width = self.geometry().width()
        self.pic_cycle = 0
        self.menu_picture = self.menu_picture.scaledToWidth(self.pic_width)

        self.picture_label.setPixmap(self.menu_picture)

        vbox = QtGui.QVBoxLayout()
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
            self.menu_picture = QtGui.QPixmap('icons/layout_menu.png')
            self.menu_picture = self.menu_picture.scaledToWidth(self.pic_width)
            self.picture_label.setPixmap(self.menu_picture)
        elif self.pic_cycle == 2:
            self.header_label.setText("<b>A profanity filter and retrain option are available in the Tools Menu</b>")
            self.menu_picture = QtGui.QPixmap('icons/tools_menu.png')
            self.menu_picture = self.menu_picture.scaledToWidth(self.pic_width)
            self.picture_label.setPixmap(self.menu_picture)

        self.picture_timer.start(4000)

    def initUI4(self):
        self.header_label = QtGui.QLabel("<b>You're almost ready to start using Nomon!</b>")
        self.sub_label_1 = QtGui.QLabel(
            "<b>>></b>Before we begin, we need some information about your pressing accuracy "
            "so that we can better predict your selections.")
        self.sub_label_2 = QtGui.QLabel("<b>>></b>A grid of clocks will appear on the next screen, please press when "
                                        "the <span style='color:#00aa00;'>GREEN CLOCK</span> reaches Noon in each round.")
        self.sub_label_3 = QtGui.QLabel("<i>(press to continue)</i>")

        self.header_label.setFont(welcome_main_font)
        self.header_label.setWordWrap(True)
        self.sub_label_1.setFont(welcome_sub_font)
        self.sub_label_1.setWordWrap(True)
        self.sub_label_2.setFont(welcome_sub_font)
        self.sub_label_2.setWordWrap(True)
        self.sub_label_3.setFont(welcome_sub_font)

        grid = QtGui.QGridLayout()
        grid.addWidget(self.header_label, 0, 0, 1, 10)
        grid.addWidget(self.sub_label_1, 1, 1, 1, 9)
        grid.addWidget(self.sub_label_2, 3, 1, 1, 9)
        grid.addWidget(self.sub_label_3, 5, 8, 1, 2)
        grid.setRowStretch(2, 1)
        grid.setRowStretch(4, 3)
        self.setLayout(grid)

    def timerEvent(self, e):  # timer to redraw clock for animation
        self.step += math.pi / 32

        if self.step >= math.pi * 2:
            self.step = -math.pi
            self.loading_clock.angle = 0
            self.loading_clock.repaint()

        if self.step > 0:
            self.loading_clock.angle = self.step
            self.loading_clock.repaint()


class PretrainScreen(QtGui.QWidget):

    def __init__(self, parent):
        super(PretrainScreen, self).__init__()
        self.parent = parent
        self.screen_res = self.parent.screen_res
        self.size_factor = min(self.screen_res) / 1080.
        self.alignment = 'cr'
        self.start_pretrain = False


    def initUI(self):

        vbox = QtGui.QVBoxLayout()

        self.key_grid = QtGui.QGridLayout()

        self.clock = ClockWidgit('', self)
        self.clock.highlighted = True

        self.generateDummyClocks()
        self.layoutClocks()

        self.main_label= QtGui.QLabel("Please press when the moving hand on the <span style='color:#00aa00;'>"
                                      "GREEN CLOCK</span> reaches Noon <b>"+str(self.parent.total_presses)+"</b> more"
                                                                                                           " times...")
        self.sub_label_1 = QtGui.QLabel("<i>(or press to continue)</i>")
        self.main_label.setFont(welcome_main_font)
        self.main_label.setWordWrap(True)
        self.sub_label_1.setFont(welcome_sub_font)

        self.start_button = QtGui.QPushButton("Start Training!")
        self.start_button.pressed.connect(self.start_buttton_func)

        # self.speed_slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        # self.speed_slider.setRange(config.scale_min, config.scale_max)
        # self.speed_slider.setValue(config.start_speed)
        # self.speed_slider.valueChanged[int].connect(self.changeValue)

        vbox.addWidget(self.main_label, 1)
        vbox.addStretch(1)
        vbox.addLayout(self.key_grid)
        vbox.addStretch(3)

        hbox=QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.start_button, 1)
        hbox.addStretch(1)

        vbox.addLayout(hbox, 1)
        vbox.addStretch(2)
        vbox.addWidget(self.sub_label_1, 1, QtCore.Qt.AlignRight)
        vbox.addStretch(1)

        self.setLayout(vbox)

    # def changeValue(self, value):  # Change clock speed
    #     speed_index = int(value)
    #     self.parent.sister.mainWidgit.speed_slider.setValue(value)
    #     pickle.dump(speed_index, open("user_preferences/start_speed.p", 'wb'))
    #     # period (as stored in config.py)
    #     self.parent.rotate_index = config.scale_max - speed_index + 1
    #     self.parent.time_rotate = config.period_li[self.parent.rotate_index]
    #     self.parent.pbc = pre_broderclocks_pyqt.Pre_broderclocks(self.parent, self.parent.file_handle, self.parent.time_rotate, self.parent.use_num, self.parent.user_id, time.time(), self.parent.prev_data)
    #     self.parent.wait_s = self.parent.pbc.get_wait()
    #     self.parent.num_stop_training = self.parent.pbc.hsi.n_training

    def generateDummyClocks(self):
        self.dummy_clocks = [ClockWidgit("not me", self) for i in range(64)]
        self.redrawClocks()

    def layoutClocks(self):
        index = 0
        for row in range(4):
            self.key_grid.addWidget(HorizontalSeparator(), row * 4, 0, 1, 13)
            for col in range(4):
                for sub_index in range(4):
                    if sub_index == 0:
                        self.key_grid.addWidget(VerticalSeparator(), row * 4, col * 3, 5, 1)
                        self.key_grid.addWidget(self.dummy_clocks[index], row * 4 + 1, col * 3 + 1, 3, 1)
                        index += 1
                    else:
                        self.key_grid.addWidget(self.dummy_clocks[index], row * 4 + sub_index, col * 3 + 2)
                        index += 1
                if col == 3:
                    self.key_grid.addWidget(VerticalSeparator(), row * 4, col * 4, 5, 1)
        self.key_grid.addWidget(HorizontalSeparator(), row * 5+1, 0, 1, 13)

    def redrawClocks(self):
        for clock in self.dummy_clocks:
            clock.text = "not me"
            clock.selected = False
            clock.highlighted = (random.random() < random.random())
            clock.dummy_angle_offset = random.random() * math.pi*-1
            angle = self.clock.angle + clock.dummy_angle_offset
            clock.angle = angle
            clock.repaint()
        selected_clock = random.randint(0, 63)
        self.dummy_clocks[selected_clock].dummy_angle_offset = 0
        self.dummy_clocks[selected_clock].selected = True
        self.dummy_clocks[selected_clock].text = "Click Me!"
        self.dummy_clocks[selected_clock].repaint()


    def start_buttton_func(self):
        if self.parent.num_presses >= self.parent.total_presses:
            self.parent.on_finish()
        else:
            self.parent.on_start()


class Pretraining(StartWindow):

    def __init__(self, screen_res, sister):
        super(Pretraining, self).__init__(screen_res, False)
        self.training_ended = 0
        self.num_presses = 0
        self.sister = sister
        self.sister.pretrain = True

        #Used to be in keyboard_pre.py
        if len(sys.argv) < 3:
             self.user_id = 0
             self.use_num = 0
            # read arguments
        else:
            user_id = string.atoi(sys.argv[1])
            use_num = string.atoi(sys.argv[2])
            self.user_id = user_id
            self.use_num = use_num
        
        
        self.in_pause = False
        self.time_rotate = self.sister.time_rotate
        
        
        self.prev_data = None
        self.num_presses = 0
        
        
        
        if config.is_write_data:
            print "yeah writing data!"
            self.gen_handle()
            self.num_presses = 0

        else:
            self.file_handle = None
        
        #which is 20
        #self.total_presses = self.pbc.hsi.n_training
        self.num_stop_training = 10
        self.total_presses = 10
        
        self.mainWidgit = PretrainScreen(self)
        self.mainWidgit.initUI()
        self.radius = self.mainWidgit.clock.radius
        
        self.pbc = pre_broderclocks_pyqt.Pre_broderclocks(self, self.file_handle, self.time_rotate, self.use_num, self.user_id, time.time(), self.prev_data)
        self.wait_s = self.pbc.get_wait()
        
        
        #self.pbc.hsi.n_training #which is 20
        self.deactivate_press = False
        #whether training has actually started
        self.started = 0

    def gen_handle(self):
        data_file = "data/preconfig.pickle"
        self.file_handle = data_file
        
    
# =============================================================================
#     def keyPressEventRedef(self, e):
#         if e.key() == QtCore.Qt.Key_Space:
#             self.on_press()
#         self.play()
# =============================================================================
    
    def play(self):
        sound_file = "icons/bell.wav"
        QSound(sound_file).play()
    
    def on_press(self):

        if self.started == 1:
            self.num_presses += 1
            self.mainWidgit.main_label.setText("Please press when the moving hand on the <span style='color:#00aa00;'>"
                                               "GREEN CLOCK</span> reaches Noon <b>" +
                                               str(self.total_presses - self.num_presses) + "</b> more times...")
            #Log press time
            if (not self.in_pause) and self.deactivate_press == False:
                #if config.is_write_data:
                self.pbc.select(time.time())
                self.mainWidgit.redrawClocks()


            if self.num_presses >= self.total_presses:
                print "finished calculating density"

                self.pbc.hsi.calculate_density()
                self.mainWidgit.main_label.setText("Training has finished!")

                self.mainWidgit.start_button.setText("Start Nomon")
                self.mainWidgit.start_button.setFocus()

                self.mainWidgit.start_button.show()
            
        if self.deactivate_press:
            self.on_finish()
        self.on_start()
        self.play()

    def on_increment(self, angle):
        self.mainWidgit.clock.angle = angle
        self.mainWidgit.clock.repaint()

    def on_start(self):
        self.mainWidgit.main_label.setFocus()  # focus on not toggle-able widget to allow keypress event
        if not self.mainWidgit.start_pretrain:
            self.mainWidgit.start_pretrain = True
     
        if self.started == 0:
            #self.start_text.setText("Click when the hour hand hits the red noon hand! \n clicks remaining = " + str(self.total_presses - self.num_presses) )
            #self.start_button.hide()
            self.train_timer = QtCore.QTimer()
            self.train_timer.timeout.connect(self.on_timer)
            self.train_timer.start(config.ideal_wait_s*1000)
            self.started = 1
            self.mainWidgit.start_button.hide()
            
    def on_timer(self):
        if not self.in_pause and self.num_presses < self.total_presses:
            #self.setFocus()
            start_t = time.time()
            self.pbc.increment(start_t)
            #self.start_text.setText("Click when the hour hand hits the red noon hand! \n clicks remaining = " + str(self.num_stop_training - self.num_presses))
            #self.mainWidgit.clock.angle = 
            #self.mainWidgit.clock.repaint()
        
        elif self.num_presses == self.total_presses:

            #print "Training Ended"
            self.deactivate_press = True

    def on_finish(self):
        print "quitting"
        self.training_ended = 1
        self.prev_data = self.sister.bc.prev_data
        self.use_num = self.sister.bc.use_num
        if config.is_write_data:
            try:
                li = self.pbc.hsi.dens_li
                print "The length of li is" + str(len(li))
                z = self.pbc.hsi.Z
                pickle.dump([li, z, self.pbc.hsi.opt_sig, self.pbc.hsi.y_li], open(self.file_handle, 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

                self.prev_data = [[self.pbc.hsi.y_li[0]], [self.pbc.hsi.opt_sig]]
                self.use_num = 1

                print "I'm quitting and the density is" + str(li)
                print "And the Z is " + str(z)
                print "file closed"
            except IOError as (errno,strerror):
                print "I/O error({0}): {1}".format(errno, strerror)
        
        print "this worked"
        self.sister.bc.hsi.not_read_pickle = 0
        #self.sister.bc.hsi.update_dens(self.sister.bc.hsi.time_rotate)
        use_num, user_id, time_rotate, prev_data = self.use_num, self.sister.bc.user_id, self.sister.bc.time_rotate, self.prev_data
        self.sister.bc.hsi = broderclocks.HourScoreIncs(use_num, user_id, time_rotate, prev_data)
        #print "is not read pickle 1? should be " + str(self.sister.bc.hsi.not_read_pickle) 
        #self.sister.bc = 
        print "this worked 1"
        self.sister.draw_histogram(bars=None)
        #self.sister.bars = self.sister.bc.hsi.dens_li
        self.sister.mainWidgit.histogram.repaint()
        #self.sister.init_histogram()
        print "this worked 2"
        #print self.sister.bc.hsi.not_read_pickle
        self.sister.pretrain_bars = list(self.sister.bars)
        self.close()

    def closeEvent(self, event):
        self.sister.pretrain = False
        event.accept()


def main():
    app = QtGui.QApplication(sys.argv)
    screen_res = (app.desktop().screenGeometry().width(), app.desktop().screenGeometry().height())
    welcome = Pretraining(screen_res)
    app.processEvents()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
