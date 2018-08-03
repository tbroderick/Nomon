from widgets import *
import sys
from PyQt4 import QtCore, QtGui


class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.clock_type = 'default'
        self.high_contrast = False
        self.show()
        self.initUI()

    def initUI(self):

        self.MainWidget = MainWidget(self)
        self.setCentralWidget(self.MainWidget)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.increment)
        self.timer.start(50)
        self.setGeometry(200, 200, 400, 100)

    def increment(self):
        self.MainWidget.clock1.angle += 0.2
        self.MainWidget.clock1.repaint()
        self.MainWidget.clock2.angle += 0.2
        self.MainWidget.clock2.repaint()
        self.timer.start(50)

class MainWidget(QtGui.QWidget):

    def __init__(self, parent):
        super(MainWidget, self).__init__()

        self.parent = parent
        self.size_factor = 1.0
        self.alignment = 'cr'
        self.initUI()

    def initUI(self):

        hbox = QtGui.QHBoxLayout()
        self.clock1 = ClockWidgit("text", self)
        self.clock2 = ClockWidgit("texting", self)
        self.clock2.highlighted = True
        hbox.addWidget(self.clock1, 1)
        hbox.addWidget(self.clock2, 1)
        self.setLayout(hbox)
        self.show()


class Wrapper(Window):

    def __init__(self):
        super(Wrapper, self).__init__()

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Wrapper()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
