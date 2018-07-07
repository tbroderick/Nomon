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

        self.clockTextAlign('auto', message=False)

        # File Menu Actions
        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        # Clock Menu Actions
        highContrastAction = QtGui.QAction('&High Contrast Mode', self)
        highContrastAction.triggered.connect(lambda: self.highContrastEvent())

        defaultClockAction = QtGui.QAction('&Default (Clock)', self)
        defaultClockAction.setStatusTip('Regular Nomon clock with sweeping minute hand')
        defaultClockAction.triggered.connect(lambda: self.clockChangeEvent('default'))
        defaultClockAction.setIcon(QtGui.QIcon(os.path.join("icons/", 'default.png')))

        radarClockAction = QtGui.QAction('&Radar (Clock)', self)
        radarClockAction.setStatusTip('Nomon clock with sweeping minute hand and radar trails')
        radarClockAction.triggered.connect(lambda: self.clockChangeEvent('radar'))
        radarClockAction.setIcon(QtGui.QIcon(os.path.join("icons/", 'radar.png')))

        ballClockAction = QtGui.QAction('&Ball (Filling)', self)
        ballClockAction.triggered.connect(lambda: self.clockChangeEvent('ball'))
        ballClockAction.setIcon(QtGui.QIcon(os.path.join("icons/", 'ball.png')))

        pacmanClockAction = QtGui.QAction('&Pac Man (Filling Pac Man)', self)
        pacmanClockAction.triggered.connect(lambda: self.clockChangeEvent('pac man'))
        pacmanClockAction.setIcon(QtGui.QIcon(os.path.join("icons/", 'pac_man.png')))

        barClockAction = QtGui.QAction('&Progress Bar', self)
        barClockAction.triggered.connect(lambda: self.clockChangeEvent('bar'))
        barClockAction.setIcon(QtGui.QIcon(os.path.join("icons/", 'bar.png')))

        # Text Menu Actions
        autoTextalignAction = QtGui.QAction('&Auto (recommended)', self)
        autoTextalignAction.triggered.connect(lambda: self.clockTextAlign('auto'))

        tcTextalignAction = QtGui.QAction('&Top Center', self)
        tcTextalignAction.triggered.connect(lambda: self.clockTextAlign('tc'))

        clTextalignAction = QtGui.QAction('&Center Left', self)
        clTextalignAction.triggered.connect(lambda: self.clockTextAlign('cl'))

        ccTextalignAction = QtGui.QAction('&Center', self)
        ccTextalignAction.triggered.connect(lambda: self.clockTextAlign('cc'))

        crTextalignAction = QtGui.QAction('&Center Right', self)
        crTextalignAction.triggered.connect(lambda: self.clockTextAlign('cr'))

        bcTextalignAction = QtGui.QAction('&Bottom Center', self)
        bcTextalignAction.triggered.connect(lambda: self.clockTextAlign('bc'))

        # Keyboard Layout Menu Actions
        defaultLayoutAction = QtGui.QAction('&Alphabetical (default)', self)
        defaultLayoutAction.triggered.connect(lambda: self.layoutChangeEvent('alphabetical'))

        qwertyLayoutAction = QtGui.QAction('&QWERTY', self)
        qwertyLayoutAction.triggered.connect(lambda: self.layoutChangeEvent('qwerty'))

        # Tools Menu Actions
        profanityFilterAction = QtGui.QAction('&Profanity Filter', self)
        profanityFilterAction.triggered.connect(self.profanityFilterEvent)

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
        viewMenu.addAction(highContrastAction)
        clockMenu = viewMenu.addMenu('&Clocks')
        clockMenu.addAction(defaultClockAction)
        clockMenu.addAction(radarClockAction)
        clockMenu.addAction(ballClockAction)
        clockMenu.addAction(pacmanClockAction)
        clockMenu.addAction(barClockAction)
        textMenu = viewMenu.addMenu('&Text Alignment')
        textMenu.addAction(autoTextalignAction)
        # textMenu.addAction(tcTextalignAction)
        centerTextMenu = textMenu.addMenu('&Center')
        centerTextMenu.addAction(clTextalignAction)
        centerTextMenu.addAction(ccTextalignAction)
        centerTextMenu.addAction(crTextalignAction)
        # textMenu.addAction(bcTextalignAction)
        keyboardMenu = viewMenu.addMenu('&Keyboard Layout')
        keyboardMenu.addAction(defaultLayoutAction)
        keyboardMenu.addAction(qwertyLayoutAction)

        toolsMenu = menubar.addMenu('&Tools')
        toolsMenu.addAction(profanityFilterAction)

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

    def highContrastEvent(self):
        messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Toggle High Contrast Mode", "Would you like to turn "
                                                                                               "<b>ON</b> High Contrast"
                                                                                               " Mode? <b>NOTICE:</b> "
                                                                                               "You will have to "
                                                                                               "restart Nomon for these"
                                                                                               " changes to take effect",
                                       QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
        messageBox.setDefaultButton(QtGui.QMessageBox.No)
        messageBox.setWindowIcon(self.icon)

        reply = messageBox.exec_()
        if reply == QtGui.QMessageBox.No:
            pickle.dump(False, open("user_preferences/high_contrast.p", "wb"))
        elif reply == QtGui.QMessageBox.Yes:
            pickle.dump(True, open("user_preferences/high_contrast.p", "wb"))

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
            if self.mainWidgit.text_alignment == 'auto':
                self.clockTextAlign('auto', message=False)

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
        messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Toggle Profanity Filter", "This will remove offensive"
                                                                                             " words from the suggestion"
                                                                                             " clocks. Would you like the"
                                                                                             " profanity filter to be ON?"
                                                                                             " <b>NOTICE:</b> You will "
                                                                                             "have to restart Nomon for"
                                                                                             " these changes to take"
                                                                                             " effect",
                                       QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
        messageBox.setDefaultButton(QtGui.QMessageBox.No)
        messageBox.setWindowIcon(self.icon)

        reply = messageBox.exec_()
        if reply == QtGui.QMessageBox.No:
            pickle.dump(kconfig.train_file_name_default, open('user_preferences/profanity_filter_preference.p', 'wb'))
        elif reply == QtGui.QMessageBox.Yes:
            pickle.dump(kconfig.train_file_name_censored, open('user_preferences/profanity_filter_preference.p', 'wb'))

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
        top_hbox.addStretch(4)
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
                            self.keyboard_grid.addLayout(undo_hbox, row * 2, key * 2 + 1)

                        else:
                            self.keyboard_grid.addWidget(self.clocks[clock_index + kconfig.N_pred], row * 2, key * 2 + 1)
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
                    if self.layout[row][key] in string.ascii_letters + kconfig.space_char:
                        key_grid = QtGui.QGridLayout()
                        key_grid.addWidget(self.clocks[clock_index + kconfig.N_pred], 0, 0)
                        for i in range(kconfig.N_pred):
                            key_grid.addWidget(self.clocks[clock_index + i], i+1, 0)

                        self.keyboard_grid.addLayout(key_grid, row * 2, key * 2 + 1)
                    else:
                        clock = self.clocks[clock_index + kconfig.N_pred]
                        if clock.text == kconfig.mybad_char:  # check if UNDO clock
                            self.undo_label = QtGui.QLabel(self.parent.previous_undo_text)
                            undo_font = QtGui.QFont('Consolas', 20)
                            undo_font.setStretch(80)
                            self.undo_label.setFont(undo_font)

                            undo_hbox = QtGui.QVBoxLayout()
                            undo_hbox.addWidget(clock)
                            undo_hbox.addWidget(self.undo_label)
                            self.keyboard_grid.addLayout(undo_hbox, row * 2, key * 2 + 1)

                        else:
                            self.keyboard_grid.addWidget(self.clocks[clock_index + kconfig.N_pred], row * 2,
                                                         key * 2 + 1)
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
