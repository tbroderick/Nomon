import sys, os
import math
import string
import config
import kconfig
from PyQt4 import QtGui, QtCore


class ClockFiller(QtGui.QWidget):  # Transparent widget to occupy spacing when clocks are off

    def __init__(self, parent):
        super(ClockFiller, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):

        self.size_factor = self.parent.size_factor
        self.minSize = round(35 * self.size_factor)
        self.maxSize = round(50 * self.size_factor)
        self.setMinimumSize(self.minSize, self.minSize)
        self.setMaximumHeight(self.maxSize)
        self.setBaseSize(self.minSize, self.minSize)


class ClockWidgit(QtGui.QWidget):

    def __init__(self, text, parent, char_clock=True):
        super(ClockWidgit, self).__init__()

        self.text = text
        self.start_angle = 0
        self.parent = parent
        self.char_clock = char_clock
        self.highlighted = False
        self.selected = False
        self.initUI()

    def initUI(self):

        self.size_factor = self.parent.size_factor
        self.minSize = round(35 * self.size_factor)
        self.maxSize = round(50 * self.size_factor)
        # self.minSize = round(100 * self.size_factor)
        # self.maxSize = round(200 * self.size_factor)
        # self.setMaximumSize(self.maxSize, self.maxSize)\
        self.setMinimumSize(self.minSize, self.minSize)
        self.setMaximumHeight(self.maxSize)
        self.setBaseSize(self.minSize, self.minSize)

        self.angle = 0
        self.filled = False

    def setAngle(self, angle):

        self.angle = angle

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawClock(e, qp)
        qp.end()

    def drawClock(self, e, qp):

        if self.parent.parent.clock_type == 'ball':
            def minute_hand_from_angle(angle, radius):
                radius *= 1.22
                if self.selected:
                    brush.setColor(QtGui.QColor(20, 245, 20))

                elif self.highlighted:
                    brush.setColor(QtGui.QColor(150, 150, 255))
                else:
                    brush.setColor(QtGui.QColor(100, 100, 100))
                qp.setBrush(brush)
                pen.setColor(QtGui.QColor(0, 0, 0, 0))
                qp.setPen(pen)

                angle -= math.pi/2
                angle = math.atan2(math.cos(angle), math.sin(angle))/math.pi
                print(angle)
                size_factor = (angle)

                qp.drawEllipse(center, radius*size_factor, radius*size_factor)

            hour_hand_from_angle = lambda x, y: x

        elif self.parent.parent.clock_type == 'radar':

            def clock_color(color_factor):
                if self.selected:
                    pen.setColor(QtGui.QColor(255 * color_factor, 255, 255 * color_factor))
                    qp.setPen(pen)
                elif self.highlighted:
                    pen.setColor(QtGui.QColor(255 * color_factor, 255 * color_factor, 255))
                    qp.setPen(pen)
                else:
                    pen.setColor(QtGui.QColor(255 * (color_factor), 255 * (color_factor), 255 * (color_factor)))
                    qp.setPen(pen)

            def hour_hand_from_angle(angle, radius):
                radius *= 1.2718
                pen.setCapStyle(QtCore.Qt.FlatCap)
                pen.setWidth(3)
                qp.setPen(pen)
                angle -= math.pi / 2  # reference angle from noon
                far_point = center + QtCore.QPointF(math.cos(angle) * radius, math.sin(angle) * radius)
                qp.drawLine(center, far_point)

            def minute_hand_from_angle(angle, radius):
                radius *= 1.2
                angle -= math.pi / 2  # reference angle from noon
                n = 8.
                length = math.pi * 2 / 3
                pen.setWidth(clock_rad * clock_thickness * 1.5)
                qp.setPen(pen)
                for inc_angle in range(int(n)):
                    inc_angle /= n
                    color_factor = min(1 - inc_angle, 1)
                    clock_color(color_factor)
                    far_point = center + QtCore.QPointF(math.cos(angle - length + inc_angle * length) * radius,
                                                        math.sin(angle - length + inc_angle * length) * radius)
                    qp.drawLine(center, far_point)
                far_point = center + QtCore.QPointF(math.cos(angle) * radius, math.sin(angle) * radius)
                pen.setWidth(clock_rad * clock_thickness)
                qp.setPen(pen)

        elif self.parent.parent.clock_type == 'default':

            def minute_hand_from_angle(angle, radius):

                angle -= math.pi / 2  # reference angle from noon

                far_point = center + QtCore.QPointF(math.cos(angle) * radius, math.sin(angle) * radius)
                qp.drawLine(center, far_point)

            hour_hand_from_angle = lambda x, y: minute_hand_from_angle(x, y*0.571)

        # calculate size of clock from available space
        size = self.size()
        w = size.width()
        h = size.height()
        constraint = h
        clock_rad = constraint / 2
        clock_thickness = 1. / 6
        center = QtCore.QPointF(constraint / 2, constraint / 2)

        # draw clock face
        pen = QtGui.QPen()
        if self.selected:
            pen.setColor(QtGui.QColor(20, 245, 20))

        elif self.highlighted:
            pen.setColor(QtGui.QColor(0, 0, 255))
        else:
            pen.setColor(QtGui.QColor(0, 0, 0))
        qp.setPen(pen)

        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        pen.setWidth(3)
        qp.setPen(pen)
        qp.setBrush(brush)

        qp.drawEllipse(center, clock_rad * (1 - clock_thickness / 2), clock_rad * (1 - clock_thickness / 2))

        # draw hands
        pen .setWidth(clock_rad * clock_thickness)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        qp.setPen(pen)

        threshold = 0.025
        if math.sin(self.angle - math.pi / 2) < -1+threshold:
            if self.highlighted:
                pen.setColor(QtGui.QColor(0, 255, 255))
            elif not (self.selected):
                pen.setColor(QtGui.QColor(150, 150, 150))
            qp.setPen(pen)

        minute_hand_from_angle(self.angle + self.start_angle, clock_rad*0.7)  # Minute Hand

        if self.selected:
            pen.setColor(QtGui.QColor(20, 245, 20))

        elif self.highlighted:
            pen.setColor(QtGui.QColor(0, 0, 255))
        else:
            pen.setColor(QtGui.QColor(0, 0, 0))
        qp.setPen(pen)
        hour_hand_from_angle(0, clock_rad * 0.7)  # Hour hand

        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 0))
        qp.setPen(pen)
        qp.setBrush(brush)

        qp.drawEllipse(center, clock_rad * (1 - clock_thickness / 2), clock_rad * (1 - clock_thickness / 2))

        # draw text
        qp.setPen(QtGui.QColor(0, 0, 0))
        if self.highlighted:
            qp.setPen(QtGui.QColor(0, 0, 0))
        font = QtGui.QFont('consolas')
        font.setBold(False)

        if len(self.text) > 11:
            reduce_factor = 1 - (len(self.text) - 10) / 40.
            font.setStretch(max(63., 80 * reduce_factor))
            font.setPointSize(clock_rad * reduce_factor)
        else:
            font.setStretch(85)
            font.setPointSize(clock_rad)

        qp.setFont(font)
        qp.drawText(center.x() + clock_rad, center.y() + clock_rad * .6, self.text)


    def drawPacManClock(self, e, qp):
        def hand_from_angle(angle, radius):
            if round(angle+math.pi / 2, 1) < 0.01:
                self.filled = (self.filled == False)

            if self.filled:
                if self.selected:
                    pen.setColor(QtGui.QColor(20, 245, 20))

                elif self.highlighted:
                    pen.setColor(QtGui.QColor(0, 0, 255))
                else:
                    pen.setColor(QtGui.QColor(0, 0, 0))
            else:
                pen.setColor(QtGui.QColor(255, 255, 255))
            qp.setPen(pen)




            angle -= math.pi / 2  # reference angle from noon

            inc_angle = 0
            increment = 0.15
            while inc_angle <= angle + math.pi+increment:

                far_point = center + QtCore.QPointF(math.cos(inc_angle- math.pi / 2) * radius,
                                                    math.sin(inc_angle- math.pi / 2) * radius)
                qp.drawLine(center, far_point)
                inc_angle += increment



        # calculate size of clock from available space
        size = self.size()
        w = size.width()
        h = size.height()
        constraint = h
        clock_rad = constraint / 2
        clock_thickness = 1. / 6
        center = QtCore.QPointF(constraint / 2, constraint / 2)

        # draw clock face
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        if self.filled:
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        else:
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        if self.highlighted:
            pen = QtGui.QPen(QtGui.QColor(0, 0, 255))
        if self.selected:
            pen = QtGui.QPen(QtGui.QColor(20, 229, 20))
        qp.setPen(pen)
        qp.setBrush(brush)

        qp.drawEllipse(center, clock_rad * (1 - clock_thickness / 2), clock_rad * (1 - clock_thickness / 2))

        # draw hands
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0), clock_rad * clock_thickness)
        if self.highlighted:
            pen = QtGui.QPen(QtGui.QColor(0, 0, 255), clock_rad * clock_thickness)
        if self.selected:
            pen = QtGui.QPen(QtGui.QColor(20, 229, 20), clock_rad * clock_thickness)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        qp.setPen(pen)

        hand_from_angle(self.angle + self.start_angle, clock_rad * 0.825)  # Minute Hand

        # draw text
        qp.setPen(QtGui.QColor(0, 0, 0))
        if self.highlighted:
            qp.setPen(QtGui.QColor(0, 0, 0))
        font = QtGui.QFont('consolas')
        font.setBold(False)

        if len(self.text) > 11:
            reduce_factor = 1 - (len(self.text) - 10) / 40.
            font.setStretch(max(63., 80 * reduce_factor))
            font.setPointSize(clock_rad * reduce_factor)
        else:
            font.setStretch(85)
            font.setPointSize(clock_rad)

        qp.setFont(font)
        qp.drawText(center.x() + clock_rad, center.y() + clock_rad * .6, self.text)


class HistogramWidget(QtGui.QWidget):

    def __init__(self, parent):
        super(HistogramWidget, self).__init__()
        self.parent = parent
        self.bars = parent.parent.bars
        self.initUI()

    def initUI(self):
        self.setMinimumSize(200, 100)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.bars = self.parent.parent.bars
        self.drawBars(qp)
        qp.end()

    def drawBars(self, qp):
        # calculate size of histogram from available space
        size = self.size()
        w = size.width()
        h = size.height() - 1

        max_value = max(self.bars)
        h_scale = h / max_value
        bar_width = float(w) / len(self.bars)

        qp.setPen(QtGui.QPen(QtGui.QColor(120, 120, 120), 1))
        qp.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        qp.drawRect(0, 0, w - 1, h)

        pen = QtGui.QPen(QtGui.QColor(0, 0, 255), 1)
        qp.setPen(pen)
        brush = QtGui.QBrush(QtGui.QColor(0, 150, 255))
        qp.setBrush(brush)
        i = 0
        for bar in self.bars:
            qp.drawRect(i * bar_width, h - bar * h_scale, bar_width, h)
            i += 1


class VerticalSeparator(QtGui.QWidget):

    def __init__(self):
        super(VerticalSeparator, self).__init__()

        self.initUI()

    def initUI(self):
        self.setMinimumSize(1, 1)
        self.setMaximumWidth(1)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawLine(qp)
        qp.end()

    def drawLine(self, qp):
        # calculate size of histogram from available space
        size = self.size()
        w = size.width()
        h = size.height()

        pen = QtGui.QPen(QtGui.QColor(100, 100, 100), 1)
        qp.setPen(pen)
        qp.drawLine(w / 2, 0, w / 2, h)


class HorizontalSeparator(QtGui.QWidget):

    def __init__(self):
        super(HorizontalSeparator, self).__init__()

        self.initUI()

    def initUI(self):
        self.setMinimumSize(1, 1)
        self.setMaximumHeight(1)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawLine(qp)
        qp.end()

    def drawLine(self, qp):
        # calculate size of histogram from available space
        size = self.size()
        w = size.width()
        h = size.height()

        pen = QtGui.QPen(QtGui.QColor(100, 100, 100), 1)
        qp.setPen(pen)
        qp.drawLine(0, h / 2, w, h / 2)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, layout, screen_res):
        super(MainWindow, self).__init__()

        self.screen_res = screen_res
        self.clock_type = 'default'

    def initUI(self):
        self.mainWidgit = GUI(self, kconfig.key_chars, self.screen_res)
        self.mainWidgit.initUI()
        self.setCentralWidget(self.mainWidgit)

        # File Menu Actions
        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        # View Menu Actions
        defaultClockAction = QtGui.QAction('&Default (Clock)', self)
        defaultClockAction.setStatusTip('Regular Nomon clock with sweeping minute hand')
        defaultClockAction.triggered.connect(lambda: self.clockChangeEvent('default'))

        radarClockAction = QtGui.QAction('&Radar (Clock)', self)
        radarClockAction.setStatusTip('Nomon clock with sweeping minute hand and radar trails')
        radarClockAction.triggered.connect(lambda: self.clockChangeEvent('radar'))

        ballClockAction = QtGui.QAction('&Ball (Filling)', self)
        ballClockAction.setStatusTip('Expanding and contracting circle')
        ballClockAction.triggered.connect(lambda: self.clockChangeEvent('ball'))

        # Help Menu Actions
        helpAction = QtGui.QAction('&Help', self)
        helpAction.setStatusTip('Nomon help')
        helpAction.triggered.connect(self.helpEvent)

        aboutAction = QtGui.QAction('&About', self)
        aboutAction.setStatusTip('Application information')
        aboutAction.triggered.connect(self.aboutEvent)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        viewMenu = menubar.addMenu('&View')
        clockMenu = viewMenu.addMenu('&Clocks')
        clockMenu.addAction(defaultClockAction)
        clockMenu.addAction(radarClockAction)
        clockMenu.addAction(ballClockAction)

        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(helpAction)
        helpMenu.addSeparator()
        helpMenu.addAction(aboutAction)

        self.setWindowTitle('Nomon Keyboard')
        icon = QtGui.QIcon('nomon.png')
        self.setWindowIcon(icon)
        self.setGeometry(self.screen_res[0] * 0.05, self.screen_res[1] * 0.0675, self.screen_res[0] * 0.9,
                         self.screen_res[1] * 0.85)
        self.show()

    def clockChangeEvent(self, design):
        design = design.replace('_', ' ')
        messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, "Change Clock Design", "This will change the clocks "
                                                                                         "to the <b>" + design + "</b> design",
                                       QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
        messageBox.setDefaultButton(QtGui.QMessageBox.Cancel)
        messageBox.setIconPixmap(QtGui.QPixmap(design + '.png'))

        reply = messageBox.exec_()
        if reply == QtGui.QMessageBox.Ok:
            self.clock_type = design

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
        QtGui.QMessageBox.question(self, 'Help', "This is the Nomon Keyboard. To select an option, \n "
                                                 "find the clock immediately to its left. Press the \n"
                                                 "spacebar when the moving hand is near noon.\n\n"
                                                 "Alternative clock designs are located under View",
                                   QtGui.QMessageBox.Ok)


class GUI(QtGui.QWidget):

    def __init__(self, parent, layout, screen_res):
        super(GUI, self).__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.parent = parent
        self.layout = layout
        self.screen_res = screen_res
        self.size_factor = min(self.screen_res) / 1080.

    def initUI(self):

        # generate slider for clock rotation speed
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setRange(config.scale_min, config.scale_max)
        self.sld.setValue(config.start_speed)
        self.sldText = QtGui.QLabel('Clock Rotation Speed:')

        font = QtGui.QFont('consolas', 16)
        font.setStretch(80)
        font.setBold(True)
        # QtGui.QFont.Helvetica

        self.sldText.setFont(font)
        self.sldLabel = QtGui.QLabel(str(self.sld.value()))
        self.sldLabel.setFont(font)

        # generate learn, speak, talk checkboxes
        self.cb_talk = QtGui.QCheckBox('Talk', self)
        self.cb_learn = QtGui.QCheckBox('Learn', self)
        self.cb_pause = QtGui.QCheckBox('Pause', self)
        self.cb_talk.toggle()
        self.cb_talk.setFont(font)
        self.cb_learn.toggle()
        self.cb_learn.setFont(font)
        self.cb_pause.toggle()
        self.cb_pause.setFont(font)

        # generate clocks from layout
        self.generate_clocks()

        self.text_box = QtGui.QTextEdit("", self)
        text_box_font = QtGui.QFont('Consolas', 20)
        text_box_font.setStretch(90)
        self.text_box.setFont(text_box_font)
        self.text_box.setMinimumSize(300, 100)
        self.text_box.setReadOnly(True)

        # generate histogram
        self.histogram = HistogramWidget(self)

        if __name__ != '__main__':
            self.sld.valueChanged[int].connect(self.changeValue)
            self.cb_learn.toggled[bool].connect(self.parent.toggle_learn_button)
            self.cb_pause.toggled[bool].connect(self.parent.toggle_pause_button)
            self.cb_talk.toggled[bool].connect(self.parent.toggle_talk_button)

        # layout slider and checkboxes
        top_hbox = QtGui.QHBoxLayout()
        top_hbox.addWidget(self.sldText, 1)
        top_hbox.addWidget(self.sld, 16)
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
        self.vbox.addWidget(HorizontalSeparator())

        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.text_box)
        splitter1.addWidget(self.histogram)
        splitter1.setSizes([1, 1])
        self.histogram.setMaximumHeight(160 * self.size_factor)
        self.text_box.setMaximumHeight(160 * self.size_factor)

        self.vbox.addSpacing(5)
        self.vbox.addWidget(splitter1,1)
        self.layoutClocks(first_time=True)
        self.setLayout(self.vbox)

        if __name__ != '__main__':
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
        self.sldText.setToolTip("This slider scales the speed of clock rotation. Higher \n"
                                "values correspond to the clock hand moving faster.")
        self.sld.setToolTip("This slider scales the speed of clock rotation. Higher \n"
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

    def changeValue(self, value):
        self.sldLabel.setText(str(self.sld.value()))
        self.parent.change_speed(value)

    def getWords(self, char):
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

    def generate_clocks(self):
        self.clocks = []
        for row in self.layout:
            for text in row:
                clock = ClockWidgit(text, self)
                words = self.getWords(clock.text.lower())
                wordClocks = ['' for i in range(kconfig.N_pred)]
                i = 0
                for word in words:
                    wordClocks[i] = ClockWidgit(word, self, char_clock=False)
                    i += 1
                self.clocks += wordClocks
                self.clocks += [clock]

    def layoutClocks(self, first_time=False):
        # layout keyboard in grid
        self.keyboard_grid = QtGui.QGridLayout()
        clock_index = 0
        for row in range(len(self.layout)):
            self.keyboard_grid.addWidget(VerticalSeparator(), row * 2, 0)
            for key in range(len(self.layout[row])):
                if self.layout[row][key] in string.ascii_letters + kconfig.space_char:
                    key_grid = QtGui.QGridLayout()
                    key_grid.addWidget(self.clocks[clock_index + kconfig.N_pred], 0, 0, kconfig.N_pred, 1)
                    for i in range(kconfig.N_pred):
                        if isinstance(self.clocks[clock_index + i], ClockWidgit):
                            key_grid.addWidget(self.clocks[clock_index + i], i, 1)
                        else:
                            key_grid.addWidget(ClockFiller(self), i, 1)
                    key_grid.setColumnMinimumWidth(0, self.clocks[clock_index + kconfig.N_pred].minSize * 3)

                    key_grid.setColumnStretch(0, 1)
                    key_grid.setColumnStretch(1, 3)
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
                        self.keyboard_grid.addWidget(self.clocks[clock_index + kconfig.N_pred], row * 2, key * 2 + 1)
                self.keyboard_grid.addWidget(VerticalSeparator(), row * 2, key * 2 + 2)
                self.keyboard_grid.addWidget(HorizontalSeparator(), row * 2 + 1, key * 2 + 1)

                clock_index += kconfig.N_pred + 1
            self.keyboard_grid.setRowStretch(row * 2, 1)

        if first_time == True:
            self.clock_vboxes = []
            self.clock_vboxes += [QtGui.QVBoxLayout()]
            self.clock_vboxes[-1].insertLayout(2, self.keyboard_grid)

            self.vbox.insertLayout(2, self.clock_vboxes[-1], 6)

    def remove_clocks(self):

        self.generate_clocks()
        self.layoutClocks()
        self.clock_vboxes = [QtGui.QVBoxLayout()] + self.clock_vboxes

        self.clock_vboxes[0].insertLayout(2, self.keyboard_grid)

        self.vbox.insertLayout(2, self.clock_vboxes[0], 6)
        self.clearLayout(self.clock_vboxes[-1])
        self.clock_vboxes = [self.clock_vboxes[0]]
        self.parent.highlight_winner(self.parent.previous_winner)

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())


def main():
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
