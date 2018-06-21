import sys
import math
import random
import config
from PyQt4 import QtGui, QtCore

space_char = '_'
mybad_char = 'Undo'
break_char = '.'
back_char = 'Delete'
# alphabetic
# always put alpha-numeric keys first (self.N_alpha_keys)
key_chars = [	['A','B','C','D','E'],
		        ['F','G','H','I','J'],
		        ['K','L','M','N','O'],
		        ['P','Q','R','S','T'],
		        ['U','V','W','X','Y'],
		['Z',space_char,break_char,back_char,mybad_char]
		    ]

# key_chars = [	['q','w','e','r','t','y','u','i','o','p'],
# 		['a','s','d','f','g','h','j','k','l','\''],
# 		['z','x','c','v','b','n','m',',','.','?'],
# 		[space_char, mybad_char]
# 		]

wordDisplayCount = 3

# get gaussian distribution
bars = [4.1731209137640166e-11, 1.5674042704727563e-10, 5.702330790217924e-10, 2.009440319647259e-09, 6.858815826469396e-09, 2.2676420114286876e-08, 7.261915168381362e-08, 2.2525745454100865e-07, 6.767971122297686e-07, 1.969650386894775e-06, 5.552276918629734e-06, 1.5160181992883207e-05, 4.009489083361327e-05, 0.00010271289727370694, 0.0002548662025258791, 0.0006125631118014535, 0.001426069713163289, 0.0032157479134091965, 0.007023839199846974, 0.01485998764716699, 0.03045184848219981, 0.0604449741201335, 0.11621389459417346, 0.21642490682430432, 0.3903981461621635, 0.6821181069890906, 1.1544170528966142, 1.8924186208565767, 3.0048515131831763, 4.621470051256386, 6.884756647011963, 9.934553867306171, 13.88543429703574, 18.798443462933843, 24.65106218552027, 31.31127178097519, 38.52273404437159, 45.90762451643071, 52.99121328326851, 59.2480729571828, 64.16466330246335, 67.30834836361127, 68.39010521167417, 67.30834836361129, 64.16466330246332, 59.2480729571828, 52.99121328326855, 45.90762451643069, 38.52273404437159, 31.311271780975158, 24.65106218552027, 18.79844346293387, 13.885434297035717, 9.934553867306171, 6.884756647011954, 4.621470051256386, 3.0048515131831834, 1.8924186208565716, 1.1544170528966142, 0.6821181069890888, 0.3903981461621635, 0.21642490682430507, 0.11621389459417325, 0.06044497412013371, 0.03045184848219981, 0.014859987647167044, 0.007023839199847036, 0.0032157479134091965, 0.0014260697131632965, 0.0006125631118014535, 0.00025486620252588053, 0.00010271289727370786, 4.009489083361327e-05, 1.5160181992883289e-05, 5.552276918629734e-06, 1.969650386894789e-06, 6.767971122297759e-07, 2.2525745454100865e-07, 7.261915168381387e-08, 2.2676420114286876e-08]


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
        minSize = round(90*self.size_factor)
        maxSize = round(120*self.size_factor)
        if self.char_clock == False:
            minSize = round(40*self.size_factor)
            maxSize = round(50*self.size_factor)
        self.setMaximumSize(maxSize * self.scaling_factor, maxSize)
        self.setMinimumSize(minSize * self.scaling_factor, minSize)

        self.angle = 0

    def setAngle(self, angle):

        self.angle = angle

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawClock(e, qp)
        qp.end()

    def drawClock(self, e, qp):

        def hand_from_angle(angle, radius):
            angle -= math.pi/2  # reference angle from noon

            far_point = center+QtCore.QPointF(math.cos(angle)*radius, math.sin(angle)*radius)
            qp.drawLine(center, far_point)

        # calculate size of clock from available space
        size = self.size()
        w = size.width()
        h = size.height()
        constraint = min((w/(len(self.text)+2)*1.6), h)
        clock_rad = constraint/2
        clock_thickness = 1./6
        center = QtCore.QPointF(constraint / 2, constraint / 2)

        # draw clock face
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        if self.highlighted:
            pen = QtGui.QPen(QtGui.QColor(0, 0, 255))
        if self.selected:
            pen = QtGui.QPen(QtGui.QColor(0, 255, 0))
        qp.setPen(pen)
        qp.setBrush(brush)

        qp.drawEllipse(center, clock_rad*(1-clock_thickness/2), clock_rad*(1-clock_thickness/2))

        # draw hands
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0), clock_rad * clock_thickness)
        if self.highlighted:
            pen = QtGui.QPen(QtGui.QColor(0, 0, 255), clock_rad * clock_thickness)
        if self.selected:
            pen = QtGui.QPen(QtGui.QColor(0, 255, 0), clock_rad * clock_thickness)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        qp.setPen(pen)

        hand_from_angle(0, clock_rad * 0.4)  # Hour hand
        hand_from_angle(self.angle+self.start_angle, clock_rad * 0.7)  # Minute Hand

        # draw text
        qp.setPen(QtGui.QColor(0, 0, 0))
        if self.highlighted:
            qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setFont(QtGui.QFont('Monospace', clock_rad))
        qp.drawText(center.x()+clock_rad,center.y()+clock_rad*.75, self.text)


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

        self.bars = bars
        self.layout = layout
        self.screen_res = screen_res
        self.size_factor = min(self.screen_res) / 1080.


    def initUI(self):

        # generate slider for clock rotation speed
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setRange(config.scale_min, config.scale_max)
        self.sld.setValue(5)
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

        # generate histogram
        self.histogram = HistogramWidget(self)

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
        self.histogram.setMaximumHeight(120*self.size_factor)
        self.text_box.setMaximumHeight(120*self.size_factor)

        self.vbox.addWidget(splitter1)
        self.layoutClocks(first_time=True)
        self.setLayout(self.vbox)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(50)

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
        self.move(100, 50)
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
                if i > wordDisplayCount:
                    break
                output += [word]

        return output

    def generate_clocks(self):
        self.clocks = []
        for row in self.layout:
            for text in row:
                clock = ClockWidgit(text, self)
                words = self.getWords(clock.text.lower())
                wordClocks = ['','','']
                i=0
                for word in words:
                    wordClocks[i] = ClockWidgit(word, self, char_clock=False)
                    i += 1
                self.clocks += wordClocks
                self.clocks += [clock]

    def layoutClocks(self, first_time=False):
        # layout rows of keyboard
        self.hboxes = []
        layout_pos = 0
        layout_row = 0
        hbox = QtGui.QHBoxLayout()
        for clock_index in range(len(self.clocks)):
            if clock_index % 4 == 3:  # check if main character clock
                layout_pos += 1
                if layout_pos != 1:
                    hbox.addWidget(VerticalSeparator())
                hbox.addWidget(self.clocks[clock_index], self.clocks[clock_index].scaling_factor * 480)
                if self.clocks[clock_index-3] != '':  # check if char clock has word clocks
                    clock_index-=4
                    vbox = QtGui.QVBoxLayout()
                    for i in range(3):
                        clock_index += 1
                        if self.clocks[clock_index] != '':
                            vbox.addWidget(self.clocks[clock_index],self.clocks[clock_index].scaling_factor * 360)
                    hbox.addLayout(vbox, 480)
                hbox.addStretch(1)

            if layout_pos == len(self.layout[layout_row]):
                self.hboxes += [hbox]
                hbox = QtGui.QHBoxLayout()
                layout_pos = 0
                if layout_row < len(self.layout) - 1:
                    layout_row += 1



        if first_time == True:
            self.clock_vboxes = []
            self.clock_vboxes += [QtGui.QVBoxLayout()]
            for hbox in self.hboxes:
                self.clock_vboxes[-1].addLayout(hbox, 2)
                self.clock_vboxes[-1].addWidget(HorizontalSeparator())
            self.vbox.insertLayout(2, self.clock_vboxes[-1])

    def remove_clocks(self):

        self.generate_clocks()
        self.layoutClocks()
        self.clock_vboxes = [QtGui.QVBoxLayout()]+self.clock_vboxes
        for hbox in self.hboxes:
            self.clock_vboxes[0].addLayout(hbox, 2)
            self.clock_vboxes[0].addWidget(HorizontalSeparator())
        self.vbox.insertLayout(2, self.clock_vboxes[0])
        self.clearLayout(self.clock_vboxes[-1])
        self.clock_vboxes = [self.clock_vboxes[0]]



    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())



def main():
    app = QtGui.QApplication(sys.argv)
    ex = GUI(key_chars)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()