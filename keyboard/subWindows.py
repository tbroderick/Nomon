from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QSound
import config
import pickle, time
import pre_broderclocks_pyqt
import string
import broderclocks
from widgets import *
import sys

class StartWindow(QtGui.QMainWindow):

    def __init__(self, screen_res, splash):
        super(StartWindow, self).__init__()
        global loading_text
        loading_text = '****************************\n****************************\n[Loading...]'

        self.screen_res = screen_res

        self.clock_type = 'default'
        self.high_contrast = False
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

        #self.setGeometry((self.screen_res[0] - w) / 2, (self.screen_res[1] - h) / 2, w, h)
        self.setGeometry(self.screen_res[0] * 0.05, self.screen_res[1] * 0.0675, self.screen_res[0] * 0.9,
                         self.screen_res[1] * 0.85)
        self.setWindowTitle('Nomon Keyboard')
        self.setWindowIcon(QtGui.QIcon('icons/nomon.png'))

        self.show()

    def initUI_welcome(self):
        self.mainWidgit = WelcomeScreen(self)
        self.mainWidgit.initUI1()
        self.setCentralWidget(self.mainWidgit)

        w = 700
        h = 500

        #self.setGeometry((self.screen_res[0] - w) / 2, (self.screen_res[1] - h) / 2, w, h)
        self.setGeometry(self.screen_res[0] * 0.05, self.screen_res[1] * 0.0675, self.screen_res[0] * 0.9,
                         self.screen_res[1] * 0.85)
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
                    if self.help_screen:  # if help screen, don't re-train histogram
                        self.close()
                    else:
                        self.mainWidgit.close()
                        self.mainWidgit = WelcomeScreen(self)
                        self.mainWidgit.initUI3()
                        self.setCentralWidget(self.mainWidgit)
                elif self.screen_num == 3:
                    self.mainWidgit.close()
                    self.mainWidgit = PretrainScreen(self)
                    self.mainWidgit.initUI()
                    self.setCentralWidget(self.mainWidgit)
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
        self.header_label = QtGui.QLabel("<b>You're almost ready to start using Nomon!</b>")
        self.sub_label_1 = QtGui.QLabel(
            "<b>>></b>Before we begin, we need some information about your pressing accuracy "
            "so that we can better predict your selections.")
        self.sub_label_2 = QtGui.QLabel("<b>>></b>A clock will appear on the following screen, please press when the "
                                        "moving hand reaches noon until it disappears. Note: you do not have to press "
                                        "every time it passes.")
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

        hbox = QtGui.QHBoxLayout()

        self.clock = ClockWidgit('', self)
        self.clock.highlighted = True
        self.clock.angle = math.pi*2/3
        self.clock.setMinimumSize(200, 200)

        self.main_label = QtGui.QLabel(
            "Please press when the moving hand reaches Noon <b>" + str(self.parent.total_presses)
            + "</b> more times...")
        self.sub_label_1 = QtGui.QLabel("<i>(or press to continue)</i>")
        self.main_label.setFont(welcome_main_font)
        self.main_label.setWordWrap(True)
        self.sub_label_1.setFont(welcome_sub_font)

        self.start_button = QtGui.QPushButton("Start Training!")
        self.start_button.pressed.connect(self.start_buttton_func)

        vbox.addWidget(self.main_label, 1)
        vbox.addStretch(1)
        vbox.addWidget(self.clock, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
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

        
    def start_buttton_func(self):
        if self.parent.num_presses >= self.parent.total_presses:
            self.parent.on_finish()
        else:
            self.parent.on_start()


class Pretraining(StartWindow):

    def __init__(self, screen_res,sister):
        super(Pretraining, self).__init__(screen_res, False)
        self.training_ended = 0
        self.num_presses = 0
        self.sister = sister
        
        ######  Tiffany's pretraining alogrithm can go here #######
        # treat this wrapper class of the pretraining GUI Window as the keyboard class above
        # add whatever attributes from the keyboard class you need in here
        
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
        self.time_rotate = 2.0
        
        
        self.prev_data = None
        self.num_presses = 0
        
        
        
        if config.is_write_data:
            print "yeah writing data!"
            self.gen_handle()
            self.num_presses = 0

        else:
            self.file_handle = None
        
        self.num_stop_training = 20
        self.total_presses = 20
        
        self.mainWidgit = PretrainScreen(self)
        self.mainWidgit.initUI()
        self.radius = self.mainWidgit.clock.radius
        
        self.pbc = pre_broderclocks_pyqt.Pre_broderclocks(self, self.file_handle, self.time_rotate, self.use_num, self.user_id, time.time(), self.prev_data)
        self.wait_s = self.pbc.get_wait()
        self.num_stop_training = self.pbc.hsi.n_training
        
        
        #self.pbc.hsi.n_training #which is 20
        self.deactivate_press = False
        #whether training has actually started
        self.started = 0
        
    def gen_handle(self):
        data_file = "data/preconfig.pickle"
        self.file_handle = open(data_file, 'wb')
        
    
# =============================================================================
#     def keyPressEventRedef(self, e):
#         if e.key() == QtCore.Qt.Key_Space:
#             self.on_press()
#         self.play()
# =============================================================================
    
    
    def play(self):
        sound_file = "bell.mp3"
        QSound.play(sound_file)
    
    def on_press(self):
        self.num_presses +=1
        self.mainWidgit.main_label.setText("Please press when the moving hand reaches Noon <b>" +
                                           str(self.total_presses - self.num_presses) + "</b> more times...")
        #Log press time    
        if (not self.in_pause) and self.deactivate_press == False:
            #if config.is_write_data:
            self.pbc.select(time.time())
        
        
        if self.num_presses >= self.total_presses:
            print "finished calculating density"
            
            self.pbc.hsi.calculate_density()
            self.mainWidgit.main_label.setText("Training has finished!")
            
            self.mainWidgit.start_button.setText("Start Nomon")
            self.mainWidgit.start_button.show()
            
        
        self.on_start()
        self.play()

    def on_increment(self, angle):
        self.mainWidgit.clock.angle = angle
        self.mainWidgit.clock.repaint()

    def on_start(self):
        self.mainWidgit.main_label.setFocus()  # focus on not toggle-able widget to allow keypress event
        if not self.mainWidgit.start_pretrain:
            self.mainWidgit.start_pretrain = True
     
        if self.started ==0:
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
        if config.is_write_data:
            try:
                li = self.pbc.hsi.dens_li
                print "The length of li is" + str(len(li))
                z = self.pbc.hsi.Z
                pickle.dump([li, z, self.pbc.hsi.opt_sig, self.pbc.hsi.y_li], self.file_handle, protocol=pickle.HIGHEST_PROTOCOL)
                print "I'm quitting and the density is" + str(li)
                print "And the Z is " + str(z)
                print "file closed"
                self.file_handle.close()
            except IOError as (errno,strerror):
                print "I/O error({0}): {1}".format(errno, strerror)
        
        print "this worked"
        self.sister.bc.hsi.not_read_pickle = 0
        #self.sister.bc.hsi.update_dens(self.sister.bc.hsi.time_rotate)
        use_num, user_id, time_rotate, prev_data = self.sister.bc.use_num, self.sister.bc.user_id, self.sister.bc.time_rotate, self.sister.bc.prev_data
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
        
        self.close()
        
        
    
        

def main():
    app = QtGui.QApplication(sys.argv)
    screen_res = (app.desktop().screenGeometry().width(), app.desktop().screenGeometry().height())
    welcome = Pretraining(screen_res)
    app.processEvents()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
