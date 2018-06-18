import sys
import math
import random
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

# get frequent words
wordListFile = open('word_list.txt', 'r')
wordList = wordListFile.read().split()
print(wordList)
wordListFile.close()
# wordList = 'and_ a_ as_ be_ by_ but_ can_ could_ do_ did_ down_ for_ from_ first_ get_ he_ have_ had_ in_ it_ is_ just_ know_ like_ more_ my_ me_ not_ no_ now_ of_ on_ or_ people_ she_ so_ said_ the_ to_ that_ up_ very_ was_ with_ which_ you_ your_ '
# wordList=wordList.split()
wordDisplayCount = 2

# get gaussian distribution
bars = [4.1731209137640166e-11, 1.5674042704727563e-10, 5.702330790217924e-10, 2.009440319647259e-09, 6.858815826469396e-09, 2.2676420114286876e-08, 7.261915168381362e-08, 2.2525745454100865e-07, 6.767971122297686e-07, 1.969650386894775e-06, 5.552276918629734e-06, 1.5160181992883207e-05, 4.009489083361327e-05, 0.00010271289727370694, 0.0002548662025258791, 0.0006125631118014535, 0.001426069713163289, 0.0032157479134091965, 0.007023839199846974, 0.01485998764716699, 0.03045184848219981, 0.0604449741201335, 0.11621389459417346, 0.21642490682430432, 0.3903981461621635, 0.6821181069890906, 1.1544170528966142, 1.8924186208565767, 3.0048515131831763, 4.621470051256386, 6.884756647011963, 9.934553867306171, 13.88543429703574, 18.798443462933843, 24.65106218552027, 31.31127178097519, 38.52273404437159, 45.90762451643071, 52.99121328326851, 59.2480729571828, 64.16466330246335, 67.30834836361127, 68.39010521167417, 67.30834836361129, 64.16466330246332, 59.2480729571828, 52.99121328326855, 45.90762451643069, 38.52273404437159, 31.311271780975158, 24.65106218552027, 18.79844346293387, 13.885434297035717, 9.934553867306171, 6.884756647011954, 4.621470051256386, 3.0048515131831834, 1.8924186208565716, 1.1544170528966142, 0.6821181069890888, 0.3903981461621635, 0.21642490682430507, 0.11621389459417325, 0.06044497412013371, 0.03045184848219981, 0.014859987647167044, 0.007023839199847036, 0.0032157479134091965, 0.0014260697131632965, 0.0006125631118014535, 0.00025486620252588053, 0.00010271289727370786, 4.009489083361327e-05, 1.5160181992883289e-05, 5.552276918629734e-06, 1.969650386894789e-06, 6.767971122297759e-07, 2.2525745454100865e-07, 7.261915168381387e-08, 2.2676420114286876e-08]


class ClockWidgit(QtGui.QWidget):

    def __init__(self, text, start_angle, char_clock = True, highlighted = False):
        super(ClockWidgit, self).__init__()

        self.text = text
        self.start_angle = start_angle
        self.char_clock = char_clock
        self.highlighted = highlighted
        self.initUI()

    def initUI(self):
        self.scaling_factor = ((len(self.text) + 2) / 1.8)
        print(self.scaling_factor)
        minSize = 55
        maxSize = 80
        if self.char_clock == False:
            minSize = 29
            if wordDisplayCount == 3:
                minSize = 20
            maxSize = 40
        self.setMinimumSize(minSize * self.scaling_factor, minSize)
        self.setMaximumSize(maxSize * self.scaling_factor, maxSize)
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
        qp.setPen(pen)
        qp.setBrush(brush)

        qp.drawEllipse(center, clock_rad*(1-clock_thickness/2), clock_rad*(1-clock_thickness/2))

        # draw hands
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0), clock_rad * clock_thickness)
        if self.highlighted:
            pen = QtGui.QPen(QtGui.QColor(0, 0, 255), clock_rad * clock_thickness)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        qp.setPen(pen)

        hand_from_angle(0, clock_rad * 0.4)  # Hour hand
        hand_from_angle(self.angle+self.start_angle, clock_rad * 0.7)  # Minute Hand

        # draw text
        qp.setPen(QtGui.QColor(0, 0, 0))
        if self.highlighted:
            qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setFont(QtGui.QFont('Monospace', clock_rad*1.5))
        qp.drawText(center.x()+clock_rad,center.y()+clock_rad*.75, self.text)


class HistogramWidget(QtGui.QWidget):

    def __init__(self, bars):
        super(HistogramWidget, self).__init__()

        self.bars = bars
        self.initUI()

    def initUI(self):
        self.setMinimumSize(200, 100)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
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


class Keyboard(QtGui.QWidget):

    def __init__(self, layout):
        super(Keyboard, self).__init__()

        self.layout = layout
        self.initUI()

    def initUI(self):

        # generate slider for clock rotation speed
        self.sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setRange(1, 24)
        self.sld.setValue(5)
        self.sldText = QtGui.QLabel('Adjust Clock Rotation Speed:')
        self.sldText.setFont(QtGui.QFont('Monospace', 10))
        self.sldLabel = QtGui.QLabel(str(self.sld.value()))
        self.sldLabel.setFont(QtGui.QFont('Monospace', 12))

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
        self.clock_rows=[]
        self.clocks=[]
        for row in self.layout:
            self.clocks = []
            for text in row:
                clock = ClockWidgit(text, random.random()*math.pi*2, highlighted=bool(round(random.random()+0.25)))
                self.clocks += [clock]
                words = self.getWords(clock.text.lower())
                if len(words) > 0:
                    wordClocks = []
                    for word in words:
                        wordClocks += [ClockWidgit(word, random.random()*math.pi*2,char_clock=False, highlighted=bool(round(random.random()+0.25)) )]
                    self.clocks += [wordClocks]


            self.clock_rows += [self.clocks]

        self.text_box = QtGui.QTextEdit("text_outputs_here",self)
        self.text_box.setFont(QtGui.QFont('Monospace', 25))
        self.text_box.setMinimumSize(300, 100)

        # generate histogram
        self.histogram = HistogramWidget(bars)

        self.sld.valueChanged[int].connect(self.changeValue)

        # initialize timer for clock rotation
        self.timer = QtCore.QBasicTimer()
        self.timer.start((1-self.sld.value()/24.)*25+5, self)
        self.step = 0

        # layout rows of keyboard
        hboxes = []

        for row in self.clock_rows:
            hbox = QtGui.QHBoxLayout()
            i = 0
            for clock in row:

                if isinstance(clock, list):
                    if len(clock) > 1:
                        wordClock_vbox = QtGui.QVBoxLayout()
                        for wordClock in clock:
                            wordClock_vbox.addWidget(wordClock)  # multiply by LCM of [1,7] to make integers
                        hbox.addLayout(wordClock_vbox, 1)

                    else:
                        hbox.addWidget(clock[0], clock[0].scaling_factor*420)

                else:
                    hbox.addStretch(1)
                    if i != 0:
                        hbox.addWidget(VerticalSeparator())
                    hbox.addWidget(clock, clock.scaling_factor*420)  # multiply by LCM of [1,7] to make integers
                i += 1
            hbox.addStretch(1)
            hboxes += [hbox]


        # layout slider and checkboxes
        top_hbox = QtGui.QHBoxLayout()
        top_hbox.addWidget(self.sldText)
        top_hbox.addWidget(self.sld,4)
        top_hbox.addWidget(self.sldLabel)
        top_hbox.addStretch(1)
        top_hbox.addWidget(self.cb_talk)
        top_hbox.addWidget(self.cb_learn)
        top_hbox.addWidget(self.cb_pause)
        top_hbox.addStretch(1)

        # stack layouts vertically
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(top_hbox,1)
        vbox.addWidget(HorizontalSeparator())
        for hbox in hboxes:
            vbox.addLayout(hbox,1)
            vbox.addWidget(HorizontalSeparator())

        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(self.text_box)
        splitter1.addWidget(self.histogram)
        splitter1.setSizes([1, 1])

        vbox.addWidget(splitter1,1)

        self.setLayout(vbox)
        self.setWindowTitle('Nomon Keyboard')
        self.setWindowIcon(QtGui.QIcon('nomon.ico'))
        self.show()

    def timerEvent(self, e):

        if self.step >= math.pi*2:
            self.step = 0
            return

        self.step = self.step + math.pi/50
        for row in self.clock_rows:
            for clock in row:
                if isinstance(clock, list):
                    for wordClock in clock:
                        wordClock.setAngle(self.step)
                        wordClock.repaint()
                else:
                    clock.setAngle(self.step)
                    clock.repaint()

    def changeValue(self, value):
        self.timer.start((1-value/24.)*25+5, self)
        self.sldLabel.setText(str(self.sld.value()))

    def getWords(self, char):
        i = 0
        output = []
        for word in wordList:
            if word[0] == char:
                i += 1
                if i > wordDisplayCount:
                    break
                output += [word]

        return output











def main():
    app = QtGui.QApplication(sys.argv)
    ex = Keyboard(key_chars)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()