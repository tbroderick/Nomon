import sys
import os
import string
import config
import pickle
from widgets import *


class MainWindow(QtGui.QMainWindow):
    def __init__(self, screen_res):
        super(MainWindow, self).__init__()

        self.screen_res = screen_res
        self.clock_type = pickle.load(open("user_preferences/clock_preference.p", "rb"))

    def initUI(self):
        self.mainWidgit = MainKeyboardWidget(self, kconfig.key_chars, self.screen_res)
        self.mainWidgit.initUI()
        self.setCentralWidget(self.mainWidgit)
        self.high_contrast = pickle.load(open("user_preferences/high_contrast.p", "rb"))
        self.profanity_filter = pickle.load(open("user_preferences/profanity_filter_preference.p", "rb"))


        self.clockTextAlign('auto', message=False)

        # File Menu Actions
        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        # Clock Menu Actions
        self.highContrastAction = QtGui.QAction('&High Contrast Mode', self, checkable=True)
        self.highContrastAction.triggered.connect(lambda: self.highContrastEvent())

        self.defaultClockAction = QtGui.QAction('&Default (Clock)', self, checkable=True)
        self.defaultClockAction.setStatusTip('Regular Nomon clock with sweeping minute hand')
        self.defaultClockAction.triggered.connect(lambda: self.clockChangeEvent('default'))
        self.defaultClockAction.setIcon(QtGui.QIcon(os.path.join("icons/", 'default.png')))

        self.radarClockAction = QtGui.QAction('&Radar (Clock)', self, checkable=True)
        self.radarClockAction.setStatusTip('Nomon clock with sweeping minute hand and radar trails')
        self.radarClockAction.triggered.connect(lambda: self.clockChangeEvent('radar'))
        self.radarClockAction.setIcon(QtGui.QIcon(os.path.join("icons/", 'radar.png')))

        self.ballClockAction = QtGui.QAction('&Ball (Filling)', self, checkable=True)
        self.ballClockAction.triggered.connect(lambda: self.clockChangeEvent('ball'))
        self.ballClockAction.setIcon(QtGui.QIcon(os.path.join("icons/", 'ball.png')))

        self.pacmanClockAction = QtGui.QAction('&Pac Man (Filling Pac Man)', self, checkable=True)
        self.pacmanClockAction.triggered.connect(lambda: self.clockChangeEvent('pac man'))
        self.pacmanClockAction.setIcon(QtGui.QIcon(os.path.join("icons/", 'pac_man.png')))

        self.barClockAction = QtGui.QAction('&Progress Bar', self, checkable=True)
        self.barClockAction.triggered.connect(lambda: self.clockChangeEvent('bar'))
        self.barClockAction.setIcon(QtGui.QIcon(os.path.join("icons/", 'bar.png')))

        # Font Menu Actions
        self.smallFontAction = QtGui.QAction('&Small', self, checkable=True)
        self.smallFontAction.triggered.connect(lambda: self.changeFontSize('small'))

        self.medFontAction = QtGui.QAction('&Medium (Default)', self, checkable=True)
        self.medFontAction.triggered.connect(lambda: self.changeFontSize('med'))

        self.largeFontAction = QtGui.QAction('&Large', self, checkable=True)
        self.largeFontAction.triggered.connect(lambda: self.changeFontSize('large'))

        # Text Menu Actions
        self.autoTextalignAction = QtGui.QAction('&Auto (Recommended)', self, checkable=True)
        self.autoTextalignAction.triggered.connect(lambda: self.clockTextAlign('auto'))

        self.tcTextalignAction = QtGui.QAction('&Top Center', self, checkable=True)
        self.tcTextalignAction.triggered.connect(lambda: self.clockTextAlign('tc'))

        self.clTextalignAction = QtGui.QAction('&Center Left', self, checkable=True)
        self.clTextalignAction.triggered.connect(lambda: self.clockTextAlign('cl'))

        self.ccTextalignAction = QtGui.QAction('&Center', self, checkable=True)
        self.ccTextalignAction.triggered.connect(lambda: self.clockTextAlign('cc'))

        self.crTextalignAction = QtGui.QAction('&Center Right', self, checkable=True)
        self.crTextalignAction.triggered.connect(lambda: self.clockTextAlign('cr'))

        self.bcTextalignAction = QtGui.QAction('&Bottom Center', self, checkable=True)
        self.bcTextalignAction.triggered.connect(lambda: self.clockTextAlign('bc'))

        # Keyboard Layout Menu Actions
        self.defaultLayoutAction = QtGui.QAction('&Alphabetical (Default)', self, checkable=True)
        self.defaultLayoutAction.triggered.connect(lambda: self.layoutChangeEvent('alphabetical'))

        self.qwertyLayoutAction = QtGui.QAction('&QWERTY', self, checkable=True)
        self.qwertyLayoutAction.triggered.connect(lambda: self.layoutChangeEvent('qwerty'))
        # Tools Menu Actions
        self.profanityFilterAction = QtGui.QAction('&Profanity Filter', self, checkable=True)
        self.profanityFilterAction.triggered.connect(self.profanityFilterEvent)


        # Help Menu Actions
        helpAction = QtGui.QAction('&Help', self)
        helpAction.setStatusTip('Nomon help')
        helpAction.triggered.connect(self.helpEvent)

        aboutAction = QtGui.QAction('&About', self)
        aboutAction.setStatusTip('Application information')
        aboutAction.triggered.connect(self.aboutEvent)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        viewMenu = menubar.addMenu('&View')
        viewMenu.addAction(self.highContrastAction)
        clockMenu = viewMenu.addMenu('&Clocks')
        clockMenu.addAction(self.defaultClockAction)
        clockMenu.addAction(self.radarClockAction)
        clockMenu.addAction(self.ballClockAction)
        clockMenu.addAction(self.pacmanClockAction)
        clockMenu.addAction(self.barClockAction)
        textMenu = viewMenu.addMenu('&Text Alignment')
        textMenu.addAction(self.autoTextalignAction)
        # textMenu.addAction(self.tcTextalignAction)
        centerTextMenu = textMenu.addMenu('&Center')
        centerTextMenu.addAction(self.clTextalignAction)
        centerTextMenu.addAction(self.ccTextalignAction)
        centerTextMenu.addAction(self.crTextalignAction)
        fontMenu = viewMenu.addMenu('&Font Size')
        fontMenu.addAction(self.smallFontAction)
        fontMenu.addAction(self.medFontAction)
        fontMenu.addAction(self.largeFontAction)
        # textMenu.addAction(self.bcTextalignAction)
        keyboardMenu = viewMenu.addMenu('&Keyboard Layout')
        keyboardMenu.addAction(self.defaultLayoutAction)
        keyboardMenu.addAction(self.qwertyLayoutAction)


        toolsMenu = menubar.addMenu('&Tools')
        toolsMenu.addAction(self.profanityFilterAction)

        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(helpAction)
        helpMenu.addSeparator()
        helpMenu.addAction(aboutAction)

        self.setWindowTitle('Nomon Keyboard')

        self.icon = QtGui.QIcon(os.path.join("icons/", 'nomon.png'))
        self.setWindowIcon(self.icon)
        self.setGeometry(self.screen_res[0] * 0.05, self.screen_res[1] * 0.0675, self.screen_res[0] * 0.9,
                         self.screen_res[1] * 0.85)
        self.show()

        self.check_filemenu()

    def check_filemenu(self):
        def switch(unit, mode):
            if mode == unit.isChecked():
                pass
            else:
                unit.toggle()
        # check clocks
        switch(self.defaultClockAction, self.clock_type == 'default')
        switch(self.radarClockAction, self.clock_type == 'radar')
        switch(self.ballClockAction, self.clock_type == 'ball')
        switch(self.pacmanClockAction, self.clock_type == 'pac_man')
        switch(self.barClockAction, self.clock_type == 'bar')

        # check text alignment
        switch(self.ccTextalignAction, self.alignment == 'cc')
        switch(self.clTextalignAction, self.alignment == 'cl')
        switch(self.crTextalignAction, self.alignment == 'cr')
        switch(self.autoTextalignAction, self.mainWidgit.text_alignment == 'auto')

        # check profanity
        switch(self.profanityFilterAction, self.profanity_filter)

        # check font menu
        from config import font_scale
        switch(self.smallFontAction, font_scale == 0.75)
        switch(self.medFontAction, font_scale == 1.)
        switch(self.largeFontAction, font_scale == 1.5)

        # check high contrast
        switch(self.highContrastAction, self.high_contrast)

        # check layout
        switch(self.defaultLayoutAction, self.mainWidgit.layout == kconfig.alpha_key_chars)
        switch(self.qwertyLayoutAction, self.mainWidgit.layout == kconfig.qwerty_key_chars)

    def changeFontSize(self, size):
        pickle.dump(size, open("user_preferences/font_scale.p", "wb"))

        reload(config)
        from config import top_bar_font
        from config import text_box_font

        self.mainWidgit.sldLabel.setFont(top_bar_font)
        self.mainWidgit.speed_slider_label.setFont(top_bar_font)
        self.mainWidgit.wpm_label.setFont(top_bar_font)
        self.mainWidgit.cb_talk.setFont(top_bar_font)
        self.mainWidgit.cb_learn.setFont(top_bar_font)
        self.mainWidgit.cb_pause.setFont(top_bar_font)
        self.mainWidgit.text_box.setFont(text_box_font)

        self.mainWidgit.wpm_label.repaint()
        self.mainWidgit.cb_talk.repaint()
        self.mainWidgit.cb_learn.repaint()
        self.mainWidgit.cb_pause.repaint()
        self.mainWidgit.sldLabel.repaint()
        self.mainWidgit.speed_slider_label.repaint()
        self.mainWidgit.text_box.repaint()

        self.check_filemenu()

    def highContrastEvent(self):

        if self.high_contrast:
            hc_status = "ON"
        else:
            hc_status = "OFF"
        messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Toggle Profanity Filter", "High Contrast Mode is "
                                                                                             "currently <b>"
                                       + hc_status + "</b>. Please select your desired setting below. "
                                                     "<b>NOTICE:</b> Changes will not take effect until "
                                                     "Nomon is restarted.")
        messageBox.addButton(QtGui.QPushButton('On'), QtGui.QMessageBox.YesRole)
        messageBox.addButton(QtGui.QPushButton('Off'), QtGui.QMessageBox.NoRole)


        messageBox.setDefaultButton(QtGui.QMessageBox.No)
        messageBox.setWindowIcon(self.icon)

        reply = messageBox.exec_()
        if reply == 1:
            pickle.dump(False, open("user_preferences/high_contrast.p", "wb"))
        elif reply == 0:
            pickle.dump(True, open("user_preferences/high_contrast.p", "wb"))
        self.check_filemenu()


    def clockChangeEvent(self, design):
        messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Change Clock Design", "This will change the clocks "
                                                                                         "to the <b>" + design + "</b"
                                                                                         "> design",
                                       QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
        design = design.replace(' ', '_')
        messageBox.setDefaultButton(QtGui.QMessageBox.Cancel)
        messageBox.setIconPixmap(QtGui.QPixmap(os.path.join("icons/", design + '.png')))
        messageBox.setWindowIcon(self.icon)

        reply = messageBox.exec_()
        if reply == QtGui.QMessageBox.Ok:
            self.clock_type = design
            pickle.dump(design, open("user_preferences/clock_preference.p", "wb"))
            self.check_filemenu()
            self.mainWidgit.wpm_label.setText("Selections/Min: "+"----")
            self.wpm_data = config.Stack(config.wpm_history_length)
            self.wpm_time = 0

            if self.mainWidgit.text_alignment == 'auto':
                self.clockTextAlign('auto', message=False)
                self.check_filemenu()


    def layoutChangeEvent(self, layout):
        messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Change Keyboard Layout", "This will change the clock "
                                                                                         "layout to <b>" + layout + "</b"
                                                                                         "> order. <b>NOTICE:</b> You "
                                                                                         "will have to restart Nomon for"
                                                                                         " these changes to take effect",
                                       QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
        messageBox.setDefaultButton(QtGui.QMessageBox.Cancel)
        messageBox.setWindowIcon(self.icon)

        reply = messageBox.exec_()
        if reply == QtGui.QMessageBox.Ok:
            if layout == 'alphabetical':
                pickle.dump(kconfig.alpha_key_chars, open("user_preferences/layout_preference.p", "wb"))
            elif layout == 'qwerty':
                pickle.dump(kconfig.qwerty_key_chars, open("user_preferences/layout_preference.p", "wb"))
            self.check_filemenu()


    def clockTextAlign(self, alignment, message=True):
        if alignment == "auto":
            self.mainWidgit.text_alignment = 'auto'
            messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Change Text Alignment", "The text will be <b>"
                                                                                               "Auto-Aligned</b> to "
                                                                                               "best suit the keyboard"
                                                                                               " layout. (recommended)",
                                           QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
            if self.clock_type == "bar":
                alignment = "cc"
            else:
                alignment = "cr"
        else:
            self.mainWidgit.text_alignment = alignment
            if alignment == "cr":
                alignment_name = 'Center Right'
            elif alignment == "cc":
                alignment_name = 'Center'
            elif alignment == "cl":
                alignment_name = 'Center Left'
            elif alignment == "bc":
                alignment_name = 'Bottom Center'
            elif alignment == "tc":
                alignment_name = 'Top Center'

            messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Change Text Alignment", "This will change the "
                                                                                               "text to be aligned on "
                                                                                               "the <b>"
                                           + alignment_name + "</b>  of the clocks",
                                           QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
        self.alignment = alignment
        if message:
            messageBox.setDefaultButton(QtGui.QMessageBox.Cancel)
            messageBox.setWindowIcon(self.icon)

            reply = messageBox.exec_()
            if reply == QtGui.QMessageBox.Ok:
                self.mainWidgit.alignment = alignment
                self.resizeClocks()
                self.check_filemenu()

        else:
            self.mainWidgit.alignment = alignment
            self.resizeClocks()

    def resizeClocks(self):
        if self.alignment[0] == 'b' or self.mainWidgit.alignment[0] == 't':
            for clock in self.mainWidgit.clocks:
                clock.setMaximumHeight(clock.maxSize*2)
                clock.setMinimumSize(clock.minSize*2.1, clock.minSize*2.1)
        else:
            for clock in self.mainWidgit.clocks:
                clock.setMaximumHeight(clock.maxSize)
                clock.setMinimumSize(clock.minSize, clock.minSize)

    def profanityFilterEvent(self):
        profanity_status = (pickle.load(open('user_preferences/profanity_filter_preference.p', 'rb')) ==
                            kconfig.train_file_name_censored)
        if profanity_status:
            profanity_status = "ON"
        else:
            profanity_status = "OFF"

        messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Toggle Profanity Filter", "The profanity filter is "
                                                                                             "currently <b>"
                                       + profanity_status + "</b>. Please select your desired setting below. "
                                                            "<b>NOTICE:</b> Changes will not take effect until "
                                                            "Nomon is restarted.")
        messageBox.addButton(QtGui.QPushButton('On'), QtGui.QMessageBox.YesRole)
        messageBox.addButton(QtGui.QPushButton('Off'), QtGui.QMessageBox.NoRole)
        messageBox.setIconPixmap(QtGui.QPixmap(os.path.join('icons/block.png')))

        messageBox.setDefaultButton(QtGui.QMessageBox.No)
        messageBox.setWindowIcon(self.icon)

        reply = messageBox.exec_()
        if reply == 1:
            pickle.dump(kconfig.train_file_name_default, open('user_preferences/profanity_filter_preference.p', 'wb'))
        elif reply == 0:
            pickle.dump(kconfig.train_file_name_censored, open('user_preferences/profanity_filter_preference.p', 'wb'))
        self.check_filemenu()


    def aboutEvent(self):
        QtGui.QMessageBox.question(self, 'About Nomon', "Copyright 2009 Tamara Broderick\n"
                                                        "This file is part of Nomon Keyboard.\n\n"

                                                        "Nomon Keyboard is free software: you can redistribute "
                                                        "it and/or modify the Free Software Foundation, either "
                                                        "version 3 of the License, or (at your option) any "
                                                        "later version.\n\n"

                                                        "Nomon Keyboard is distributed in the hope that it will"
                                                        " be useful, but WITHOUT ANY WARRANTY; without even the"
                                                        " implied warranty of MERCHANTABILITY or FITNESS FOR A "
                                                        "PARTICULAR PURPOSE.  See the GNU General Public "
                                                        "License for more details.\n\n"

                                                        "You should have received a copy of the GNU General "
                                                        "Public License along with Nomon Keyboard.  If not, see"
                                                        " <http://www.gnu.org/licenses/>.",
                                   QtGui.QMessageBox.Ok)

    def helpEvent(self):
        self.launch_help()


class MainKeyboardWidget(QtGui.QWidget):

    def __init__(self, parent, layout, screen_res):
        super(MainKeyboardWidget, self).__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.parent = parent
        self.layout = layout
        self.screen_res = screen_res
        self.size_factor = min(self.screen_res) / 1080.
        self.text_alignment = 'auto'

    def initUI(self):

        # generate slider for clock rotation speed
        self.speed_slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.speed_slider.setRange(config.scale_min, config.scale_max)
        self.speed_slider.setValue(config.start_speed)
        self.speed_slider_label = QtGui.QLabel('Clock Rotation Speed:')

        self.speed_slider_label.setFont(top_bar_font)
        self.sldLabel = QtGui.QLabel(str(self.speed_slider.value()))
        self.sldLabel.setFont(top_bar_font)

        # wpm label
        self.wpm_label = QtGui.QLabel("Selections/Min: "+"----")
        self.wpm_label.setFont(top_bar_font)


        # generate learn, speak, talk checkboxes
        self.cb_talk = QtGui.QCheckBox('Talk', self)
        self.cb_learn = QtGui.QCheckBox('Learn', self)
        self.cb_pause = QtGui.QCheckBox('Pause', self)
        self.cb_talk.toggle()
        self.cb_talk.setFont(top_bar_font)
        self.cb_learn.toggle()
        self.cb_learn.setFont(top_bar_font)
        self.cb_pause.toggle()
        self.cb_pause.setFont(top_bar_font)

        # generate clocks from layout
        self.generateClocks()

        self.text_box = QtGui.QTextEdit("", self)

        self.text_box.setFont(text_box_font)
        self.text_box.setMinimumSize(300, 100)
        self.text_box.setReadOnly(True)

        # generate histogram
        self.histogram = HistogramWidget(self)

        if __name__ != '__main__':
            self.speed_slider.valueChanged[int].connect(self.changeValue)
            self.cb_learn.toggled[bool].connect(self.parent.toggle_learn_button)
            self.cb_pause.toggled[bool].connect(self.parent.toggle_pause_button)
            self.cb_talk.toggled[bool].connect(self.parent.toggle_talk_button)

        # layout slider and checkboxes
        top_hbox = QtGui.QHBoxLayout()
        top_hbox.addWidget(self.speed_slider_label, 1)
        top_hbox.addWidget(self.speed_slider, 16)
        top_hbox.addWidget(self.sldLabel, 1)
        top_hbox.addStretch(2)
        top_hbox.addWidget(self.wpm_label, 1)
        top_hbox.addStretch(2)

        top_hbox.addWidget(self.cb_talk, 1)
        top_hbox.addWidget(self.cb_learn, 1)
        top_hbox.addWidget(self.cb_pause, 1)
        top_hbox.addStretch(1)

        # stack layouts vertically
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setSpacing(0)
        self.vbox.addLayout(top_hbox)
        self.vbox.addStretch(1)
        self.vbox.addWidget(HorizontalSeparator())

        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.text_box)
        splitter1.addWidget(self.histogram)
        splitter1.setSizes([1, 1])
        self.histogram.setMaximumHeight(160 * self.size_factor)
        self.text_box.setMaximumHeight(160 * self.size_factor)

        self.vbox.addSpacing(5)
        self.vbox.addWidget(splitter1, 4)
        self.layoutClocks()
        self.setLayout(self.vbox)

        if __name__ != '__main__':  # remove inheritance dependent timers for sole GUI run
            self.frame_timer = QtCore.QTimer()
            self.frame_timer.timeout.connect(self.parent.on_timer)
            self.frame_timer.start(config.ideal_wait_s * 1000)

            self.pause_timer = QtCore.QTimer()
            self.pause_timer.setSingleShot(True)
            self.pause_timer.timeout.connect(self.parent.end_pause)

            self.highlight_timer = QtCore.QTimer()
            self.highlight_timer.setSingleShot(True)
            self.highlight_timer.timeout.connect(self.parent.end_highlight)

        # Tool Tips
        QtGui.QToolTip.setFont(QtGui.QFont('Monospace', 12))
        self.setToolTip("This is the Nomon Keyboard. To select an option, \n "
                        "find the clock immediately to its left. Press the \n"
                        "spacebar when the moving hand is near noon.")
        self.speed_slider_label.setToolTip("This slider scales the speed of clock rotation. Higher \n"
                                "values correspond to the clock hand moving faster.")
        self.speed_slider.setToolTip("This slider scales the speed of clock rotation. Higher \n"
                            "values correspond to the clock hand moving faster.")
        self.cb_pause.setToolTip("If this button is checked, there will be a brief \n"
                                 "pause and minty screen flash after each selection \n"
                                 "you make.")
        self.cb_talk.setToolTip("If this button is checked and if you have festival \n"
                                "installed and working on your system, there will be \n"
                                "spoken feedback after each selection you make.")
        self.cb_learn.setToolTip("If this button is checked, the program will adapt \n"
                                 "to how you click around noon (illustrated in the \n"
                                 "histogram below).")
        self.histogram.setToolTip("This is Nomon's estimate of where you click relative \n"
                                  "to noon on the clocks. The thinner the distribution, \n"
                                  "the more precisely Nomon thinks you are clicking.")

    def changeValue(self, value):  # Change clock speed
        self.sldLabel.setText(str(self.speed_slider.value()))
        self.parent.change_speed(value)
        pickle.dump(value, open("user_preferences/start_speed.p", 'wb'))

    def getWords(self, char):  # Reformat word list into blueprint for GUI construction
        i = 0
        output = []
        for word in self.parent.word_list:
            index = len(self.parent.prefix)
            if word[index] == char:
                i += 1
                if i > 3:
                    break
                output += [word]
        return output

    def generateClocks(self):  # Generate the clock widgets according to blueprint from self.getWords
        self.clocks = []
        for row in self.layout:
            for text in row:
                clock = ClockWidgit(text, self)
                words = self.getWords(clock.text.lower())
                word_clocks = ['' for i in range(kconfig.N_pred)]
                i = 0
                for word in words:
                    word_clocks[i] = ClockWidgit(word, self)
                    i += 1
                for n in range(i, 3):
                    word_clocks[n] = ClockWidgit('', self, filler_clock=True)
                self.clocks += word_clocks
                self.clocks += [clock]

    def updateClocks(self):  # Used to change text and turn off clocks after initialization
        index = 0
        for row in self.layout:
            for text in row:
                words = self.getWords(text.lower())
                for word in words:
                    self.clocks[index].filler_clock = False
                    self.clocks[index].text = word
                    index += 1
                for i in range(len(words), 3):
                    self.clocks[index].text = ''
                    self.clocks[index].filler_clock = True
                    self.clocks[index].repaint()
                    index += 1
                self.clocks[index].text = text
                index += 1

    def layoutClocks(self):  # called after self.generateClocks, arranges clocks in grid

        # layout keyboard in grid
        self.keyboard_grid = QtGui.QGridLayout()
        self.punctuation_grid = QtGui.QGridLayout()
        self.back_clear_vbox = QtGui.QVBoxLayout()

        clock_index = 0
        if len(self.layout) > 4:  # layout used for keyboard with many rows (Alphabetical)
            for row in range(len(self.layout)):
                self.keyboard_grid.addWidget(VerticalSeparator(), row * 2, 0)
                for key in range(len(self.layout[row])):
                    if self.layout[row][key] in string.ascii_letters + kconfig.space_char:  # check if key has words
                        # make sub grid for each char and words
                        key_grid = QtGui.QGridLayout()
                        key_grid.addWidget(self.clocks[clock_index + kconfig.N_pred], 0, 0, kconfig.N_pred, 1)
                        for i in range(kconfig.N_pred):
                            key_grid.addWidget(self.clocks[clock_index + i], i, 1)
                        key_grid.setColumnMinimumWidth(0, self.clocks[clock_index + kconfig.N_pred].minSize * 3)

                        key_grid.setColumnStretch(0, 1)
                        key_grid.setColumnStretch(1, 3)
                        self.keyboard_grid.addLayout(key_grid, row * 2, key * 2 + 1)
                    else:
                        clock = self.clocks[clock_index + kconfig.N_pred]
                        if clock.text == kconfig.mybad_char:  # check if UNDO clock (special layout with Undo text)
                            self.undo_label = QtGui.QLabel(self.parent.previous_undo_text)
                            undo_font = QtGui.QFont('Consolas', 20)
                            undo_font.setStretch(80)
                            self.undo_label.setFont(undo_font)

                            undo_hbox = QtGui.QVBoxLayout()
                            undo_hbox.addWidget(clock)
                            undo_hbox.addWidget(self.undo_label)
                            self.keyboard_grid.addLayout(undo_hbox, row * 2, (key - len(kconfig.break_chars[0])-1) * 2 + 1)
                        elif clock.text in kconfig.break_chars[0]:
                            self.punctuation_grid.addWidget(clock, kconfig.break_chars[0].index(clock.text), 0)
                        elif clock.text == kconfig.break_chars[1]:
                                self.keyboard_grid.addLayout(self.punctuation_grid, row * 2, key * 2 + 1)

                                self.punctuation_grid.addWidget(VerticalSeparator(), 0, 1, len(kconfig.break_chars[0]), 1)
                                self.punctuation_grid.addWidget(clock, 1, 2)
                                for i in range(kconfig.N_pred):
                                    self.punctuation_grid.addWidget(self.clocks[clock_index + i], i, 3)
                                self.punctuation_grid.setColumnStretch(0, 1)
                                self.punctuation_grid.setColumnStretch(2, 1)
                                self.punctuation_grid.setColumnStretch(3, 3)
                        elif clock.text == kconfig.back_char:
                            self.back_clear_vbox.addWidget(clock)
                            self.keyboard_grid.addLayout(self.back_clear_vbox, row * 2,
                                                         (key - len(kconfig.break_chars[0])) * 2 + 1)
                        elif clock.text == kconfig.clear_char:
                            self.back_clear_vbox.addWidget(clock)

                        else:
                            self.keyboard_grid.addWidget(clock, row * 2,
                                                         (key - len(kconfig.break_chars[0])) * 2 + 1)

                    # add sub grid to main keyboard grid
                    self.keyboard_grid.addWidget(VerticalSeparator(), row * 2, key * 2 + 2)
                    self.keyboard_grid.addWidget(HorizontalSeparator(), row * 2 + 1, key * 2 + 1)

                    clock_index += kconfig.N_pred + 1
                self.keyboard_grid.setRowStretch(row * 2, 1)

        else:
            # layout used for keyboard with many columns (QWERTY)
            # sub grids are now completely vertical to save horizontal space
            for row in range(len(self.layout)):
                self.keyboard_grid.addWidget(VerticalSeparator(), row * 2, 0)
                for key in range(len(self.layout[row])):
                    clock = self.clocks[clock_index + kconfig.N_pred]
                    if self.layout[row][key] in string.ascii_letters:

                        key_grid = QtGui.QGridLayout()
                        key_grid.addWidget(self.clocks[clock_index + kconfig.N_pred], 0, 0)
                        for i in range(kconfig.N_pred):
                            key_grid.addWidget(self.clocks[clock_index + i], i+1, 0)

                        self.keyboard_grid.addLayout(key_grid, row * 2, key * 2 + 1)
                    else:

                        if clock.text == kconfig.mybad_char:  # check if UNDO clock
                            self.undo_label = QtGui.QLabel(self.parent.previous_undo_text)
                            undo_font = QtGui.QFont('Consolas', 20)
                            undo_font.setStretch(80)
                            self.undo_label.setFont(undo_font)

                            undo_hbox = QtGui.QVBoxLayout()
                            undo_hbox.addWidget(clock)
                            undo_hbox.addWidget(self.undo_label)
                            self.keyboard_grid.addLayout(undo_hbox, row * 2, key * 2 + 1)
                        elif clock.text == kconfig.space_char:
                            key_grid = QtGui.QGridLayout()
                            key_grid.addWidget(clock, 0, 0)
                            for i in range(kconfig.N_pred):
                                key_grid.addWidget(self.clocks[clock_index + i], i + 1, 0)

                            self.keyboard_grid.addLayout(key_grid, 6, 7)
                            self.keyboard_grid.addWidget(VerticalSeparator(), 6, 8)
                            self.keyboard_grid.addWidget(HorizontalSeparator(), 7, 7)
                        elif clock.text == kconfig.break_chars[1]:
                            key_grid = QtGui.QGridLayout()
                            key_grid.addWidget(clock, 0, 0)
                            for i in range(kconfig.N_pred):
                                key_grid.addWidget(self.clocks[clock_index + i], i + 1, 0)

                            self.keyboard_grid.addLayout(key_grid, 2, 19)
                            self.keyboard_grid.addWidget(VerticalSeparator(), 2, 20)
                            self.keyboard_grid.addWidget(HorizontalSeparator(), 3, 19)

                        elif clock.text in kconfig.break_chars[0]:
                            self.keyboard_grid.addWidget(self.clocks[clock_index + kconfig.N_pred], row * 2,
                                                         (key-2) * 2 + 1)
                        else:
                            self.keyboard_grid.addWidget(self.clocks[clock_index + kconfig.N_pred], row * 2,
                                                         key * 2 + 1)
                    if key < 10:
                        self.keyboard_grid.addWidget(VerticalSeparator(), row * 2, key * 2 + 2)
                        self.keyboard_grid.addWidget(HorizontalSeparator(), row * 2 + 1, key * 2 + 1)


                    clock_index += kconfig.N_pred + 1
                self.keyboard_grid.setRowStretch(row * 2, 2)

        self.vbox.insertLayout(3, self.keyboard_grid, 6)  # add keyboard grid to place in main layout


def main():  # set up 'dummy' keyboard instance to allow for pure GUI layout debugging
    app = QtGui.QApplication(sys.argv)
    screen_res = (app.desktop().screenGeometry().width(), app.desktop().screenGeometry().height())
    ex = MainWindow(screen_res)
    word_list = open('word_list.txt', 'r')
    words = word_list.read()
    words = words.split()
    word_list.close()
    ex.word_list = []
    for letter in string.ascii_lowercase:
        i = 0
        for word in words:
            if word[0] == letter and i < kconfig.N_pred:
                i += 1
                ex.word_list += [word]
    ex.prefix = ''
    ex.bars = kconfig.bars
    ex.previous_undo_text = ''
    ex.initUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
