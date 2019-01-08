from __future__ import division
from PyQt4.QtCore import QPoint, QRect, QPointF, Qt
from PyQt4.QtGui import QWidget, QPainter, QPen, QLabel, QFont, QBrush, QColor, QPalette
import math
from numpy import array
import config


class ClockWidgit(QWidget):

    def __init__(self, text, parent, filler_clock=False):
        super(ClockWidgit, self).__init__()

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
        self.minute_hand_point = QPoint(0, 0)
        self.hour_hand_point = QPoint(0, 0)
        self.minute_hand_angles = [0, 0, 0, 0, 0, 0]
        self.minute_hand_angle = 0
        self.inner_radius = 0

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

        self.setMinimumSize(self.minSize*1.3, self.minSize)
        self.setMaximumHeight(self.maxSize)
        # self.setBaseSize(self.minSize*1.3, self.minSize)
        self.angle = 0

        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def set_text(self, text):
        self.text = text
        self.redraw_text = True

    def set_angle(self, angle):
        self.angle = angle

    def set_params(self, clock_params, recompute=False):
        self.clock_params = clock_params
        if recompute:
            self.center = QPoint(clock_params[0], clock_params[0])
            self.outer_radius = clock_params[1]
            self.hour_hand_point = QPointF(self.center.x(), self.center.x()-self.outer_radius)
            self.draw = True
            self.calculate_clock_size()
            self.rect = QRect(self.h / 2 - self.outer_radius, self.h / 2 - self.outer_radius, self.outer_radius * 2,
                              self.outer_radius * 2)

        if self.parent.parent.clock_type == 'default':
            self.minute_hand_point = QPoint(clock_params[2], clock_params[3])

        elif self.parent.parent.clock_type == 'ball':
            self.inner_radius = clock_params[2]
            self.inner_radius = min(self.outer_radius, self.inner_radius)

        elif self.parent.parent.clock_type == 'radar':
            self.inner_rect = QRect(self.h / 2 - self.outer_radius*0.9, self.h / 2 - self.outer_radius*0.9, self.outer_radius * 2*0.9,
                              self.outer_radius * 2*0.9)
            self.minute_hand_angles = clock_params[2:7]

        elif self.parent.parent.clock_type == 'pac_man':
            self.minute_hand_angle = clock_params[2]

        elif self.parent.parent.clock_type == 'bar':
            self.inner_radius = clock_params[2]

    def paintEvent(self, e):
        if self.draw:
            qp = QPainter()
            qp.begin(self)
            if self.redraw_text:
                self.draw_background(e, qp)
            if not self.filler_clock:
                self.draw_clock(e, qp)
        else:
            qp = QPainter()
            qp.begin(self)
            if self.redraw_text:
                self.draw_background(e, qp)

        qp.end()
        self.redraw_text = False
        
    def calculate_clock_size(self):
        # calculate size of clock from available space
        size = self.size()
        self.w = size.width()
        self.h = size.height()

        if self.w < self.h * 1.5:
            self.w = self.h
            self.h = self.h/1.5
            self.resize(self.w, self.h)
            self.redraw_text = True


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

        self.center = QPointF(constraint / 2 + center_offset_x, constraint / 2 + center_offset_y)
        self.redraw_text = True

    def draw_background(self, e, qp):
        if self.background:
            color = QColor(175, 255, 175)
        elif not self.in_focus:
            color = QColor(220,220,220)
        else:
            color = self.palette().color(QPalette.Background)
        brush = QBrush(color)
        qp.fillRect(0, 0, self.w, self.h, brush)

        if self.parent.parent.clock_type == 'radar' and not self.filler_clock:
            colored_pen = QPen()
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
            self.text_font = QFont(config.clock_font)
            self.text_font.setPixelSize(min(self.h, 50))
            self.text_font.setStretch(85)
            qp.setFont(self.text_font)

            label = QLabel(self.text)
            label.setFont(self.text_font)
            text_width = label.fontMetrics().boundingRect(label.text()).width()

            if self.parent.parent.clock_type != "bar":
                width = self.w - 2.1 * self.radius
            else:
                width = self.w * 0.7

            size_factor = float(text_width) / (float(width)*0.95)

            if size_factor > 1:
                if size_factor < 1.2:
                    self.text_font.setStretch(int(85. / size_factor))

                    label = QLabel(self.text)
                    label.setFont(self.text_font)
                    text_width = label.fontMetrics().boundingRect(label.text()).width()
                elif size_factor > 1.2:
                    self.text_font.setStretch(int(85. / 1.2))
                    label = QLabel(self.text)
                    label.setFont(self.text_font)
                    text_width = label.fontMetrics().boundingRect(label.text()).width()

                    size_factor = float(text_width) / (float(width) + 0.1)
                    self.text_font.setPixelSize(min(50,  max(1, int(float(self.h) / size_factor))))

                    label = QLabel(self.text)
                    label.setFont(self.text_font)
                    text_width = label.fontMetrics().boundingRect(label.text()).width()

            if self.parent.alignment == 'tc':  # align text according to text layout setting
                x_offest = -text_width / 2
                y_offest = -self.radius * 1.3
            elif self.parent.alignment == 'cr':
                x_offest = self.radius
                y_offest = self.radius * .6
            elif self.parent.alignment == 'cc':
                x_offest = -text_width / 2
                y_offest = self.radius * .6
            elif self.parent.alignment == 'cl':
                x_offest = -self.radius - text_width
                y_offest = self.radius * .6
            elif self.parent.alignment == 'bc':
                x_offest = -text_width / 2
                y_offest = self.radius * 2.3
            self.text_x = self.center.x() + x_offest
            self.text_y = self.center.y() + y_offest
        # draw text
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
        qp.drawText(self.text_x, self.text_y, self.text)

    def draw_clock(self, e, qp):

        colored_pen = QPen()
        colored_pen.setWidth(4)
        if self.selected:
            colored_pen.setColor(config.default_selct_color[self.parent.color_index])
        elif self.highlighted:
            colored_pen.setColor(config.default_highlt_color[self.parent.color_index])
        else:
            colored_pen.setColor(config.default_reg_color[self.parent.color_index])

        # draw clock face
        qp.setPen(colored_pen)

        brush = QBrush(config.clock_bg_color[self.parent.color_index])

        if self.parent.parent.clock_type != 'bar':
            # if self.parent.parent.clock_type != 'radar' or self.new_round:
            qp.setPen(colored_pen)
            qp.setBrush(brush)
            qp.drawEllipse(self.center, self.outer_radius, self.outer_radius)


        # draw hands
        if self.parent.parent.clock_type == 'default':
            pen = QPen()
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
            pen = QPen()
            pen.setColor(QColor(0, 0, 0, 0))
            qp.setPen(pen)
            qp.drawEllipse(self.center, self.inner_radius, self.inner_radius)

        elif self.parent.parent.clock_type == 'radar':
            pen = QPen()

            pen.setColor(QColor(0, 0, 0, 0))
            qp.setPen(pen)
            brush.setColor(QColor(255, 255, 255, 255))
            qp.setBrush(brush)
            qp.drawPie(self.inner_rect, self.minute_hand_angles[-1]+20*16, 20 * 16*(len(self.minute_hand_angles)-1))
            for i in range(len(self.minute_hand_angles)-1):
                if self.selected:
                    brush.setColor(QColor(0, 255, 0, 255 * i/4))
                    qp.setBrush(brush)
                elif self.highlighted:
                    brush.setColor(QColor(0, 0, 255, 255 * i/4))
                    qp.setBrush(brush)
                else:
                    brush.setColor(QColor(0, 0, 0, 255 * i/4))
                    qp.setBrush(brush)
                qp.drawPie(self.inner_rect, self.minute_hand_angles[i], 20*16)

            pen.setColor(config.default_hh_color[self.parent.color_index])
            pen.setWidth(2)
            qp.setPen(pen)

            qp.drawLine(self.center, self.hour_hand_point)  # Hour Hand

        elif self.parent.parent.clock_type == 'pac_man':
            pen = QPen()
            pen.setColor(QColor(0, 0, 0, 0))
            qp.setPen(pen)

            if self.selected:
                brush.setColor(config.pac_man_selct_color[self.parent.color_index])

            elif self.highlighted:
                brush.setColor(config.pac_man_highlt_color[self.parent.color_index])
            else:
                brush.setColor(config.pac_man_reg_color[self.parent.color_index])
            qp.setBrush(brush)

            if abs(self.minute_hand_angle) < 100:
                self.color_switch = self.color_switch == False

            if self.color_switch:
                qp.drawEllipse(self.center, self.outer_radius, self.outer_radius)

                brush.setColor(config.clock_bg_color[self.parent.color_index])
                qp.setBrush(brush)

            qp.setBrush(brush)
            qp.drawPie(self.rect, 90*16, self.minute_hand_angle)

            brush.setColor(QColor(0, 0, 0, 0))
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
            pen = QPen()
            pen.setColor(QColor(0, 0, 0, 0))
            qp.setPen(pen)
            qp.drawRect(10, 2, self.inner_radius, self.h - 4)

            brush.setColor(self.palette().color(QPalette.Background))  # redraw background from bar for 'emptying'
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
            brush.setColor(QColor(0, 0, 0, 0))
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
            qp.drawText(self.text_x, self.text_y, self.text)
        self.new_round = False


class HistogramWidget(QWidget):

    def __init__(self, parent):
        super(HistogramWidget, self).__init__()
        self.parent = parent
        self.initUI()
        self.bars = parent.parent.bars

    def initUI(self):
        self.setMinimumSize(200, 100)


    def paintEvent(self, e):
        qp = QPainter()
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

        qp.setPen(QPen(QColor(120, 120, 120), 1))
        qp.setBrush(QBrush(QColor(255, 255, 255)))
        qp.drawRect(0, 0, w - 1, h)

        pen = QPen(QColor(0, 0, 255), 1)
        qp.setPen(pen)
        brush = QBrush(QColor(0, 150, 255))
        qp.setBrush(brush)
        i = 0
        for bar in self.bars:
            qp.drawRect(i * bar_width, h - bar * h_scale, bar_width, h)
            i += 1
        if not self.parent.in_focus:
            qp.fillRect(0,0,self.geometry().width(),self.geometry().height(),QColor(0,0,0,25))


class VerticalSeparator(QWidget):

    def __init__(self):
        super(VerticalSeparator, self).__init__()

        self.initUI()

    def initUI(self):
        self.setMinimumSize(1, 1)
        self.setMaximumWidth(1)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawLine(qp)
        qp.end()

    def drawLine(self, qp):
        # calculate size of histogram from available space
        size = self.size()
        w = size.width()
        h = size.height()

        pen = QPen(QColor(100, 100, 100), 1)
        qp.setPen(pen)
        qp.drawLine(w / 2, 0, w / 2, h)


class HorizontalSeparator(QWidget):

    def __init__(self):
        super(HorizontalSeparator, self).__init__()

        self.initUI()

    def initUI(self):
        self.setMinimumSize(1, 1)
        self.setMaximumHeight(1)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawLine(qp)
        qp.end()

    def drawLine(self, qp):
        # calculate size of histogram from available space
        size = self.size()
        w = size.width()
        h = size.height()

        pen = QPen(QColor(100, 100, 100), 1)
        qp.setPen(pen)
        qp.drawLine(0, h / 2, w, h / 2)


class OldClockWidgit(QWidget):

    def __init__(self, text, parent, filler_clock=False):
        super(OldClockWidgit, self).__init__()

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

        qp = QPainter()
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

        self.center = QPointF(constraint / 2 + center_offset_x, constraint / 2 + center_offset_y)
        self.redraw_text = True

    def draw_clock(self, e, qp):
        if self.parent.parent.clock_type == 'ball':  # initialize functions for drawing "min hand" based on clock design
            def minute_hand_from_angle(angle, radius):
                radius *= 1.22
                if self.selected:
                    brush.setColor(config.ball_mh_selct_color[self.parent.color_index])

                elif self.highlighted:
                    brush.setColor(config.ball_mh_highlt_color[self.parent.color_index])
                else:
                    brush.setColor(config.ball_mh_reg_color[self.parent.color_index])
                qp.setBrush(brush)
                pen.setColor(QColor(0, 0, 0, 0))
                qp.setPen(pen)

                def sign(x):
                    if abs(x) == x:
                        return 1
                    return -1

                angle = (-angle + math.pi * sign(angle)) / math.pi
                size_factor = angle

                qp.drawEllipse(self.center, radius * size_factor, radius * size_factor)

            hour_hand_from_angle = lambda x, y: x

        elif self.parent.parent.clock_type == 'radar':
            if self.parent.parent.high_contrast:
                def clock_color(color_factor):
                    if self.selected:
                        brush.setColor(QColor(0, 255, 0, 255 * color_factor))
                        qp.setBrush(brush)
                    elif self.highlighted:
                        brush.setColor(QColor(255, 0, 0, 255 * color_factor))
                        qp.setBrush(brush)
                    else:
                        brush.setColor(QColor(0, 0, 255, 255 * color_factor))
                        qp.setBrush(brush)
            else:
                def clock_color(color_factor):
                    if self.selected:
                        brush.setColor(QColor(0, 255, 0, 255 * color_factor))
                        qp.setBrush(brush)
                    elif self.highlighted:
                        brush.setColor(QColor(0, 0, 255, 255 * color_factor))
                        qp.setBrush(brush)
                    else:
                        brush.setColor(QColor(0, 0, 0, 255 * color_factor))
                        qp.setBrush(brush)

            def hour_hand_from_angle(angle, radius):
                pen.setColor(config.default_hh_color[self.parent.color_index])
                pen.setWidth(2)
                qp.setPen(pen)

                angle -= math.pi / 2  # reference angle from noon
                radius *= 1.1
                far_point = self.center + QPointF(math.cos(angle) * radius, math.sin(angle) * radius)
                qp.drawLine(self.center, far_point)

                if self.selected:
                    pen.setColor(config.default_selct_color[self.parent.color_index])

                elif self.highlighted:
                    pen.setColor(config.default_highlt_color[self.parent.color_index])
                else:
                    pen.setColor(config.default_reg_color[self.parent.color_index])
                pen.setWidth(3)
                qp.setPen(pen)

            def minute_hand_from_angle(angle, radius):
                radius *= 1.2
                angle *= 180. / math.pi
                angle = 90 - angle
                if angle > 0:
                    angle = -360 + angle
                r = self.radius * (1. - clock_thickness / 2)
                rect = QRect(self.center.x() - r + 1, self.center.y() - r + 1, r * 2., r * 2.)

                n = 8.
                length = math.pi * 2 / 3
                pen.setColor(QColor(0, 0, 0, 0))
                pen.setWidth(1)
                qp.setPen(pen)
                for i in range(int(n)):
                    color_factor = min(1. - float(i) / n, 1.)
                    inc_angle = float(i) * length / n
                    inc_angle = math.degrees(inc_angle)
                    clock_color(color_factor)
                    qp.drawPie(rect, (angle + inc_angle) * 16, (math.degrees(length / n) + 1) * 16)

                pen.setWidth(self.radius * clock_thickness)
                qp.setPen(pen)

        elif self.parent.parent.clock_type == 'pac_man':
            def minute_hand_from_angle(angle, radius):
                angle *= 180. / math.pi
                angle = - angle
                if angle > 0:
                    angle = -360 + angle
                r = self.radius * (1. - clock_thickness / 2)
                rect = QRect(self.center.x() - r + 1, self.center.y() - r + 1, r * 2., r * 2.)

                if self.selected:
                    brush.setColor(config.pac_man_selct_color[self.parent.color_index])

                elif self.highlighted:
                    brush.setColor(config.pac_man_highlt_color[self.parent.color_index])
                else:
                    brush.setColor(config.pac_man_reg_color[self.parent.color_index])
                qp.setBrush(brush)
                pen.setColor(QColor(0, 0, 0, 0))
                qp.setPen(pen)

                if angle > self.previous_angle:
                    self.color_switch = self.color_switch == False

                if self.color_switch:
                    qp.drawEllipse(self.center, self.radius * (1 - clock_thickness / 2),
                                   self.radius * (1 - clock_thickness / 2))

                    brush.setColor(config.clock_bg_color[self.parent.color_index])
                    qp.setBrush(brush)

                self.previous_angle = angle
                qp.drawPie(rect, 90 * 16, angle * 16)

            def hour_hand_from_angle(angle, radius):
                pass

        elif self.parent.parent.clock_type == 'bar':
            def minute_hand_from_angle(angle, radius):
                radius *= 1.22
                if self.selected:
                    brush.setColor(config.bar_mh_selct_color[self.parent.color_index])

                elif self.highlighted:
                    brush.setColor(config.bar_mh_highlt_color[self.parent.color_index])
                else:
                    brush.setColor(config.bar_mh_reg_color[self.parent.color_index])
                qp.setBrush(brush)
                pen.setColor(QColor(0, 0, 0, 0))
                qp.setPen(pen)

                def sign(x):
                    if abs(x) == x:
                        return 1
                    return -1

                angle = (-angle + math.pi * sign(angle)) / math.pi

                qp.drawRect(10, 2, (self.w - 20) * abs(angle), self.h - 4)

            def hour_hand_from_angle(angle, radius):
                if self.selected:
                    pen.setColor(config.bar_hh_selct_color[self.parent.color_index])

                elif self.highlighted:
                    pen.setColor(config.bar_hh_highlt_color[self.parent.color_index])
                else:
                    pen.setColor(config.bar_hh_reg_color[self.parent.color_index])
                pen.setWidth(4)
                qp.setPen(pen)
                qp.drawRect(10, 1, self.w - 20, self.h - 1)

        elif self.parent.parent.clock_type == 'default':

            def minute_hand_from_angle(angle, radius):

                angle -= math.pi / 2  # reference angle from noon

                far_point = self.center + QPointF(math.cos(angle) * radius, math.sin(angle) * radius)
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
        if self.redraw_text:
            self.text_font = QFont(config.clock_font)
            self.text_font.setPixelSize(self.h)
            self.text_font.setStretch(85)
            qp.setFont(self.text_font)

            label = QLabel(self.text)
            label.setFont(self.text_font)
            text_width = label.fontMetrics().boundingRect(label.text()).width()

            if self.parent.parent.clock_type != "bar":
                width = self.w - 2.1 * self.radius
            else:
                width = self.w * 0.7

            size_factor = float(text_width) / (float(width) + 0.1)

            if size_factor > 1:
                if size_factor < 1.3:
                    self.text_font.setStretch(int(85. / size_factor))

                    label = QLabel(self.text)
                    label.setFont(self.text_font)
                    text_width = label.fontMetrics().boundingRect(label.text()).width()
                elif size_factor > 1.3:
                    self.text_font.setStretch(65)
                    label = QLabel(self.text)
                    label.setFont(self.text_font)
                    text_width = label.fontMetrics().boundingRect(label.text()).width()

                    size_factor = float(text_width) / (float(width) + 0.1)
                    self.text_font.setPixelSize(max(1, int(float(self.h) / size_factor)))

                    label = QLabel(self.text)
                    label.setFont(self.text_font)
                    text_width = label.fontMetrics().boundingRect(label.text()).width()

        if self.background:
            brush = QBrush(QColor(175, 255, 175))
            qp.fillRect(0, 0, self.w, self.h, brush)
        # draw clock face
        pen = QPen()
        if self.selected:
            pen.setColor(config.default_selct_color[self.parent.color_index])

        elif self.highlighted:
            pen.setColor(config.default_highlt_color[self.parent.color_index])
        else:
            pen.setColor(config.default_reg_color[self.parent.color_index])
        qp.setPen(pen)

        brush = QBrush(config.clock_bg_color[self.parent.color_index])
        try:
            if not self.parent.in_focus:
                brush = QBrush(QColor(230, 230, 230))
        except AttributeError:
            pass
        pen.setWidth(3)
        qp.setPen(pen)
        qp.setBrush(brush)

        if self.parent.parent.clock_type == 'bar':
            pass
        else:
            qp.drawEllipse(self.center, self.radius * (1 - clock_thickness / 2),
                           self.radius * (1 - clock_thickness / 2))

        # draw hands
        pen.setWidth(self.radius * clock_thickness)
        pen.setCapStyle(Qt.RoundCap)
        qp.setPen(pen)

        hour_hand_from_angle(0, self.radius * 0.7)  # Hour hand

        threshold = 0.025
        if math.sin(self.angle - math.pi / 2) < -1 + threshold:
            if self.highlighted:
                pen.setColor(QColor(0, 255, 255))
            elif not (self.selected):
                pen.setColor(QColor(150, 150, 150))
            qp.setPen(pen)

        minute_hand_from_angle(self.angle + self.start_angle, self.radius * 0.7)  # Minute Hand

        if self.selected:
            pen.setColor(config.default_selct_color[self.parent.color_index])

        elif self.highlighted:
            pen.setColor(config.default_highlt_color[self.parent.color_index])
        else:
            pen.setColor(config.default_reg_color[self.parent.color_index])
        qp.setPen(pen)

        brush = QBrush(QColor(0, 0, 0, 0))
        pen.setWidth(self.radius * clock_thickness)
        qp.setPen(pen)
        qp.setBrush(brush)

        if self.parent.parent.clock_type == 'bar':  # re draw clock border in case painted over
            pass
        else:
            qp.drawEllipse(self.center, self.radius * (1 - clock_thickness / 2),
                           self.radius * (1 - clock_thickness / 2))

        # draw text
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
        if self.redraw_text:
            if self.parent.alignment == 'tc':  # align text according to text layout setting
                x_offest = -text_width / 2
                y_offest = -self.radius * 1.3
            elif self.parent.alignment == 'cr':
                x_offest = self.radius
                y_offest = self.radius * .6
            elif self.parent.alignment == 'cc':
                x_offest = -text_width / 2
                y_offest = self.radius * .6
            elif self.parent.alignment == 'cl':
                x_offest = -self.radius - text_width
                y_offest = self.radius * .6
            elif self.parent.alignment == 'bc':
                x_offest = -text_width / 2
                y_offest = self.radius * 2.3
            self.text_x = self.center.x() + x_offest
            self.text_y = self.center.y() + y_offest

        qp.drawText(self.text_x, self.text_y, self.text)