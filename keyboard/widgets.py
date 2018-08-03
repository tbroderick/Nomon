from __future__ import division
from PyQt4 import QtGui, QtCore
import math
import kconfig
from config import *


class ClockWidgit(QtGui.QWidget):

    def __init__(self, text, parent, filler_clock=False):
        super(ClockWidgit, self).__init__()

        self.text = text
        self.redraw_text = True
        self.start_angle = 0.
        self.parent = parent
        self.filler_clock = filler_clock  # filler clock is transparent, but saves space in layout for later use
        self.highlighted = False
        self.selected = False
        self.previous_angle = -360.  # used in pac-man clock to compare if hand passed noon (- to + angle)
        self.color_switch = False  # used in pac-man clock to alternate color fill
        self.dummy_angle_offset = 0.
        self.initUI()

        try:
            if self.parent.alignment[0] != 'c':
                self.constraint_factor = 0.5
            else:
                self.constraint_factor = 1
            self.radius = self.size().height() * self.constraint_factor / 2
        except:
            pass

    def initUI(self):

        self.size_factor = self.parent.size_factor
        self.minSize = round(40 * self.size_factor)
        self.maxSize = round(50 * self.size_factor)

        self.setMinimumSize(self.minSize, self.minSize)
        self.setMaximumHeight(self.maxSize)
        self.setBaseSize(self.minSize, self.minSize)

        self.angle = 0

    def setText(self, text):
        self.text = text
        self.redraw_text = True

    def setAngle(self, angle):
        self.angle = angle

    def paintEvent(self, e):

        qp = QtGui.QPainter()
        qp.begin(self)
        if not self.filler_clock:
            self.drawClock(e, qp)
        qp.end()
        self.redraw_text = False

    def drawClock(self, e, qp):

        if self.parent.parent.clock_type == 'ball':  # initialize functions for drawing "min hand" based on clock design
            def minute_hand_from_angle(angle, radius):
                radius *= 1.22
                if self.selected:
                    brush.setColor(ball_mh_selct_color)

                elif self.highlighted:
                    brush.setColor(ball_mh_highlt_color)
                else:
                    brush.setColor(ball_mh_reg_color)
                qp.setBrush(brush)
                pen.setColor(QtGui.QColor(0, 0, 0, 0))
                qp.setPen(pen)

                def sign(x):
                    if abs(x) == x:
                        return 1
                    return -1

                angle = (-angle+math.pi*sign(angle))/math.pi
                size_factor = angle

                qp.drawEllipse(center, radius * size_factor, radius * size_factor)

            hour_hand_from_angle = lambda x, y: x

        elif self.parent.parent.clock_type == 'radar':
            if self.parent.parent.high_contrast:
                def clock_color(color_factor):
                    if self.selected:
                        brush.setColor(QtGui.QColor(0, 255, 0, 255 * color_factor))
                        qp.setBrush(brush)
                    elif self.highlighted:
                        brush.setColor(QtGui.QColor(0, 0, 255, 255 * color_factor))
                        qp.setBrush(brush)
                    else:
                        brush.setColor(QtGui.QColor(255, 0, 0, 255 * color_factor))

                        qp.setBrush(brush)
            else:
                def clock_color(color_factor):
                    if self.selected:
                        brush.setColor(QtGui.QColor(0, 255, 0, 255 * color_factor))
                        qp.setBrush(brush)
                    elif self.highlighted:
                        brush.setColor(QtGui.QColor(0, 0, 255, 255 * color_factor))
                        qp.setBrush(brush)
                    else:
                        brush.setColor(QtGui.QColor(0, 0, 0, 255 * color_factor))
                        qp.setBrush(brush)

            def hour_hand_from_angle(angle, radius):
                pen.setColor(default_hh_color)
                pen.setWidth(2)
                qp.setPen(pen)

                angle -= math.pi / 2  # reference angle from noon
                radius *= 1.1
                far_point = center + QtCore.QPointF(math.cos(angle) * radius, math.sin(angle) * radius)
                qp.drawLine(center, far_point)

                if self.selected:
                    pen.setColor(default_selct_color)

                elif self.highlighted:
                    pen.setColor(default_highlt_color)
                else:
                    pen.setColor(default_reg_color)
                pen.setWidth(3)
                qp.setPen(pen)

            def minute_hand_from_angle(angle, radius):
                radius *= 1.2
                angle *= 180. / math.pi
                angle = 90 - angle
                if angle > 0:
                    angle = -360 + angle
                r = clock_rad * (1. - clock_thickness / 2)
                rect = QtCore.QRect(center.x() - r + 1, center.y() - r + 1, r * 2., r * 2.)

                n = 8.
                length = math.pi * 2 / 3
                pen.setColor(QtGui.QColor(0, 0, 0, 0))
                pen.setWidth(1)
                qp.setPen(pen)
                for i in range(int(n)):
                    color_factor = min(1. - float(i) / n, 1.)
                    inc_angle = float(i) * length / n
                    inc_angle = math.degrees(inc_angle)
                    clock_color(color_factor)
                    qp.drawPie(rect, (angle + inc_angle) * 16, (math.degrees(length / n) + 1) * 16)

                pen.setWidth(clock_rad * clock_thickness)
                qp.setPen(pen)

        elif self.parent.parent.clock_type == 'pac_man':
            def minute_hand_from_angle(angle, radius):
                angle *= 180. / math.pi
                angle = - angle
                if angle > 0:
                    angle = -360 + angle
                r = clock_rad * (1. - clock_thickness / 2)
                rect = QtCore.QRect(center.x() - r + 1, center.y() - r + 1, r * 2., r * 2.)

                if self.selected:
                    brush.setColor(pac_man_selct_color)

                elif self.highlighted:
                    brush.setColor(pac_man_highlt_color)
                else:
                    brush.setColor(pac_man_reg_color)
                qp.setBrush(brush)
                pen.setColor(QtGui.QColor(0, 0, 0, 0))
                qp.setPen(pen)

                if angle > self.previous_angle:
                    self.color_switch = self.color_switch == False

                if self.color_switch:
                    qp.drawEllipse(center, clock_rad * (1 - clock_thickness / 2), clock_rad * (1 - clock_thickness / 2))

                    brush.setColor(clock_bg_color)
                    qp.setBrush(brush)

                self.previous_angle = angle
                qp.drawPie(rect, 90 * 16, angle * 16)

            def hour_hand_from_angle(angle, radius):
                pass

        elif self.parent.parent.clock_type == 'bar':
            def minute_hand_from_angle(angle, radius):
                radius *= 1.22
                if self.selected:
                    brush.setColor(bar_mh_selct_color)

                elif self.highlighted:
                    brush.setColor(bar_mh_highlt_color)
                else:
                    brush.setColor(bar_mh_reg_color)
                qp.setBrush(brush)
                pen.setColor(QtGui.QColor(0, 0, 0, 0))
                qp.setPen(pen)

                def sign(x):
                    if abs(x) == x:
                        return 1
                    return -1

                angle = (-angle+math.pi*sign(angle))/math.pi

                qp.drawRect(10, 2, (w - 20) * abs(angle), h - 4)

            def hour_hand_from_angle(angle, radius):
                if self.selected:
                    pen.setColor(bar_hh_selct_color)

                elif self.highlighted:
                    pen.setColor(bar_hh_highlt_color)
                else:
                    pen.setColor(bar_hh_reg_color)
                pen.setWidth(4)
                qp.setPen(pen)
                qp.drawRect(10, 1, w - 20, h - 1)

        elif self.parent.parent.clock_type == 'default':

            def minute_hand_from_angle(angle, radius):

                angle -= math.pi / 2  # reference angle from noon

                far_point = center + QtCore.QPointF(math.cos(angle) * radius, math.sin(angle) * radius)
                qp.drawLine(center, far_point)

            def hour_hand_from_angle(angle, radius):
                pen.setColor(default_hh_color)
                pen.setWidth(2)
                qp.setPen(pen)

                minute_hand_from_angle(angle, radius * 1.1)

                if self.selected:
                    pen.setColor(default_selct_color)

                elif self.highlighted:
                    pen.setColor(default_highlt_color)
                else:
                    pen.setColor(default_reg_color)
                pen.setWidth(3)
                qp.setPen(pen)

        # calculate size of clock from available space
        size = self.size()
        w = size.width()
        h = size.height()
        if self.parent.alignment[0] != 'c':
            constraint_factor = 0.5
        else:
            constraint_factor = 1

        constraint = h * constraint_factor
        clock_rad = constraint / 2

        self.radius = clock_rad
        clock_thickness = 1. / 6

        # calculate size of text from leftover space
        if self.redraw_text:
            self.text_font = QtGui.QFont(clock_font)

            font_size = clock_rad * min(1., 1.2 * constraint_factor)
            self.text_font.setPointSize(font_size)
            self.text_font.setStretch(85)

            if self.parent.layout == kconfig.qwerty_key_chars:
                if self.text in sum(kconfig.qwerty_key_chars, []):
                    self.text_font.setBold(True)
                    self.text_font.setPointSize(min(20 * self.parent.size_factor, self.text_font.pointSize() * 1.5 * self.parent.size_factor))
                elif self.parent.parent.clock_type == 'bar':
                    self.text_font.setBold(True)
                    self.text_fontsetPointSize(min(15 * self.parent.size_factor, self.text_font.pointSize() * 0.7 * self.parent.size_factor))
                else:
                    self.text_font.setBold(False)

            qp.setFont(self.text_font)

            label = QtGui.QLabel(self.text)
            label.setFont(self.text_font)
            text_width = label.fontMetrics().boundingRect(label.text()).width()
            text_height = label.fontMetrics().boundingRect(label.text()).height()

            if text_width + clock_rad*2 > w:
                self.text_font.setStretch(max(63., 85*float(w - clock_rad*2.2)/float(text_width)))
                qp.setFont(self.text_font)
                label = QtGui.QLabel(self.text)
                label.setFont(self.text_font)
                text_width = label.fontMetrics().boundingRect(label.text()).width()
                text_height = label.fontMetrics().boundingRect(label.text()).height()

                if text_width + clock_rad * 2 > w:
                    self.text_font.setPointSize(self.text_font.pointSize() * float(w - clock_rad * 2.2) / float(text_width))
                    qp.setFont(self.text_font)
                    label = QtGui.QLabel(self.text)
                    label.setFont(self.text_font)
                    text_width = label.fontMetrics().boundingRect(label.text()).width()
                    text_height = label.fontMetrics().boundingRect(label.text()).height()


        if self.parent.alignment == 'cl':  # offset clock face and text according to text alignment setting.
            center_offset_x = w - clock_rad * 2
        elif self.parent.alignment[1] == 'c':
            center_offset_x = w / 2 - clock_rad
        else:
            center_offset_x = 0

        if self.parent.alignment[0] == 't':
            center_offset_y = text_height
        else:
            center_offset_y = 0

        center = QtCore.QPointF(constraint / 2 + center_offset_x, constraint / 2 + center_offset_y)

        # draw clock face
        pen = QtGui.QPen()
        if self.selected:
            pen.setColor(default_selct_color)

        elif self.highlighted:
            pen.setColor(default_highlt_color)
        else:
            pen.setColor(default_reg_color)
        qp.setPen(pen)

        brush = QtGui.QBrush(clock_bg_color)
        pen.setWidth(3)
        qp.setPen(pen)
        qp.setBrush(brush)

        if self.parent.parent.clock_type == 'bar':
            pass
        else:
            qp.drawEllipse(center, clock_rad * (1 - clock_thickness / 2), clock_rad * (1 - clock_thickness / 2))

        # draw hands
        pen.setWidth(clock_rad * clock_thickness)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        qp.setPen(pen)

        hour_hand_from_angle(0, clock_rad * 0.7)  # Hour hand

        threshold = 0.025
        if math.sin(self.angle - math.pi / 2) < -1 + threshold:
            if self.highlighted:
                pen.setColor(QtGui.QColor(0, 255, 255))
            elif not (self.selected):
                pen.setColor(QtGui.QColor(150, 150, 150))
            qp.setPen(pen)

        minute_hand_from_angle(self.angle + self.start_angle, clock_rad * 0.7)  # Minute Hand

        if self.selected:
            pen.setColor(default_selct_color)

        elif self.highlighted:
            pen.setColor(default_highlt_color)
        else:
            pen.setColor(default_reg_color)
        qp.setPen(pen)

        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
        pen.setWidth(clock_rad * clock_thickness)
        qp.setPen(pen)
        qp.setBrush(brush)

        if self.parent.parent.clock_type == 'bar':  # re draw clock border in case painted over
            pass
        else:
            qp.drawEllipse(center, clock_rad * (1 - clock_thickness / 2), clock_rad * (1 - clock_thickness / 2))

        # draw text
        if self.parent.parent.high_contrast:
            if self.parent.parent.clock_type == 'bar':
                if self.highlighted:
                    qp.setPen(clock_text_reg_color)
                elif self.selected:
                    qp.setPen(clock_text_color)
                else:
                    qp.setPen(clock_text_hl_color)
            else:
                if self.highlighted:
                    qp.setPen(clock_text_hl_color)
                elif self.selected:
                    qp.setPen(clock_text_color)
                else:
                    qp.setPen(clock_text_reg_color)
        else:
            qp.setPen(clock_text_color)
        qp.setFont(self.text_font)
        if self.redraw_text:
            if self.parent.alignment == 'tc':  # align text according to text layout setting
                x_offest = -text_width / 2
                y_offest = -clock_rad * 1.3
            elif self.parent.alignment == 'cr':
                x_offest = clock_rad
                y_offest = clock_rad * .6
            elif self.parent.alignment == 'cc':
                x_offest = -text_width / 2
                y_offest = clock_rad * .6
            elif self.parent.alignment == 'cl':
                x_offest = -clock_rad - text_width
                y_offest = clock_rad * .6
            elif self.parent.alignment == 'bc':
                x_offest = -text_width / 2
                y_offest = clock_rad * 2.3
            self.text_x = center.x() + x_offest
            self.text_y = center.y() + y_offest

        qp.drawText(self.text_x, self.text_y, self.text)


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