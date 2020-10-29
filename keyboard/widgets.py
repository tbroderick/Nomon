######################################
# Copyright 2019 Nicholas Bonaker, Keith Vertanen, Emli-Mari Nel, Tamara Broderick
# This file is part of the Nomon software.
# Nomon is free software: you can redistribute it and/or modify it
# under the terms of the MIT License reproduced below.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY
# OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR
#OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# <https://opensource.org/licenses/mit-license.html>
######################################



from __future__ import division
from PySide2 import QtCore, QtGui, QtWidgets
import math
from numpy import array
import numpy as np
import config
import kconfig


def indexOf_2d(array, item):
    for row_index in range(len(array)):
        row = array[row_index]
        if item in row:
            col_index = array[row_index].index(item)
            return [row_index, col_index]

    return False


class ClockWidget(QtWidgets.QWidget):

    def __init__(self, text, parent, filler_clock=False):
        super(ClockWidget, self).__init__()

        self.text = text
        self.redraw_text = True
        self.start_angle = 0.
        self.parent = parent
        self.filler_clock = filler_clock  # filler clock is transparent, but saves space in layout for later use
        self.highlighted = False
        self.background = False
        self.selected = False
        self.previous_angle = -360.  # used in pac-man clock to compare if hand passed noon (- to + angle)
        self.color_switch = False  # used in pac-man clock to alternate color fill
        self.new_round = True

        self.draw = False
        self.in_focus = True

        self.w = 1
        self.h = 1

        self.clock_params = None
        self.outer_radius = 0
        self.hand_loc = array([0, 0])
        self.minute_hand_point = QtCore.QPoint(0, 0)
        self.hour_hand_point = QtCore.QPoint(0, 0)
        self.minute_hand_angles = [0, 0, 0, 0, 0, 0]
        self.minute_hand_angle = 0
        self.inner_radius = 0
        self.inner_rect = QtCore.QRect(0, 0, 0, 0)

        self.initUI()

        if self.parent.alignment[0] != 'c':
               self.constraint_factor = 0.5
        else:
            self.constraint_factor = 1
        self.radius = self.size().height() * self.constraint_factor / 2
        self.calculate_clock_size()

    def initUI(self):

        self.size_factor = self.parent.size_factor
        self.minSize = round(20 * self.size_factor)
        self.maxSize = round(50 * self.size_factor)

        self.label = QtWidgets.QLabel(self.text)
        self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # sizePolicy.setWidthForHeight(True)
        # self.setSizePolicy(sizePolicy)

        self.setMinimumSize(self.minSize, self.minSize)
        self.setMaximumHeight(self.maxSize)
        # self.setBaseSize(self.minSize*1.3, self.minSize)
        self.angle = 0

        # self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

    def set_text(self, text):
        self.text = text
        self.label.setText(self.text)
        self.redraw_text = True

    def set_angle(self, angle):
        self.angle = angle

    def set_params(self, clock_params, recompute=False):
        self.clock_params = clock_params
        if recompute:
            self.center = QtCore.QPoint(clock_params[0], clock_params[0])
            self.outer_radius = clock_params[1]
            self.hour_hand_point = QtCore.QPointF(self.center.x(), self.center.x()-self.outer_radius)
            self.draw = True
            self.calculate_clock_size()
            self.rect = QtCore.QRect(self.h / 2 - self.outer_radius, self.h / 2 - self.outer_radius, self.outer_radius * 2,
                              self.outer_radius * 2)

        if self.parent.parent.clock_type == 'default':
            self.minute_hand_point = QtCore.QPoint(clock_params[2], clock_params[3])

        elif self.parent.parent.clock_type == 'ball':
            self.inner_radius = clock_params[2]
            self.inner_radius = min(self.outer_radius, self.inner_radius)

        elif self.parent.parent.clock_type == 'radar':
            self.inner_rect = QtCore.QRect(self.h / 2 - self.outer_radius*0.9, self.h / 2 - self.outer_radius*0.9, self.outer_radius * 2*0.9,
                              self.outer_radius * 2*0.9)
            self.minute_hand_angles = clock_params[2:7]

        elif self.parent.parent.clock_type == 'pac_man':
            self.minute_hand_angle = clock_params[2]

        elif self.parent.parent.clock_type == 'bar':
            self.inner_radius = clock_params[2]

    def paintEvent(self, e):
        if self.draw:
            qp = QtGui.QPainter()
            qp.begin(self)
            # if self.redraw_text:
            self.draw_background(e, qp)
            if not self.filler_clock:
                self.draw_clock(e, qp)
        else:
            qp = QtGui.QPainter()
            qp.begin(self)
            # if self.redraw_text:
            self.draw_background(e, qp)

        qp.end()
        self.redraw_text = False
        
    def calculate_clock_size(self):
        # calculate size of clock from available space
        size = self.size()
        self.w = size.width()
        self.h = size.height()

        # if self.w < self.h:
        #     self.w = self.h
        #     self.h = self.h
        #     self.resize(self.w, self.h)
        #     self.redraw_text = True


        # if self.parent.alignment[0] != 'c':
        #     self.constraint_factor = 0.5
        # else:
        #     self.constraint_factor = 1

        # constraint = self.h * self.constraint_factor
        # self.radius = constraint / 2

        self.radius = self.h

        # if self.parent.alignment == 'cl':  # offset clock face and text according to text alignment setting.
        #     center_offset_x = self.w - self.radius * 2
        # elif self.parent.alignment[1] == 'c':
        #     center_offset_x = self.w / 2 - self.radius
        # else:
        #     center_offset_x = 0
        #
        # if self.parent.alignment[0] == 't':
        #     center_offset_y = self.text_height
        # else:
        #     center_offset_y = 0
        #
        # self.center = QtCore.QPointF(constraint / 2 + center_offset_x, constraint / 2 + center_offset_y)
        self.redraw_text = True

    def draw_background(self, e, qp):
        if self.background:
            color = QtGui.QColor(190, 255, 190)
            self.label.setStyleSheet("background-color:#f0fff0;")
            # f0fff0
        elif not self.in_focus:
            color = QtGui.QColor(220,220,220)
        else:
            color = self.palette().color(QtGui.QPalette.Background)
            self.label.setStyleSheet("background-color:#ffffff;")
        brush = QtGui.QBrush(color)
        # qp.fillRect(0, 0, self.w, self.h, brush)

        if self.parent.parent.clock_type == 'radar' and not self.filler_clock:
            colored_pen = QtGui.QPen()
            colored_pen.setWidth(2)
            if self.selected:
                colored_pen.setColor(config.default_selct_color[self.parent.color_index])
            elif self.highlighted:
                colored_pen.setColor(config.default_highlt_color[self.parent.color_index])
            else:
                colored_pen.setColor(config.default_reg_color[self.parent.color_index])

            qp.setPen(colored_pen)
            qp.setBrush(brush)
            qp.drawEllipse(self.center, self.outer_radius*1.05, self.outer_radius*1.05)

        # calculate size of text from leftover space
        if self.redraw_text:
            self.text_font = QtGui.QFont(config.clock_font[self.parent.parent.font_scale])

            label = QtWidgets.QLabel("test")
            label.setFont(self.text_font)
            font_height_max = label.fontMetrics().boundingRect(label.text()).height()

            self.text_font.setPixelSize(min(font_height_max, self.parent.parent.universal_clock_height*0.85))
            if self.parent.parent.layout_preference == "emoji":
                text_stretch = 100
            else:
                text_stretch = 85
            self.text_font.setStretch(text_stretch)
            self.label.setFont(self.text_font)
        #
        #     label = QtWidgets.QLabel(self.text)
        #     label.setFont(self.text_font)
        #     text_width = label.fontMetrics().boundingRect(label.text()).width()
        #
        #     if self.parent.parent.clock_type != "bar":
        #         width = self.w - 2.1 * self.radius
        #     else:
        #         width = self.w * 0.7
        #
        #     size_factor = float(text_width) / (float(width)*0.95)
        #
        #     print(size_factor)

            # if size_factor > 1:
            #     if size_factor < 1.2:
            #         self.text_font.setStretch(int(85. / size_factor))
            #
            #         label = QtWidgets.QLabel(self.text)
            #         label.setFont(self.text_font)
            #         text_width = label.fontMetrics().boundingRect(label.text()).width()
            #     elif size_factor > 1.2:
            #         self.text_font.setStretch(int(85. / 1.2))
            #
            #         label = QtWidgets.QLabel(self.text)
            #         label.setFont(self.text_font)
            #         text_width = label.fontMetrics().boundingRect(label.text()).width()
            #         size_factor = float(text_width) / (float(width) + 0.1)
            #         self.text_font.setPixelSize(min(50,  max(1, int(float(self.h) / size_factor))))
            #
            #         label = QtWidgets.QLabel(self.text)
            #         label.setFont(self.text_font)
            #         text_width = label.fontMetrics().boundingRect(label.text()).width()
        #
        #     if self.parent.alignment == 'tc':  # align text according to text layout setting
        #         x_offest = -text_width / 2
        #         y_offest = -self.radius * 1.3
        #     elif self.parent.alignment == 'cr':
        #         x_offest = self.radius
        #         y_offest = self.radius * .6
        #     elif self.parent.alignment == 'cc':
        #         x_offest = -text_width / 2
        #         y_offest = self.radius * .6
        #     elif self.parent.alignment == 'cl':
        #         x_offest = -self.radius - text_width
        #         y_offest = self.radius * .6
        #     elif self.parent.alignment == 'bc':
        #         x_offest = -text_width / 2
        #         y_offest = self.radius * 2.3
        #     self.text_x = self.center.x() + x_offest
        #     self.text_y = self.center.y() + y_offest
        # # draw text
        # if self.parent.parent.high_contrast:
        #     if self.parent.parent.clock_type == 'bar':
        #         if self.highlighted:
        #             qp.setPen(config.clock_text_reg_color[self.parent.color_index])
        #         elif self.selected:
        #             qp.setPen(config.clock_text_color[self.parent.color_index])
        #         else:
        #             qp.setPen(config.clock_text_hl_color[self.parent.color_index])
        #     else:
        #         if self.highlighted:
        #             qp.setPen(config.clock_text_hl_color[self.parent.color_index])
        #         elif self.selected:
        #             qp.setPen(config.clock_text_color[self.parent.color_index])
        #         else:
        #             qp.setPen(config.clock_text_reg_color[self.parent.color_index])
        # else:
        #     qp.setPen(config.clock_text_color[self.parent.color_index])
        # qp.setFont(self.text_font)
        # qp.drawText(self.text_x, self.text_y, self.text)

    def draw_clock(self, e, qp):

        colored_pen = QtGui.QPen()
        colored_pen.setWidth(4)
        if self.selected:
            colored_pen.setColor(config.default_selct_color[self.parent.color_index])
        elif self.highlighted:
            colored_pen.setColor(config.default_highlt_color[self.parent.color_index])
        else:
            colored_pen.setColor(config.default_reg_color[self.parent.color_index])

        # draw clock face
        qp.setPen(colored_pen)

        brush = QtGui.QBrush(config.clock_bg_color[self.parent.color_index])

        if self.parent.parent.clock_type != 'bar':
            # if self.parent.parent.clock_type != 'radar' or self.new_round:
            qp.setPen(colored_pen)
            qp.setBrush(brush)
            qp.drawEllipse(self.center, self.outer_radius, self.outer_radius)


        # draw hands
        if self.parent.parent.clock_type == 'default':
            pen = QtGui.QPen()
            pen.setColor(config.default_hh_color[self.parent.color_index])
            pen.setWidth(2)
            qp.setPen(pen)

            qp.drawLine(self.center, self.hour_hand_point)  # Hour Hand
            qp.setPen(colored_pen)
            qp.drawLine(self.center, self.minute_hand_point)  # Minute Hand

        elif self.parent.parent.clock_type == 'ball':
            if self.selected:
                brush.setColor(config.ball_mh_selct_color[self.parent.color_index])

            elif self.highlighted:
                brush.setColor(config.ball_mh_highlt_color[self.parent.color_index])
            else:
                brush.setColor(config.ball_mh_reg_color[self.parent.color_index])
            qp.setBrush(brush)
            pen = QtGui.QPen()
            pen.setColor(QtGui.QColor(0, 0, 0, 0))
            qp.setPen(pen)
            qp.drawEllipse(self.center, self.inner_radius, self.inner_radius)

        elif self.parent.parent.clock_type == 'radar':
            pen = QtGui.QPen()

            pen.setColor(QtGui.QColor(0, 0, 0, 0))
            qp.setPen(pen)
            brush.setColor(QtGui.QColor(255, 255, 255, 255))
            qp.setBrush(brush)
            qp.drawPie(self.inner_rect, self.minute_hand_angles[-1]+20*16, 20 * 16*(len(self.minute_hand_angles)-1))
            for i in range(len(self.minute_hand_angles)-1):
                if self.selected:
                    brush.setColor(QtGui.QColor(0, 255, 0, 255 * i/4))
                    qp.setBrush(brush)
                elif self.highlighted:
                    brush.setColor(QtGui.QColor(0, 0, 255, 255 * i/4))
                    qp.setBrush(brush)
                else:
                    brush.setColor(QtGui.QColor(0, 0, 0, 255 * i/4))
                    qp.setBrush(brush)
                qp.drawPie(self.inner_rect, self.minute_hand_angles[i], 20*16)

            pen.setColor(config.default_hh_color[self.parent.color_index])
            pen.setWidth(2)
            qp.setPen(pen)

            qp.drawLine(self.center, self.hour_hand_point)  # Hour Hand

        elif self.parent.parent.clock_type == 'pac_man':
            pen = QtGui.QPen()
            pen.setColor(QtGui.QColor(0, 0, 0, 0))
            qp.setPen(pen)

            if self.selected:
                brush.setColor(config.pac_man_selct_color[self.parent.color_index])

            elif self.highlighted:
                brush.setColor(config.pac_man_highlt_color[self.parent.color_index])
            else:
                brush.setColor(config.pac_man_reg_color[self.parent.color_index])
            qp.setBrush(brush)

            if self.minute_hand_angle > self.previous_angle:
                self.color_switch = self.color_switch == False

            self.previous_angle = self.minute_hand_angle

            if self.color_switch:
                qp.drawEllipse(self.center, self.outer_radius, self.outer_radius)

                brush.setColor(config.clock_bg_color[self.parent.color_index])
                qp.setBrush(brush)

            qp.setBrush(brush)
            qp.drawPie(self.rect, 90*16, self.minute_hand_angle)

            brush.setColor(QtGui.QColor(0, 0, 0, 0))
            qp.setBrush(brush)
            qp.setPen(colored_pen)
            qp.drawEllipse(self.center, self.outer_radius, self.outer_radius)

        elif self.parent.parent.clock_type == 'bar':
            if self.selected:
                brush.setColor(config.bar_mh_selct_color[self.parent.color_index])

            elif self.highlighted:
                brush.setColor(config.bar_mh_highlt_color[self.parent.color_index])
            else:
                brush.setColor(config.bar_mh_reg_color[self.parent.color_index])
            qp.setBrush(brush)
            pen = QtGui.QPen()
            pen.setColor(QtGui.QColor(0, 0, 0, 0))
            qp.setPen(pen)
            qp.drawRect(10, 2, self.inner_radius, self.h - 4)

            brush.setColor(self.palette().color(QtGui.QPalette.Background))  # redraw background from bar for 'emptying'
            qp.setBrush(brush)
            qp.drawRect(10+self.inner_radius, 2, self.w-10, self.h - 4)

            if self.selected:
                pen.setColor(config.bar_hh_selct_color[self.parent.color_index])

            elif self.highlighted:
                pen.setColor(config.bar_hh_highlt_color[self.parent.color_index])
            else:
                pen.setColor(config.bar_hh_reg_color[self.parent.color_index])
            pen.setWidth(4)
            qp.setPen(pen)
            brush.setColor(QtGui.QColor(0, 0, 0, 0))
            qp.setBrush(brush)

            qp.drawRect(10, 1, self.w - 20, self.h - 1)

            # draw text over bar
            if self.parent.parent.high_contrast:
                if self.parent.parent.clock_type == 'bar':
                    if self.highlighted:
                        qp.setPen(config.clock_text_reg_color[self.parent.color_index])
                    elif self.selected:
                        qp.setPen(config.clock_text_color[self.parent.color_index])
                    else:
                        qp.setPen(config.clock_text_hl_color[self.parent.color_index])
                else:
                    if self.highlighted:
                        qp.setPen(config.clock_text_hl_color[self.parent.color_index])
                    elif self.selected:
                        qp.setPen(config.clock_text_color[self.parent.color_index])
                    else:
                        qp.setPen(config.clock_text_reg_color[self.parent.color_index])
            else:
                qp.setPen(config.clock_text_color[self.parent.color_index])
            qp.setFont(self.text_font)
            # qp.drawText(self.text_x, self.text_y, self.text)
        self.new_round = False


class HistogramWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(HistogramWidget, self).__init__()
        self.parent = parent
        self.initUI()
        self.bars = self.parent.bars

    def initUI(self):
        self.setMinimumSize(200, 50)

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
        # if not self.parent.in_focus:
        #     qp.fillRect(0,0,self.geometry().width(),self.geometry().height(),QtGui.QColor(0,0,0,25))


class VerticalSeparator(QtWidgets.QWidget):

    def __init__(self):
        super(VerticalSeparator, self).__init__()

        self.initUI()

    def initUI(self):
        self.setMinimumSize(1, 1)
        self.setMaximumWidth(1)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        # self.drawLine(qp)
        qp.end()

    def drawLine(self, qp):
        # calculate size of histogram from available space
        size = self.size()
        w = size.width()
        h = size.height()

        pen = QtGui.QPen(QtGui.QColor(100, 100, 100), 1)
        qp.setPen(pen)
        qp.drawLine(w / 2, 0, w / 2, h)


class HorizontalSeparator(QtWidgets.QWidget):

    def __init__(self):
        super(HorizontalSeparator, self).__init__()

        self.initUI()

    def initUI(self):
        self.setMinimumSize(1, 1)
        self.setMaximumHeight(1)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        # self.drawLine(qp)
        qp.end()

    def drawLine(self, qp):
        # calculate size of histogram from available space
        size = self.size()
        w = size.width()
        h = size.height()

        pen = QtGui.QPen(QtGui.QColor(100, 100, 100), 1)
        qp.setPen(pen)
        qp.drawLine(0, h / 2, w, h / 2)


class OldClockWidget(QtWidgets.QWidget):

    def __init__(self, text, parent, filler_clock=False):
        super(OldClockWidget, self).__init__()

        self.text = text
        self.redraw_text = True
        self.start_angle = 0.
        self.parent = parent
        self.filler_clock = filler_clock  # filler clock is transparent, but saves space in layout for later use
        self.highlighted = False
        self.background = False
        self.selected = False
        self.previous_angle = -360.  # used in pac-man clock to compare if hand passed noon (- to + angle)
        self.color_switch = False  # used in pac-man clock to alternate color fill
        self.dummy_angle_offset = 0.  # used in pretraining
        self.w = 1
        self.h = 1
        self.radius=1
        self.initUI()

        # try:
        #     if self.parent.alignment[0] != 'c':
        #         self.constraint_factor = 0.5
        #     else:
        #         self.constraint_factor = 1
        #     self.radius = self.size().height() * self.constraint_factor / 2
        # except:
        #     pass

    def initUI(self):

        self.size_factor = self.parent.size_factor
        self.minSize = round(15 * self.size_factor)
        self.maxSize = round(50 * self.size_factor)

        self.setMinimumSize(self.minSize, self.minSize)
        self.setMaximumHeight(self.maxSize)
        self.setBaseSize(self.minSize, self.minSize)
        self.angle = 0

    def set_text(self, text):
        self.text = text
        self.redraw_text = True

    def set_angle(self, angle):
        self.angle = angle

    def paintEvent(self, e):
        size = self.size()
        if self.w != size.width() or self.h != size.height():
            self.calcClockSize()

        qp = QtGui.QPainter()
        qp.begin(self)
        if not self.filler_clock:
            self.draw_clock(e, qp)
        qp.end()
        self.redraw_text = False

    def calcClockSize(self):
        # calculate size of clock from available space
        size = self.size()
        self.w = size.width()
        self.h = size.height()
        if self.parent.alignment[0] != 'c':
            self.constraint_factor = 0.5
        else:
            self.constraint_factor = 1

        constraint = self.h * self.constraint_factor
        self.radius = constraint / 2

        self.radius = self.radius

        if self.parent.alignment == 'cl':  # offset clock face and text according to text alignment setting.
            center_offset_x = self.w - self.radius * 2
        elif self.parent.alignment[1] == 'c':
            center_offset_x = self.w / 2 - self.radius
        else:
            center_offset_x = 0

        if self.parent.alignment[0] == 't':
            center_offset_y = self.text_height
        else:
            center_offset_y = 0

        self.center = QtCore.QPointF(constraint / 2 + center_offset_x, constraint / 2 + center_offset_y)
        self.redraw_text = True

    def draw_clock(self, e, qp):

        def minute_hand_from_angle(angle, radius):

            angle -= math.pi / 2  # reference angle from noon

            far_point = self.center + QtCore.QPointF(math.cos(angle) * radius, math.sin(angle) * radius)
            qp.drawLine(self.center, far_point)

        def hour_hand_from_angle(angle, radius):
            pen.setColor(config.default_hh_color[self.parent.color_index])
            pen.setWidth(2)
            qp.setPen(pen)

            minute_hand_from_angle(angle, radius * 1.1)

            if self.selected:
                pen.setColor(config.default_selct_color[self.parent.color_index])

            elif self.highlighted:
                pen.setColor(config.default_highlt_color[self.parent.color_index])
            else:
                pen.setColor(config.default_reg_color[self.parent.color_index])
            pen.setWidth(3)
            qp.setPen(pen)

        clock_thickness = 1. / 6
        # calculate size of text from leftover space
        self.text_font = QtGui.QFont(config.clock_font[2])
        self.text_font.setPixelSize(self.height()*0.8)
        self.text_font.setStretch(85)
        qp.setFont(self.text_font)

        label = QtWidgets.QLabel(self.text)
        label.setFont(self.text_font)
        text_width = label.fontMetrics().boundingRect(label.text()).width()


        width = self.w - 2.1 * self.radius


        size_factor = float(text_width) / (float(width) + 0.1)

        if size_factor > 1:
            if size_factor < 1.3:
                self.text_font.setStretch(int(85. / size_factor))

                label = QtWidgets.QLabel(self.text)
                label.setFont(self.text_font)
                text_width = label.fontMetrics().boundingRect(label.text()).width()
            elif size_factor > 1.3:
                self.text_font.setStretch(65)
                label = QtWidgets.QLabel(self.text)
                label.setFont(self.text_font)
                text_width = label.fontMetrics().boundingRect(label.text()).width()

                size_factor = float(text_width) / (float(width) + 0.1)
                self.text_font.setPixelSize(max(1, int(float(self.h) / size_factor)))

                label = QtWidgets.QLabel(self.text)
                label.setFont(self.text_font)
                text_width = label.fontMetrics().boundingRect(label.text()).width()

        # draw clock face
        pen = QtGui.QPen()
        if self.selected:
            pen.setColor(config.default_selct_color[self.parent.color_index])

        elif self.highlighted:
            pen.setColor(config.default_highlt_color[self.parent.color_index])
        else:
            pen.setColor(config.default_reg_color[self.parent.color_index])
        qp.setPen(pen)

        brush = QtGui.QBrush(config.clock_bg_color[self.parent.color_index])

        pen.setWidth(3)
        qp.setPen(pen)
        qp.setBrush(brush)

        qp.drawEllipse(self.center, self.radius * (1 - clock_thickness / 2),
                           self.radius * (1 - clock_thickness / 2))

        # draw hands
        pen.setWidth(self.radius * clock_thickness)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        qp.setPen(pen)

        hour_hand_from_angle(0, self.radius * 0.7)  # Hour hand

        threshold = 0.025
        if math.sin(self.angle - math.pi / 2) < -1 + threshold:
            if self.highlighted:
                pen.setColor(QtGui.QColor(0, 255, 255))
            elif not (self.selected):
                pen.setColor(QtGui.QColor(150, 150, 150))
            qp.setPen(pen)

        minute_hand_from_angle(self.angle + self.start_angle, self.radius * 0.7)  # Minute Hand

        if self.selected:
            pen.setColor(config.default_selct_color[self.parent.color_index])

        elif self.highlighted:
            pen.setColor(config.default_highlt_color[self.parent.color_index])
        else:
            pen.setColor(config.default_reg_color[self.parent.color_index])
        qp.setPen(pen)

        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
        pen.setWidth(self.radius * clock_thickness)
        qp.setPen(pen)
        qp.setBrush(brush)


        qp.drawEllipse(self.center, self.radius * (1 - clock_thickness / 2),
                           self.radius * (1 - clock_thickness / 2))

        # draw text

        qp.setPen(config.clock_text_color[self.parent.color_index])
        qp.setFont(self.text_font)

        x_offest = self.radius
        y_offest = self.radius * .6

        self.text_x = self.center.x() + x_offest
        self.text_y = self.center.y() + y_offest

        qp.drawText(self.text_x, self.text_y, self.text)


class KeygridWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(KeygridWidget, self).__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.parent = parent
        self.screen_res = self.parent.screen_res

        self.highlight = False

        self.init_ui()

    # noinspection PyUnresolvedReferences
    def init_ui(self):
        self.x_positions = []
        self.y_positions = []
        self.target_layout = self.parent.parent.target_layout

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_layout(qp)
        qp.end()

    def draw_layout(self, qp):
        self.generate_layout()
        size = self.size()
        w = size.width()
        h = size.height()

        qp.setPen(QtGui.QPen(QtGui.QColor(120, 120, 120), 1))
        if self.highlight:
            qp.setBrush(QtGui.QBrush(QtGui.QColor(210, 255, 210)))
        else:
            qp.setBrush(QtGui.QBrush(QtGui.QColor(238, 238, 238)))
        qp.drawRect(0, 0, w - 1, h - 1)

        for row in range(len(self.x_positions)):
            y_start = self.y_positions[row][0]
            y_end = self.y_positions[row][1]

            for col in range(len(self.x_positions[row])):
                x_start = self.x_positions[row][col][0]
                x_end = self.x_positions[row][col][1]

                if self.highlight:
                    qp.setBrush(QtGui.QBrush(QtGui.QColor(245, 255, 245)))
                else:
                    qp.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))

                qp.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 1))

                qp.drawRect(x_start, y_start, x_end - x_start, y_end - y_start)

    def generate_layout(self):
        if self.parent.parent.layout_preference == "alpha":
            if self.parent.parent.word_pred_on == 2:
                self.target_layout = kconfig.alpha_target_layout
            elif self.parent.parent.word_pred_on == 1:
                self.target_layout = kconfig.alpha_target_layout_reduced
            else:
                self.target_layout = kconfig.alpha_target_layout_off
        else:
            if self.parent.parent.word_pred_on == 1:
                self.target_layout = kconfig.qwerty_target_reduced
            else:
                self.target_layout = kconfig.qwerty_target_layout

        size = self.size()
        w = size.width()
        h = size.height()

        if self.parent.parent.layout_preference == "qwerty" and self.parent.parent.word_pred_on == 2:
            y_height_bottom = h / 10 * 0.95
            y_height = (h - y_height_bottom) / 3 * 0.95
            y_spacing = h / (len(self.target_layout) + 1) * 0.05
        elif self.parent.parent.word_pred_on == 1:
            y_height = h / len(self.target_layout) * 0.93
            y_spacing = h / (len(self.target_layout) + 3) * 0.07
        else:
            y_height = h / len(self.target_layout) * 0.95
            y_spacing = h / (len(self.target_layout) + 1) * 0.05

        self.x_width = (w - y_spacing * (len(self.target_layout[0]) + 1)) / len(self.target_layout[0])

        self.x_positions = []

        for row in range(len(self.target_layout)):
            row_x_positions = []

            layout_row = self.target_layout[row]

            if self.parent.parent.layout_preference == "qwerty" and row == len(self.target_layout) - 1:
                base_x_width = (w - y_spacing * 6) / 10
                prev_x_spacing = 0

                for col in range(len(layout_row)):
                    char = layout_row[col]

                    double_space_chars = [kconfig.mybad_char, kconfig.back_char, kconfig.clear_char,
                                          kconfig.speak_char]
                    if char in double_space_chars:
                        x_width = base_x_width * 2
                    else:
                        x_width = base_x_width - y_spacing / 2

                    x_start = col * y_spacing + prev_x_spacing + y_spacing
                    prev_x_spacing += x_width

                    x_end = x_start + x_width
                    row_x_positions.append([x_start, x_end])
            else:
                x_width = (w - y_spacing * (len(layout_row) + 1)) / len(layout_row)

                for col in range(len(layout_row)):
                    x_start = col * y_spacing + col * x_width + y_spacing
                    x_end = x_start + x_width
                    row_x_positions.append([x_start, x_end])

            self.x_positions.append(row_x_positions)

        self.y_positions = []
        for row in range(len(self.target_layout)):
            if self.parent.parent.word_pred_on == 1 and row >= 1:
                y_start = row * y_spacing + row * y_height + y_spacing*3
                y_end = y_start + y_height
                self.y_positions.append([y_start, y_end])
            elif self.parent.parent.layout_preference == "qwerty" and row == len(self.target_layout) - 1 and \
                    self.parent.parent.word_pred_on == 2:
                y_start = row * y_spacing + row * y_height + y_spacing
                y_end = y_start + y_height_bottom
                self.y_positions.append([y_start, y_end])
            else:
                y_start = row * y_spacing + row * y_height + y_spacing
                y_end = y_start + y_height
                self.y_positions.append([y_start, y_end])

    def resizeEvent(self, event):
        QtWidgets.QWidget.resizeEvent(self, event)
        self.parent.update_widget_positions()


class clockGridWidget(QtWidgets.QWidget):

    def __init__(self, parent, keygrid):
        super(clockGridWidget, self).__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.parent = parent

        self.keygrid = keygrid
        self.target_layout = self.parent.target_layout
        self.key_chars = kconfig.key_chars
        self.main_chars = kconfig.main_chars
        self.n_pred = 3

        self.init_ui()

    # noinspection PyUnresolvedReferences
    def init_ui(self):
        self.xpos = 0
        self.clocks = []

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")

    def generate_layout(self):
        if self.parent.layout_preference == "alpha":
            if self.parent.word_pred_on == 1:
                self.target_layout = kconfig.alpha_target_layout_reduced
                self.clock_radius = min((self.keygrid.y_positions[0][1] - self.keygrid.y_positions[0][0]) / 3,
                                        (self.keygrid.x_positions[0][0][1] - self.keygrid.x_positions[0][0][0]) / 10)
            elif self.parent.word_pred_on == 2:
                self.target_layout = kconfig.alpha_target_layout
                self.clock_radius = (self.keygrid.y_positions[0][1] - self.keygrid.y_positions[0][0]) / 7
            else:
                self.target_layout = kconfig.alpha_target_layout_off
                self.clock_radius = min((self.keygrid.y_positions[0][1] - self.keygrid.y_positions[0][0]) / 3,
                                        (self.keygrid.x_positions[0][0][1] - self.keygrid.x_positions[0][0][0]) / 10)
        else:
            if self.parent.word_pred_on == 1:
                self.target_layout = kconfig.qwerty_target_reduced
                self.clock_radius = min((self.keygrid.y_positions[0][1] - self.keygrid.y_positions[0][0]) / 3,
                                        (self.keygrid.x_positions[0][0][1] - self.keygrid.x_positions[0][0][0]) / 10)
            elif self.parent.word_pred_on == 2:
                self.target_layout = kconfig.qwerty_target_layout
                self.clock_radius = (self.keygrid.y_positions[0][1] - self.keygrid.y_positions[0][0]) / 10
            else:
                self.target_layout = kconfig.qwerty_target_layout
                self.clock_radius = min((self.keygrid.y_positions[0][1] - self.keygrid.y_positions[0][0]) / 4,
                                        (self.keygrid.x_positions[0][0][1] - self.keygrid.x_positions[0][0][0]) / 6)
        self.clocks = []


        for i in range(len(self.main_chars)):
            main_char = self.main_chars[i]
            main_char_indices = indexOf_2d(self.target_layout, main_char)

            x_start = self.keygrid.x_positions[main_char_indices[0]][main_char_indices[1]][0]
            x_end = self.keygrid.x_positions[main_char_indices[0]][main_char_indices[1]][1]
            y_start = self.keygrid.y_positions[main_char_indices[0]][0]
            y_end = self.keygrid.y_positions[main_char_indices[0]][1]

            self.generate_word_clock_layout(x_start, y_start, x_end, y_end)
            self.generate_main_clock_layout(x_start, y_start, x_end, y_end, main_char)

        if indexOf_2d(self.target_layout, "BREAKUNIT"):
            break_chars = kconfig.break_chars
            break_chars = [char for char in break_chars if char in self.key_chars]

            break_unit_indicies = indexOf_2d(self.target_layout, "BREAKUNIT")
            x_start = self.keygrid.x_positions[break_unit_indicies[0]][break_unit_indicies[1]][0]
            x_end = self.keygrid.x_positions[break_unit_indicies[0]][break_unit_indicies[1]][1]
            y_start = self.keygrid.y_positions[break_unit_indicies[0]][0]
            y_end = self.keygrid.y_positions[break_unit_indicies[0]][1]

            for break_char_index in range(len(break_chars)):
                break_char = break_chars[break_char_index]

                break_clock_x = x_start + (x_end - x_start) / 2 * (break_char_index % 2 + 0.25)
                if break_char_index < 2:
                    break_clock_y = y_start + (y_end - y_start) / 4
                else:
                    break_clock_y = y_start + (y_end - y_start) * 3 / 4

                cur_break_clock = Clock(self, break_clock_x, break_clock_y, self.clock_radius, break_char)

                for i in range(self.n_pred):
                    self.clocks.append(None)

                self.clocks.append(cur_break_clock)
        else:
            for break_char in kconfig.break_chars:
                break_char_indices = indexOf_2d(self.target_layout, break_char)

                x_start = self.keygrid.x_positions[break_char_indices[0]][break_char_indices[1]][0]
                x_end = self.keygrid.x_positions[break_char_indices[0]][break_char_indices[1]][1]
                y_start = self.keygrid.y_positions[break_char_indices[0]][0]
                y_end = self.keygrid.y_positions[break_char_indices[0]][1]

                for i in range(self.n_pred):
                    self.clocks.append(None)
                self.generate_main_clock_layout(x_start, y_start, x_end, y_end, break_char)

        if indexOf_2d(self.target_layout, "BACKUNIT"):
            back_chars = ['#', '$']
            back_chars = [char for char in back_chars if char in self.key_chars]

            back_unit_indicies = indexOf_2d(self.target_layout, "BACKUNIT")
            x_start = self.keygrid.x_positions[back_unit_indicies[0]][back_unit_indicies[1]][0]

            y_start = self.keygrid.y_positions[back_unit_indicies[0]][0]
            y_end = self.keygrid.y_positions[back_unit_indicies[0]][1]

            for back_char_index in range(len(back_chars)):
                back_char = back_chars[back_char_index]

                back_clock_x = x_start + self.clock_radius * 1.5
                back_clock_y = y_start + (y_end - y_start) / 4 * ((back_char_index % 2) * 2 + 1)

                if back_char == '#':
                    back_char = 'Backspace'
                elif back_char == '$':
                    back_char = 'Clear'

                cur_back_clock = Clock(self, back_clock_x, back_clock_y, self.clock_radius, back_char)
                for i in range(self.n_pred):
                    self.clocks.append(None)

                self.clocks.append(cur_back_clock)
        else:
            back_chars = ['#', '$']
            for back_char in back_chars:
                back_char_indices = indexOf_2d(self.target_layout, back_char)

                if back_char == '#':
                    back_char = 'Backspace'
                elif back_char == '$':
                    back_char = 'Clear'

                x_start = self.keygrid.x_positions[back_char_indices[0]][back_char_indices[1]][0]
                x_end = self.keygrid.x_positions[back_char_indices[0]][back_char_indices[1]][1]
                y_start = self.keygrid.y_positions[back_char_indices[0]][0]
                y_end = self.keygrid.y_positions[back_char_indices[0]][1]

                for i in range(self.n_pred):
                    self.clocks.append(None)
                self.generate_main_clock_layout(x_start, y_start, x_end, y_end, back_char)

        if indexOf_2d(self.target_layout, "UNDOUNIT"):

            undo_unit_indicies = indexOf_2d(self.target_layout, "UNDOUNIT")
            x_start = self.keygrid.x_positions[undo_unit_indicies[0]][undo_unit_indicies[1]][0]
            x_end = self.keygrid.x_positions[undo_unit_indicies[0]][undo_unit_indicies[1]][1]
            y_start = self.keygrid.y_positions[undo_unit_indicies[0]][0]
            y_end = self.keygrid.y_positions[undo_unit_indicies[0]][1]

            undo_clock_x = x_start + self.clock_radius * 1.5
            undo_clock_y = y_start + (y_end - y_start) / 4

            cur_undo_clock = Clock(self, undo_clock_x, undo_clock_y, self.clock_radius, "Undo")
            for i in range(self.n_pred):
                self.clocks.append(None)

            self.clocks.append(cur_undo_clock)

            space_clock_x = x_start + self.clock_radius * 1.5
            space_clock_y = y_start + (y_end - y_start) / 4 * 3

            cur_space_clock = Clock(self, space_clock_x, space_clock_y, self.clock_radius, "_")
            for i in range(self.n_pred):
                self.clocks.append(None)

            self.clocks.append(cur_space_clock)

            break_clock_x = x_start + (x_end - x_start) / 2 * (1.25)
            break_clock_y = y_start + (y_end - y_start) / 4 * 3

            cur_speak_clock = Clock(self, break_clock_x, break_clock_y, self.clock_radius, "speak")
            for i in range(self.n_pred):
                self.clocks.append(None)

            self.clocks.append(cur_speak_clock)

            undo_label_x = x_start + self.clock_radius * 8
            undo_label_y = y_start + (y_end - y_start) / 4

            # self.undo_label = new Label(self.face_canvas, undo_label_x, undo_label_y, self.clock_radius*2,"")
        else:
            special_chars = [kconfig.mybad_char, kconfig.space_char, kconfig.speak_char]
            for special_char in special_chars:
                special_char_indices = indexOf_2d(self.target_layout, special_char)

                if special_char == kconfig.mybad_char:
                    special_char = 'Undo'
                elif special_char == kconfig.speak_char:
                    special_char = 'Speak'

                x_start = self.keygrid.x_positions[special_char_indices[0]][special_char_indices[1]][0]
                x_end = self.keygrid.x_positions[special_char_indices[0]][special_char_indices[1]][1]
                y_start = self.keygrid.y_positions[special_char_indices[0]][0]
                y_end = self.keygrid.y_positions[special_char_indices[0]][1]

                for i in range(self.n_pred):
                    self.clocks.append(None)
                self.generate_main_clock_layout(x_start, y_start, x_end, y_end, special_char)

        if self.parent.words_li is not None:
            self.update_word_clocks(self.parent.words_li)

    def generate_main_clock_layout(self, x_start, y_start, x_end, y_end, text):
        if self.parent.layout_preference == "qwerty" and self.parent.word_pred_on == 2:
            main_clock_x = x_start + self.clock_radius * 1.5
            main_clock_y = y_start + self.clock_radius * 1.15

            cur_main_clock = Clock(self, main_clock_x, main_clock_y, self.clock_radius, text)

            self.clocks.append(cur_main_clock)
        else:
            main_clock_x = x_start + self.clock_radius * 1.2
            main_clock_y = (y_start + y_end) / 2

            cur_main_clock = Clock(self, main_clock_x, main_clock_y, self.clock_radius, text)

            self.clocks.append(cur_main_clock)

    def generate_word_clock_layout(self, x_start, y_start, x_end, y_end):
        if self.parent.layout_preference == "qwerty":
            word_clock_x = x_start + self.clock_radius * 1.5

            for word_clock_index in range(self.n_pred):
                word_clock_y = y_start + (y_end - y_start) / 8 * ((word_clock_index + 1.5) * 2)

                cur_word_clock = Clock(self, word_clock_x, word_clock_y, self.clock_radius, "filler")
                self.clocks.append(cur_word_clock)

        else:
            word_clock_x = x_start + (x_end - x_start) * 0.4

            for word_clock_index in range(-1, self.n_pred - 1):
                word_clock_y = (y_start + y_end) / 2 + self.clock_radius * 2.25 * word_clock_index

                cur_word_clock = Clock(self, word_clock_x, word_clock_y, self.clock_radius, "filler")
                self.clocks.append(cur_word_clock)

    def update_word_clocks(self, words):
        reduced_word_index = 0

        for clock_index in range(len(self.clocks)):
            clock = self.clocks[clock_index]

            key_index = int(clock_index / (self.n_pred + 1))
            word_index = clock_index % (self.n_pred + 1)
            if (word_index != 3) and (key_index < len(self.main_chars)):
                if words[key_index][word_index] != "":
                    if self.parent.word_pred_on == 1:
                        self.place_reduced_word_clock(clock, reduced_word_index)
                        reduced_word_index += 1

                    word = words[key_index][word_index]
                    clock.text = word
                    clock.filler = False
                else:
                    clock.text = ""
                    clock.filler = True

        self.update()
        self.update_mask()

        # ifnself.parent.emoji_keyboard)
        #     self.undo_label.draw_text()

    def place_reduced_word_clock(self, clock, index):
        x_start = self.keygrid.x_positions[0][index][0]
        x_end = self.keygrid.x_positions[0][index][1]
        y_start = self.keygrid.y_positions[0][0]
        y_end = self.keygrid.y_positions[0][1]

        clock_x = x_start + self.clock_radius * 1.2
        clock_y = (y_start + y_end) / 2

        clock.x_pos = clock_x
        clock.y_pos = clock_y

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_layout(qp)
        qp.end()

    def draw_layout(self, qp):
        for clock in self.clocks:
            if clock is not None:
                clock.draw_face(qp)

    def update_mask(self):
        maskedRegion = QtGui.QRegion(0, 0, 0, 0,
                                     QtGui.QRegion.Ellipse)
        for clock in self.clocks:
            if clock is not None:
                text_length = self.keygrid.x_width*2
                maskedRegion += QtGui.QRegion(clock.x_pos - clock.radius * 1.2, clock.y_pos - clock.radius * 1.2,
                                              clock.radius * 2.4, clock.radius * 2.4, QtGui.QRegion.Ellipse)
                maskedRegion += QtGui.QRegion(clock.x_pos + clock.radius * 1.5, clock.y_pos - clock.radius,
                                              text_length * 2 / 3, clock.radius * 3, QtGui.QRegion.Rectangle)
        self.setMask(maskedRegion)


class clockHandsWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super(clockHandsWidget, self).__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.parent = parent

        self.init_ui()

    # noinspection PyUnresolvedReferences
    def init_ui(self):
        self.xpos = 0
        self.target_layout = kconfig.alpha_target_layout

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_hands(qp)
        qp.end()

    def draw_hands(self, qp):
        for clock in self.parent.clocks:
            if clock is not None:
                clock.draw_hands(qp)

    def update_mask(self):
        maskedRegion = QtGui.QRegion(0, 0, 0, 0,
                                     QtGui.QRegion.Ellipse)
        for clock in self.parent.clocks:
            if clock is not None:
                maskedRegion += QtGui.QRegion(clock.x_pos - clock.radius, clock.y_pos - clock.radius, clock.radius * 2,
                                              clock.radius * 2, QtGui.QRegion.Ellipse)
        self.setMask(maskedRegion)


class Clock():
    def __init__(self, parent, x_pos, y_pos, radius, text=""):
        self.parent = parent
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = radius
        self.angle = np.random.random() * np.pi
        self.text = text
        self.filler = False
        self.highlighted = True
        self.winner = False

        font = QtGui.QFont('Helvetica')
        font.setPixelSize(self.radius * 1.8)
        self.text_width = QtGui.QFontMetrics(font).width(self.text)

    def draw_face(self, qp):
        if not self.filler:
            qp.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))

            if (self.winner):
                qp.setPen(QtGui.QPen(QtGui.QColor(0, 255, 0), self.radius / 5))
            elif (self.highlighted):
                qp.setPen(QtGui.QPen(QtGui.QColor(0, 86, 255), self.radius / 5))
            else:
                qp.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), self.radius / 5))

            qp.drawEllipse(self.x_pos - self.radius, self.y_pos - self.radius,
                           2 * self.radius, 2 * self.radius)

            qp.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), self.radius / 5))
            font = QtGui.QFont('Helvetica')
            if self.parent.parent.layout_preference == "qwerty":
                font.setPixelSize(self.radius * 1.4)
            else:
                if self.parent.parent.word_pred_on == 2:
                    font.setPixelSize(self.radius * 1.8)
                else:
                    font.setPixelSize(self.radius * 1.4)
            qp.setFont(font)

            qp.drawText(self.x_pos + self.radius * 1.5, self.y_pos + self.radius * 0.5, self.text)

            self.text_width = QtGui.QFontMetrics(font).width(self.text)

    def draw_hands(self, qp):
        if not self.filler:
            qp.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), self.radius / 10))
            qp.drawLine(self.x_pos, self.y_pos, self.x_pos,
                        self.y_pos - self.radius)

            if (self.winner):
                qp.setPen(QtGui.QPen(QtGui.QColor(0, 255, 0), self.radius / 5))
            elif (self.highlighted):
                qp.setPen(QtGui.QPen(QtGui.QColor(0, 86, 255), self.radius / 5))
            else:
                qp.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), self.radius / 5))

            angle_corr = 0

            qp.drawLine(self.x_pos - self.radius * np.cos(self.angle - angle_corr) * 0.,
                        self.y_pos - self.radius * np.sin(self.angle - angle_corr) * 0,
                        self.x_pos + self.radius * np.cos(self.angle - angle_corr) * 0.75,
                        self.y_pos + self.radius * np.sin(self.angle - angle_corr) * 0.75)
