import sys
import math
import random
import string
import config
import kconfig
from PyQt4 import QtGui, QtCore


class ClockWidgit(QtGui.QWidget):

    def __init__(self, text, parent, char_clock = True):
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
        self.scaling_factor = round((len(self.text) + 2) / 1.7, 6)
        self.minSize = round(35*self.size_factor)
        self.maxSize = round(50*self.size_factor)
        # self.setMaximumSize(self.maxSize, self.maxSize)\
        self.setMinimumSize(self.minSize * self.scaling_factor, self.minSize)
        self.setMaximumHeight(self.maxSize)
        self.setBaseSize(self.minSize * self.scaling_factor, self.minSize)

        self.angle = 0

    def setAngle(self, angle):

        self.angle = angle

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawClock(e, qp)
        qp.end()

    def drawClock(self, e, qp):

        def clock_color(color_factor):
            if self.selected:
                pen.setColor(QtGui.QColor(255 * color_factor, 255, 255 * color_factor))
                qp.setPen(pen)
            elif self.highlighted:
                pen.setColor(QtGui.QColor(255*color_factor,255*color_factor,255))
                qp.setPen(pen)
            else:
                pen.setColor(QtGui.QColor(255 * (color_factor), 255 * (color_factor), 255 * (color_factor)))
                qp.setPen(pen)

        def hour_hand_from_angle(angle, radius):
            angle -= math.pi/2  # reference angle from noon
            far_point = center+QtCore.QPointF(math.cos(angle)*radius, math.sin(angle)*radius)
            qp.drawLine(center, far_point)

        def hand_from_angle(angle, radius):
            angle -= math.pi/2  # reference angle from noon
            for inc_angle in range(int(math.pi*7)+1):
                color_factor = min(float(inc_angle)/float(math.pi*7), 1)
                clock_color(color_factor)
                far_point = center+QtCore.QPointF(math.cos(angle+(1-inc_angle)/7.)*radius, math.sin(angle+(1-inc_angle)/7.)*radius)
                qp.drawLine(center, far_point)
            far_point = center + QtCore.QPointF(math.cos(angle) * radius, math.sin(angle) * radius)

            if self.selected:
                pen.setColor(QtGui.QColor(20, 245, 20))

            elif self.highlighted:
                pen.setColor(QtGui.QColor(0, 0, 255))
            else:
                pen.setColor(QtGui.QColor(0, 0, 0))
            qp.setPen(pen)

        # calculate size of clock from available space
        size = self.size()
        w = size.width()
        h = size.height()
        constraint = h
        clock_rad = constraint/2
        clock_thickness = 1./6
        center = QtCore.QPointF(constraint / 2, constraint / 2)

        # draw clock face
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        if self.highlighted:
            pen = QtGui.QPen(QtGui.QColor(0, 0, 255))
        if self.selected:
            pen = QtGui.QPen(QtGui.QColor(20, 229, 20))
        qp.setPen(pen)
        qp.setBrush(brush)

        qp.drawEllipse(center, clock_rad*(1-clock_thickness/2), clock_rad*(1-clock_thickness/2))

        # draw hands
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0), clock_rad * clock_thickness)
        if self.highlighted:
            pen = QtGui.QPen(QtGui.QColor(0, 0, 255), clock_rad * clock_thickness)
        if self.selected:
            pen = QtGui.QPen(QtGui.QColor(	20, 229, 20), clock_rad * clock_thickness)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        qp.setPen(pen)

        hand_from_angle(self.angle + self.start_angle, clock_rad * 0.825)  # Minute Hand
        pen.setWidth(3)
        qp.setPen(pen)
        hour_hand_from_angle(0, clock_rad * 0.85)  # Hour hand

        # draw text
        qp.setPen(QtGui.QColor(0, 0, 0))
        if self.highlighted:
            qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setFont(QtGui.QFont('Monospace', clock_rad))
        qp.drawText(center.x()+clock_rad,center.y()+clock_rad*.6, self.text)


class HistogramWidget(QtGui.QWidget):

    def __init__(self, parent):
        super(HistogramWidget, self).__init__()
        self.parent = parent
        self.bars = parent.bars
        self.initUI()


    def initUI(self):
        self.setMinimumSize(200, 100)

    def paintEvent(self, e):
        print("repainting")
        qp = QtGui.QPainter()
        qp.begin(self)
        self.bars = self.parent.bars
        self.drawBars(qp)
        qp.end()

    def drawBars(self, qp):
        # calculate size of histogram from available space
        size = self.size()
        w = size.width()
        h = size.height()

        max_value = max(self.bars)
        h_scale = h/max_value
        bar_width = float(w)/len(self.bars)

        qp.setPen(QtGui.QPen(QtGui.QColor(120, 120, 120), 1))
        qp.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        qp.drawRect(0, 0, w-1, h)

        pen = QtGui.QPen(QtGui.QColor(0, 0, 255),1)
        qp.setPen(pen)
        brush = QtGui.QBrush(QtGui.QColor(0, 150, 255))
        qp.setBrush(brush)
        i = 0
        for bar in self.bars:
            qp.drawRect(i*bar_width, h-bar*h_scale, bar_width, h)
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

        pen = QtGui.QPen(QtGui.QColor(100,100,100),1)
        qp.setPen(pen)
        qp.drawLine(w/2, 0, w/2, h)


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

        pen = QtGui.QPen(QtGui.QColor(100, 100, 100),1)
        qp.setPen(pen)
        qp.drawLine(0, h/2, w, h/2)


class GUI(QtGui.QWidget):

    def __init__(self, layout, screen_res):
        super(GUI, self).__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.layout = layout
        self.screen_res = screen_res
        self.size_factor = min(self.screen_res) / 1080.


    def initUI(self):

        # generate slider for clock rotation speed
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setRange(config.scale_min, config.scale_max)
        self.sld.setValue(config.start_speed)
        self.sldText = QtGui.QLabel('Clock Rotation Speed:')
        self.sldText.setFont(QtGui.QFont('Monospace', 12))
        self.sldLabel = QtGui.QLabel(str(self.sld.value()))
        self.sldLabel.setFont(QtGui.QFont('Monospace', 14))

        # generate learn, speak, talk checkboxes
        self.cb_talk = QtGui.QCheckBox('Talk', self)
        self.cb_learn = QtGui.QCheckBox('Learn', self)
        self.cb_pause = QtGui.QCheckBox('Pause', self)
        self.cb_talk.toggle()
        self.cb_talk.setFont(QtGui.QFont('Monospace', 12))
        self.cb_learn.toggle()
        self.cb_learn.setFont(QtGui.QFont('Monospace', 12))
        self.cb_pause.toggle()
        self.cb_pause.setFont(QtGui.QFont('Monospace', 12))

        # generate clocks from layout
        self.generate_clocks()

        self.text_box = QtGui.QTextEdit("",self)
        self.text_box.setFont(QtGui.QFont('Monospace', 25))
        self.text_box.setMinimumSize(300, 100)
        self.text_box.setReadOnly(True)

        # generate histogram
        self.histogram = HistogramWidget(self)

        if __name__ != '__main__':
            self.sld.valueChanged[int].connect(self.changeValue)
            self.cb_learn.toggled[bool].connect(self.toggle_learn_button)
            self.cb_pause.toggled[bool].connect(self.toggle_pause_button)
            self.cb_talk.toggled[bool].connect(self.toggle_talk_button)

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
        self.histogram.setMaximumHeight(150*self.size_factor)
        self.text_box.setMaximumHeight(150*self.size_factor)

        self.vbox.addSpacing(5)
        self.vbox.addWidget(splitter1)
        self.layoutClocks(first_time=True)
        self.setLayout(self.vbox)

        if __name__ != '__main__':

            self.frame_timer = QtCore.QTimer()
            self.frame_timer.timeout.connect(self.on_timer)
            self.frame_timer.start(config.ideal_wait_s*1000)

            self.pause_timer = QtCore.QTimer()
            self.pause_timer.setSingleShot(True)
            self.pause_timer.timeout.connect(self.end_pause)

            self.highlight_timer = QtCore.QTimer()
            self.highlight_timer.setSingleShot(True)
            self.highlight_timer.timeout.connect(self.end_highlight)


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

        self.setWindowTitle('Nomon Keyboard')
        self.setWindowIcon(QtGui.QIcon('nomon.ico'))
        self.setGeometry(self.screen_res[0]*0.05, self.screen_res[1]*0.0675, self.screen_res[0]*0.9, self.screen_res[1]*0.85)
        self.show()

    def changeValue(self, value):
        self.sldLabel.setText(str(self.sld.value()))
        self.change_speed(value)

    def getWords(self, char):
        i = 0
        output = []
        for word in self.word_list:
            index = len(self.prefix)
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
                i=0
                for word in words:
                    wordClocks[i] = ClockWidgit(word, self, char_clock=False)
                    i += 1
                self.clocks += wordClocks
                self.clocks += [clock]

    def layoutClocks(self, first_time=False):
        # layout keyboard in grid
        self.keyboard_rows = []
        clock_index = 0
        for row in range(len(self.layout)):
            keyboard_row = QtGui.QHBoxLayout()
            for key in range(len(self.layout[row])):
                if self.layout[row][key] in string.ascii_letters + kconfig.space_char:
                    key_grid = QtGui.QGridLayout()
                    key_grid.addWidget(self.clocks[clock_index+kconfig.N_pred], 0, 0, kconfig.N_pred, 1)
                    for i in range(kconfig.N_pred):
                        if isinstance(self.clocks[clock_index + i],ClockWidgit):
                            key_grid.addWidget(self.clocks[clock_index + i], i, 1)

                    key_grid.setColumnMinimumWidth(0,self.clocks[clock_index+kconfig.N_pred].minSize*3)

                    key_grid.setColumnStretch(0, 1)
                    key_grid.setColumnStretch(1, 3)

                    keyboard_row.addWidget(VerticalSeparator())
                    keyboard_row.addLayout(key_grid,1)

                else:
                    keyboard_row.addWidget(VerticalSeparator())
                    clock = self.clocks[clock_index+kconfig.N_pred]
                    if clock.text == kconfig.mybad_char:  # check if UNDO clock
                        self.undo_label = QtGui.QLabel(self.previous_undo_text)
                        undo_font = QtGui.QFont('Monospace', 20)
                        self.undo_label.setFont(undo_font)

                        undo_hbox = QtGui.QVBoxLayout()
                        undo_hbox.addWidget(self.clocks[clock_index+kconfig.N_pred])
                        undo_hbox.addWidget(self.undo_label)
                        keyboard_row.addLayout(undo_hbox,1)
                    else:
                        keyboard_row.addWidget(self.clocks[clock_index+kconfig.N_pred], 1)

                clock_index += kconfig.N_pred + 1

            keyboard_row.addWidget(VerticalSeparator())
            self.keyboard_rows += [keyboard_row]

        if first_time == True:
            self.clock_vboxes = []
            self.clock_vboxes += [QtGui.QVBoxLayout()]
            i=0
            for row in self.keyboard_rows:
                self.clock_vboxes[-1].insertLayout(2+i, row)
                self.clock_vboxes[-1].insertWidget(3+i, HorizontalSeparator())
                i += 2
            self.vbox.insertLayout(2, self.clock_vboxes[-1])

    def remove_clocks(self):

        self.generate_clocks()
        self.layoutClocks()
        self.clock_vboxes = [QtGui.QVBoxLayout()]+self.clock_vboxes
        i=0
        for row in self.keyboard_rows:
            self.clock_vboxes[0].insertLayout(2 + i, row)
            self.clock_vboxes[0].insertWidget(3 + i, HorizontalSeparator())
            i += 2
        self.vbox.insertLayout(2, self.clock_vboxes[0])
        self.clearLayout(self.clock_vboxes[-1])
        self.clock_vboxes = [self.clock_vboxes[0]]
        self.highlight_winner(self.previous_winner)



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
    ex = GUI(kconfig.key_chars, screen_res)
    word_list = open('word_list.txt', 'r')
    words = word_list.read()
    words = words.split()
    word_list.close()
    ex.word_list = []
    for letter in string.ascii_lowercase:
        i=0
        for word in words:
            if word[0] == letter and i < kconfig.N_pred:
                i += 1
                ex.word_list += [word]
    ex.prefix = ''
    ex.bars = kconfig.bars
    ex.previous_undo_text = 'sss'

    ex.initUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()