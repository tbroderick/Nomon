from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
import string

import sys
import config
import kconfig
from pickle_util import PickleUtil
from phrases import Phrases
import os
import zipfile
import numpy as np
import time

from widgets import ClockWidget, HistogramWidget, VerticalSeparator, HorizontalSeparator


# noinspection PyArgumentList,PyAttributeOutsideInit
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, screen_res):
        super(MainWindow, self).__init__()

        self.screen_res = screen_res
        # Load User Preferences

    def init_ui(self):

        self.mainWidget = MainKeyboardWidget(self, self.key_chars, self.screen_res)
        self.mainWidget.init_ui()
        self.setCentralWidget(self.mainWidget)
        self.clock_text_align('auto', message=False)

        # File Menu Actions
        restart_action = QtWidgets.QAction('&Restart', self)
        restart_action.setShortcut('Ctrl+R')
        restart_action.setStatusTip('Restart application')
        # restart_action.triggered.connect(self.restartEvent)

        exit_action = QtWidgets.QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        # exit_action.triggered.connect(QtWidgets.qApp.quit)
        exit_action.triggered.connect(self.closeEvent)

        # Clock Menu Actions
        self.high_contrast_action = QtWidgets.QAction('&High Contrast Mode', self, checkable=True)
        self.high_contrast_action.triggered.connect(lambda: self.high_contrast_event())

        self.default_clock_action = QtWidgets.QAction('&Default (Clock)', self, checkable=True)
        self.default_clock_action.setStatusTip('Regular Nomon clock with sweeping minute hand')
        self.default_clock_action.triggered.connect(lambda: self.clock_change_event('default'))
        self.default_clock_action.setIcon(QtGui.QIcon(os.path.join("icons/", 'default.png')))

        self.radar_clock_action = QtWidgets.QAction('&Radar (Clock)', self, checkable=True)
        self.radar_clock_action.setStatusTip('Nomon clock with sweeping minute hand and radar trails')
        self.radar_clock_action.triggered.connect(lambda: self.clock_change_event('radar'))
        self.radar_clock_action.setIcon(QtGui.QIcon(os.path.join("icons/", 'radar.png')))

        self.ball_clock_action = QtWidgets.QAction('&Ball (Filling)', self, checkable=True)
        self.ball_clock_action.triggered.connect(lambda: self.clock_change_event('ball'))
        self.ball_clock_action.setIcon(QtGui.QIcon(os.path.join("icons/", 'ball.png')))

        self.pacman_clock_action = QtWidgets.QAction('&Pac Man (Filling Pac Man)', self, checkable=True)
        self.pacman_clock_action.triggered.connect(lambda: self.clock_change_event('pac man'))
        self.pacman_clock_action.setIcon(QtGui.QIcon(os.path.join("icons/", 'pac_man.png')))

        self.bar_clock_action = QtWidgets.QAction('&Progress Bar', self, checkable=True)
        self.bar_clock_action.triggered.connect(lambda: self.clock_change_event('bar'))
        self.bar_clock_action.setIcon(QtGui.QIcon(os.path.join("icons/", 'bar.png')))

        # Font Menu Actions
        self.small_font_action = QtWidgets.QAction('&Small', self, checkable=True)
        self.small_font_action.triggered.connect(lambda: self.change_font_size('small'))

        self.med_font_action = QtWidgets.QAction('&Medium (Default)', self, checkable=True)
        self.med_font_action.triggered.connect(lambda: self.change_font_size('med'))

        self.large_font_action = QtWidgets.QAction('&Large', self, checkable=True)
        self.large_font_action.triggered.connect(lambda: self.change_font_size('large'))

        # Text Menu Actions
        self.auto_text_align_action = QtWidgets.QAction('&Auto (Recommended)', self, checkable=True)
        self.auto_text_align_action.triggered.connect(lambda: self.clock_text_align('auto'))

        self.tc_text_align_action = QtWidgets.QAction('&Top Center', self, checkable=True)
        self.tc_text_align_action.triggered.connect(lambda: self.clock_text_align('tc'))

        self.cl_text_align_action = QtWidgets.QAction('&Center Left', self, checkable=True)
        self.cl_text_align_action.triggered.connect(lambda: self.clock_text_align('cl'))

        self.cc_text_align_action = QtWidgets.QAction('&Center', self, checkable=True)
        self.cc_text_align_action.triggered.connect(lambda: self.clock_text_align('cc'))

        self.cr_text_align_action = QtWidgets.QAction('&Center Right', self, checkable=True)
        self.cr_text_align_action.triggered.connect(lambda: self.clock_text_align('cr'))

        self.bc_text_align_action = QtWidgets.QAction('&Bottom Center', self, checkable=True)
        self.bc_text_align_action.triggered.connect(lambda: self.clock_text_align('bc'))

        # Keyboard Layout Menu Actions
        self.default_layout_action = QtWidgets.QAction('&Alphabetical (Default)', self, checkable=True)
        self.default_layout_action.triggered.connect(lambda: self.layout_change_event('alpha'))

        self.qwerty_layout_action = QtWidgets.QAction('&QWERTY', self, checkable=True)
        self.qwerty_layout_action.triggered.connect(lambda: self.layout_change_event('qwerty'))

        # Word Count Action
        self.high_word_action = QtWidgets.QAction('&High (Default)', self, checkable=True)
        self.high_word_action.triggered.connect(lambda: self.word_change_event('high'))

        self.low_word_action = QtWidgets.QAction('&Low (5 Words)', self, checkable=True)
        self.low_word_action.triggered.connect(lambda: self.word_change_event('low'))

        self.off_word_action = QtWidgets.QAction('&Off', self, checkable=True)
        self.off_word_action.triggered.connect(lambda: self.word_change_event('off'))

        # Tools Menu Actions
        # self.profanity_filter_action = QtWidgets.QAction('&Profanity Filter', self, checkable=True)
        # self.profanity_filter_action.triggered.connect(self.profanity_filter_event)

        self.retrain_action = QtWidgets.QAction('&Retrain', self)
        self.retrain_action.triggered.connect(self.retrain_event)

        self.phrase_prompts_action = QtWidgets.QAction('&Study Mode', self, checkable=True)
        self.phrase_prompts_action.triggered.connect(self.phrase_prompts_event)

        self.log_data_action = QtWidgets.QAction('&Data Logging', self, checkable=True)
        self.log_data_action.triggered.connect(self.log_data_event)

        self.compress_data_action = QtWidgets.QAction('&Compress Data', self, checkable=False)
        self.compress_data_action.triggered.connect(self.compress_data_event)

        # Help Menu Actions
        help_action = QtWidgets.QAction('&Help', self)
        help_action.setStatusTip('Nomon help')
        help_action.triggered.connect(self.help_event)

        about_action = QtWidgets.QAction('&About', self)
        about_action.setStatusTip('Application information')
        about_action.triggered.connect(self.about_event)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu('&View')
        view_menu.addAction(self.high_contrast_action)
        clock_menu = view_menu.addMenu('&Clocks')
        clock_menu.addAction(self.default_clock_action)
        clock_menu.addAction(self.radar_clock_action)
        clock_menu.addAction(self.ball_clock_action)
        clock_menu.addAction(self.pacman_clock_action)
        clock_menu.addAction(self.bar_clock_action)
        # text_menu = view_menu.addMenu('&Text Alignment')
        # text_menu.addAction(self.auto_text_align_action)
        # center_text_menu = text_menu.addMenu('&Center')
        # center_text_menu.addAction(self.cl_text_align_action)
        # center_text_menu.addAction(self.cc_text_align_action)
        # center_text_menu.addAction(self.cr_text_align_action)
        font_menu = view_menu.addMenu('&Font Size')
        font_menu.addAction(self.small_font_action)
        font_menu.addAction(self.med_font_action)
        font_menu.addAction(self.large_font_action)
        keyboard_menu = view_menu.addMenu('&Keyboard Layout')
        keyboard_menu.addAction(self.default_layout_action)
        keyboard_menu.addAction(self.qwerty_layout_action)
        # word prediction
        word_menu = view_menu.addMenu('&Word Prediction Frequency')
        word_menu.addAction(self.high_word_action)
        word_menu.addAction(self.low_word_action)
        word_menu.addAction(self.off_word_action)

        tools_menu = menubar.addMenu('&Tools')
        # tools_menu.addAction(self.profanity_filter_action)
        tools_menu.addAction(self.log_data_action)
        tools_menu.addAction(self.phrase_prompts_action)
        tools_menu.addAction(self.retrain_action)
        tools_menu.addAction(self.compress_data_action)

        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(help_action)
        help_menu.addSeparator()
        help_menu.addAction(about_action)

        self.setWindowTitle('Nomon Keyboard')

        self.icon = QtGui.QIcon(os.path.join("icons/", 'nomon.png'))
        self.setWindowIcon(self.icon)
        self.setGeometry(self.screen_res[0] * 0.05, self.screen_res[1] * 0.0675, self.screen_res[0] * 0.9,
                         self.screen_res[1] * 0.85)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)
        self.show()
        self.window_size = (self.size().width(), self.size().height())

        self.check_filemenu()

    def check_filemenu(self):
        def switch(unit, mode):
            if mode == unit.isChecked():
                pass
            else:
                unit.toggle()
        # check clocks
        switch(self.default_clock_action, self.clock_type == 'default')
        switch(self.radar_clock_action, self.clock_type == 'radar')
        switch(self.ball_clock_action, self.clock_type == 'ball')
        switch(self.pacman_clock_action, self.clock_type == 'pac_man')
        switch(self.bar_clock_action, self.clock_type == 'bar')

        # check text alignment
        switch(self.cc_text_align_action, self.alignment == 'cc')
        switch(self.cl_text_align_action, self.alignment == 'cl')
        switch(self.cr_text_align_action, self.alignment == 'cr')
        switch(self.auto_text_align_action, self.mainWidget.text_alignment == 'auto')

        # check profanity
        # switch(self.profanity_filter_action, self.pf_preference == 'on')

        # check log data
        switch(self.log_data_action, self.is_write_data)
        switch(self.phrase_prompts_action, self.phrase_prompts)

        # check font menu
        switch(self.small_font_action, self.font_scale == 0)
        switch(self.med_font_action, self.font_scale == 1)
        switch(self.large_font_action, self.font_scale == 2)

        # check high contrast
        switch(self.high_contrast_action, self.high_contrast)

        # check layout
        switch(self.default_layout_action, self.target_layout == kconfig.alpha_target_layout)
        switch(self.qwerty_layout_action, self.target_layout == kconfig.qwerty_target_layout)

        # check word count
        switch(self.high_word_action, self.word_pred_on == 2)
        switch(self.low_word_action, self.word_pred_on == 1)
        switch(self.off_word_action, self.word_pred_on == 0)

    def word_change_event(self, frequency):
        if frequency == 'high':
            self.word_pred_on = 2
        elif frequency == 'low':
            self.word_pred_on = 1

        elif frequency == 'off':
            self.word_pred_on = 0

        self.check_filemenu()

        self.mainWidget.clocks = []

        self.mainWidget.clear_layout(self.mainWidget.keyboard_grid)
        self.mainWidget.clear_layout(self.mainWidget.words_grid)
        self.mainWidget.laid_out = False
        self.mainWidget.clocks = []
        self.mainWidget.words_grid.deleteLater()
        self.mainWidget.keyboard_grid.deleteLater()
        self.mainWidget.generate_clocks()
        self.draw_words()
        self.mainWidget.layout_clocks()
        self.environment_change = True

    def change_font_size(self, size):
        if size == 'small':
            size = 0
        elif size == 'med':
            size = 1
        elif size == 'large':
            size = 2
        self.font_scale = size
        self.up_handel.safe_save([self.clock_type, size, self.high_contrast, self.layout_preference, self.pf_preference,
                                  self.start_speed, self.is_write_data])

        self.mainWidget.sldLabel.setFont(config.top_bar_font[size])
        self.mainWidget.speed_slider_label.setFont(config.top_bar_font[size])
        self.mainWidget.wpm_label.setFont(config.top_bar_font[size])
        self.mainWidget.cb_learn.setFont(config.top_bar_font[size])
        self.mainWidget.cb_pause.setFont(config.top_bar_font[size])
        self.mainWidget.cb_sound.setFont(config.top_bar_font[size])
        self.mainWidget.text_box.setFont(config.text_box_font[size])

        self.mainWidget.wpm_label.update()
        # self.mainWidget.cb_talk.update()
        self.mainWidget.cb_learn.update()
        self.mainWidget.cb_pause.update()
        self.mainWidget.sldLabel.update()
        self.mainWidget.speed_slider_label.update()
        self.mainWidget.text_box.update()

        self.check_filemenu()
        QtCore.QTimer.singleShot(500, self.init_clocks)

    def high_contrast_event(self):

        if self.high_contrast:
            hc_status = False
        else:
            hc_status = True

        self.up_handel.safe_save(
            [self.clock_type, self.font_scale, hc_status, self.layout_preference, self.pf_preference, self.start_speed,
             self.is_write_data])
        self.high_contrast = hc_status
        self.mainWidget.color_index = hc_status
        self.environment_change = True

    def phrase_prompts_event(self):
        if self.phrase_prompts:
            phrase_status = False
        else:
            phrase_status = True

        if self.phrases is None:
            self.phrases = Phrases("resources/comm2.dev")

        self.phrase_prompts = phrase_status
        if phrase_status == True:
            self.phrases.sample()
            self.update_phrases(self.typed_versions[-1], "")

            choice_dict = {"time": time.time(), "undo": False, "backspace": False, "typed": "", "target": self.phrases.cur_phrase}
            self.params_handle_dict['choice'].append(choice_dict)

            self.is_write_data = True

            self.mainWidget.cb_learn.setChecked(True)
            self.mainWidget.cb_pause.setChecked(True)
            self.default_clock_action.trigger()
            self.high_word_action.trigger()
            self.med_font_action.trigger()
            self.default_layout_action.trigger()

            self.mainWidget.cb_learn.setEnabled(False)
            self.mainWidget.cb_pause.setEnabled(False)
            self.mainWidget.speed_slider_label.setStyleSheet('QLabel { color: grey }')
            self.mainWidget.sldLabel.setStyleSheet('QLabel { color: grey }')

            self.default_clock_action.setEnabled(False)
            self.radar_clock_action.setEnabled(False)
            self.ball_clock_action.setEnabled(False)
            self.pacman_clock_action.setEnabled(False)
            self.bar_clock_action.setEnabled(False)
            self.default_layout_action.setEnabled(False)
            self.qwerty_layout_action.setEnabled(False)
            self.high_contrast_action.setEnabled(False)
            self.low_word_action.setEnabled(False)
            self.high_word_action.setEnabled(False)
            self.off_word_action.setEnabled(False)
            self.small_font_action.setEnabled(False)
            self.med_font_action.setEnabled(False)
            self.large_font_action.setEnabled(False)
            self.log_data_action.setEnabled(False)

        else:
            self.typed_versions.append("")
            self.left_context = ""
            self.context = ""
            self.typed = ""
            self.lm_prefix = ""
            self.mainWidget.text_box.setText("")

            self.mainWidget.cb_learn.setEnabled(True)
            self.mainWidget.cb_pause.setEnabled(True)
            self.mainWidget.speed_slider.setEnabled(True)

            self.default_clock_action.setEnabled(True)
            self.radar_clock_action.setEnabled(True)
            self.ball_clock_action.setEnabled(True)
            self.pacman_clock_action.setEnabled(True)
            self.bar_clock_action.setEnabled(True)
            self.default_layout_action.setEnabled(True)
            self.qwerty_layout_action.setEnabled(True)
            self.high_contrast_action.setEnabled(True)
            self.low_word_action.setEnabled(True)
            self.high_word_action.setEnabled(True)
            self.off_word_action.setEnabled(True)
            self.small_font_action.setEnabled(True)
            self.med_font_action.setEnabled(True)
            self.large_font_action.setEnabled(True)
            self.log_data_action.setEnabled(True)

            self.mainWidget.speed_slider_label.setStyleSheet('QLabel { color: black }')
            self.mainWidget.sldLabel.setStyleSheet('QLabel { color: black }')
            self.mainWidget.error_label.setStyleSheet("color: rgb(0, 0, 0);")
            self.mainWidget.wpm_label.setStyleSheet("color: rgb(0, 0, 0);")

            self.mainWidget.wpm_label.setText("Words/Min: " + "----")
            self.mainWidget.error_label.setText("Error Rate: " + "----")


        self.check_filemenu()

    def clock_change_event(self, design):
        message_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Change Clock Design", "This will change the clocks "
                                                                                         "to the <b>" + design + "</b"
                                                                                         "> design",
                                       QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
        design = design.replace(' ', '_')
        message_box.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        message_box.setIconPixmap(QtGui.QPixmap(os.path.join("icons/", design + '.png')))
        message_box.setWindowIcon(self.icon)

        self.clock_type = design
        self.up_handel.safe_save([design, self.font_scale, self.high_contrast, self.layout_preference,
                                  self.pf_preference, self.start_speed, self.is_write_data])
        self.check_filemenu()

        if self.mainWidget.text_alignment == 'auto':
            self.clock_text_align('auto', message=False)
            self.check_filemenu()

        QtCore.QTimer.singleShot(100, self.init_clocks)
        self.environment_change = True

    def layout_change_event(self, layout):
        message_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Change Keyboard Layout", "This will change the clock "
                                                                                         "layout to <b>" + layout + "</b"
                                                                                         "> order. <b>NOTICE:</b> You "
                                                                                         "will have to restart Nomon for"
                                                                                         " these changes to take effect",
                                       QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
        message_box.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        message_box.setWindowIcon(self.icon)

        
        if layout == 'alpha':
            self.up_handel.safe_save([self.clock_type, self.font_scale, self.high_contrast, 'alpha',
                                      self.pf_preference, self.start_speed, self.is_write_data])
            self.target_layout = kconfig.alpha_target_layout

        elif layout == 'qwerty':
            self.up_handel.safe_save([self.clock_type, self.font_scale, self.high_contrast, 'qwerty',
                                      self.pf_preference, self.start_speed, self.is_write_data])
            self.target_layout = kconfig.qwerty_target_layout

        self.layout_preference = layout
        self.check_filemenu()

        self.in_pause = True
        self.mainWidget.clocks = []

        self.mainWidget.clear_layout(self.mainWidget.keyboard_grid)
        self.mainWidget.clear_layout(self.mainWidget.words_grid)
        self.mainWidget.words_grid.deleteLater()
        self.mainWidget.keyboard_grid.deleteLater()
        self.mainWidget.generate_clocks()
        self.mainWidget.layout_clocks()

        QtCore.QTimer.singleShot(100, self.init_clocks)
        self.in_pause = False
        self.environment_change = True

    def clock_text_align(self, alignment, message=True):
        if alignment == "auto":
            self.mainWidget.text_alignment = 'auto'
            message_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Change Text Alignment", "The text will be <b>"
                                                                                               "Auto-Aligned</b> to "
                                                                                               "best suit the keyboard"
                                                                                               " layout. (recommended)",
                                           QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
            if self.clock_type == "bar":
                alignment = "cc"
            else:
                alignment = "cr"
        else:
            self.mainWidget.text_alignment = alignment
            alignment_name = ""
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

            message_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Change Text Alignment", "This will change the "
                                      "text to be aligned on the <b>" + alignment_name + "</b>  of the clocks",
                                      QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
        self.alignment = alignment

        self.mainWidget.alignment = alignment
        self.resize_clocks()
        if message:
            self.check_filemenu()
            QtCore.QTimer.singleShot(100, self.init_clocks)

    def resize_clocks(self):
        if self.alignment[0] == 'b' or self.mainWidget.alignment[0] == 't':
            for clock in self.mainWidget.clocks:
                clock.setMaximumHeight(clock.maxSize*2)
                # clock.setMinimumSize(clock.minSize*2.1, clock.minSize*2.1)
        else:
            for clock in self.mainWidget.clocks:
                clock.setMaximumHeight(clock.maxSize)
                # clock.setMinimumSize(clock.minSize, clock.minSize)

    def log_data_event(self):
        message_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Data Logging Consent", "We would like to save "
                                  "some data regarding your clicking time relative to Noon to help us improve Nomon. "
                                  "All data collected is anonymous and only your click times will be saved. <b> Do you"
                                  " consent to allowing us to log click timing data locally?</b> (Note: you can change"
                                  " your preference anytime in the Tools menu).")
        message_box.addButton(QtWidgets.QMessageBox.Yes)
        message_box.addButton(QtWidgets.QMessageBox.No)
        message_box.setDefaultButton(QtWidgets.QMessageBox.Yes)
        message_box.setWindowIcon(self.icon)

        reply = message_box.exec_()
        
        if reply == QtWidgets.QMessageBox.No:
            self.up_handel.safe_save(
                [self.clock_type, self.font_scale, self.high_contrast, self.layout_preference, self.pf_preference,
                 self.start_speed, False])
            self.is_write_data = False
        elif reply == QtWidgets.QMessageBox.Yes:
            self.up_handel.safe_save(
                [self.clock_type, self.font_scale, self.high_contrast, self.layout_preference, self.pf_preference,
                 self.start_speed, True])
            self.is_write_data = True
        self.check_filemenu()

    def compress_data_event(self):
        self.bc.save_when_quit()
        data_save_path, _ = os.path.split(self.data_path)
        data_zip_path = os.path.join(data_save_path, "nomon_data.zip")
        zf = zipfile.ZipFile(data_zip_path, "w")
        for dirname, subdirs, files in os.walk(self.data_path):
            sub_dirname = dirname[len(self.data_path):]

            zf.write(dirname, sub_dirname)
            for filename in files:
                file_path = os.path.join(dirname, filename)
                sub_file_path = file_path[len(self.data_path):]
                zf.write(file_path, sub_file_path)
        zf.close()

        message_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Data Compression", "We have compressed your data into a ZIP"
                                                                           " archive accessible in the location"
                                                                           "listed under \"Details\". Please press \""
                                                                           "Show Details\", and email the "
                                                                           "ZIP archive to the listed email address. We"
                                                                           " greatly appreciate your willingness to "
                                                                           "help us make Nomon better!")
        message_box.setDetailedText("File Path: \n" + data_save_path + "\n\n Email: \nnomonstudy@gmail.com")
        message_box.addButton(QtWidgets.QMessageBox.Ok)
        message_box.setWindowIcon(self.icon)

        reply = message_box.exec_()

    # def profanity_filter_event(self):
    #     profanity_status = self.pf_preference
    #     messageBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Profanity Filter Settings", "The profanity filter is"
    #                                                                                            " currently <b>"
    #                                    + self.pf_preference.upper() + "</b>. Please select your desired setting "
    #                                                                   "below. ")
    #     messageBox.addButton(QtWidgets.QPushButton('On'), QtWidgets.QMessageBox.YesRole)
    #     messageBox.addButton(QtWidgets.QPushButton('Off'), QtWidgets.QMessageBox.NoRole)
    #     messageBox.setIconPixmap(QtWidgets.QPixmap(os.path.join('icons/block.png')))
    #
    #     messageBox.setDefaultButton(QtWidgets.QMessageBox.No)
    #     messageBox.setWindowIcon(self.icon)
    #
    #     reply = messageBox.exec_()
    #
    #     if reply == 1:
    #         self.up_handel.safe_save(
    #             [self.clock_type, self.font_scale, self.high_contrast, self.layout_preference, 'off', self.start_speed,
    #              self.is_write_data])
    #         if profanity_status == 'on':
    #             train_handle = open(kconfig.train_file_name_default, 'r')
    #             self.pause_animation = True
    #             self.dt = dtree.DTree(train_handle, self)
    #         self.pf_preference = 'off'
    #     elif reply == 0:
    #         self.up_handel.safe_save(
    #             [self.clock_type, self.font_scale, self.high_contrast, self.layout_preference, 'on', self.start_speed,
    #              self.is_write_data])
    #         if profanity_status == 'off':
    #             train_handle = open(kconfig.train_file_name_censored, 'r')
    #             self.pause_animation = True
    #             self.dt = dtree.DTree(train_handle, self)
    #         self.pf_preference = 'on'
    #     self.check_filemenu()

    def about_event(self):
        # noinspection PyTypeChecker
        QtWidgets.QMessageBox.question(self, 'About Nomon', " Copyright 2019 Nicholas Bonaker, Keith Vertanen,"
                                                            " Emli-Mari Nel, Tamara Broderick. This file is part of "
                                                            "the Nomon software. Nomon is free software: you can "
                                                            "redistribute it and/or modify it under the terms of the "
                                                            "MIT License reproduced below.\n\n "
                                                            "Permission is hereby granted, free of charge, to any "
                                                            "person obtaining a copy of this software and associated"
                                                            " documentation files (the \"Software\"), to deal in the"
                                                            " Software without restriction, including without "
                                                            "limitation the rights to use, copy, modify, merge, "
                                                            "publish, distribute, sublicense, and/or sell copies of the"
                                                            " Software,and to permit persons to whom the Software is"
                                                            " furnished to do so, subject to the following conditions: "
                                                            "The above copyright notice and this permission notice"
                                                            " shall be included in all copies or substantial portions"
                                                            " of the Software. \n\n "
                                                            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY" 
                                                            "OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT"
                                                            " LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS"
                                                            " FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO"
                                                            " EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE"
                                                            " LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,"
                                                            " WHETHER IN AN ACTION OF CONTRACT, TORT OR"
                                                            " OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION"
                                                            " WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS"
                                                            " IN THE SOFTWARE.\n\n"
                                                            " <https://opensource.org/licenses/mit-license.html>",
                                       QtWidgets.QMessageBox.Ok)

    def help_event(self):
        self.launch_help()

    def retrain_event(self):
        self.launch_retrain()

    def resizeEvent(self, event):
        self.environment_change = True
        self.in_pause = True
        for clock in self.mainWidget.clocks:
            clock.redraw_text = True
            clock.calculate_clock_size()
        QtCore.QTimer.singleShot(100, self.init_clocks)
        QtWidgets.QMainWindow.resizeEvent(self, event)
        self.window_size = (self.size().width(), self.size().height())
        self.in_pause = False



class MainKeyboardWidget(QtWidgets.QWidget):

    def __init__(self, parent, layout, screen_res):
        super(MainKeyboardWidget, self).__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.parent = parent
        self.layout = layout
        self.screen_res = screen_res
        self.size_factor = min(self.screen_res) / 1080.
        self.text_alignment = 'auto'
        self.alignment = 'cr'
        self.in_focus = True
        self.color_index = self.parent.high_contrast
        self.reduced_word_clocks = [ClockWidget('INIT', self) for i in range(self.parent.reduce_display)]

    # noinspection PyUnresolvedReferences
    def init_ui(self):

        # generate slider for clock rotation speed
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.speed_slider.setRange(config.scale_min, config.scale_max)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.setValue(self.parent.start_speed)
        self.speed_slider_label = QtWidgets.QLabel('Clock Rotation Speed:')

        self.speed_slider_label.setFont(config.top_bar_font[self.parent.font_scale])
        self.sldLabel = QtWidgets.QLabel(str(self.speed_slider.value()))
        self.sldLabel.setFont(config.top_bar_font[self.parent.font_scale])

        # wpm label
        self.wpm_label = QtWidgets.QLabel("Words/Min: "+"----")
        self.wpm_label.setFont(config.top_bar_font[self.parent.font_scale])

        self.error_label = QtWidgets.QLabel("Error Rate: " + "----")
        self.error_label.setFont(config.top_bar_font[self.parent.font_scale])

        # generate learn, speak, talk checkboxes
        # self.cb_talk = QtWidgets.QCheckBox('Talk', self)
        self.cb_learn = QtWidgets.QCheckBox('Learn', self)
        self.cb_pause = QtWidgets.QCheckBox('Pause', self)
        self.cb_sound = QtWidgets.QCheckBox('Sound', self)
        # self.cb_talk.toggle()
        # self.cb_talk.setFont(config.top_bar_font[self.parent.font_scale])
        self.cb_learn.toggle()
        self.cb_learn.setFont(config.top_bar_font[self.parent.font_scale])
        self.cb_pause.toggle()
        self.cb_pause.setFont(config.top_bar_font[self.parent.font_scale])
        self.cb_sound.toggle()
        self.cb_sound.setFont(config.top_bar_font[self.parent.font_scale])

        # generate clocks from layout
        self.generate_clocks()

        self.text_box = QtWidgets.QTextEdit("", self)

        self.text_box.setFont(config.text_box_font[self.parent.font_scale])
        self.text_box.setMinimumSize(300, 100)
        self.text_box.setReadOnly(True)

        # generate histogram
        self.histogram = HistogramWidget(self)

        self.speed_slider.valueChanged[int].connect(self.change_value)
        self.cb_learn.toggled[bool].connect(self.parent.toggle_learn_button)
        self.cb_pause.toggled[bool].connect(self.parent.toggle_pause_button)
        # self.cb_talk.toggled[bool].connect(self.parent.toggle_talk_button)
        self.cb_sound.toggled[bool].connect(self.parent.toggle_sound_button)

        # layout slider and checkboxes
        top_hbox = QtWidgets.QHBoxLayout()
        top_hbox.addWidget(self.speed_slider_label, 1)
        top_hbox.addStretch(1)
        top_hbox.addWidget(self.speed_slider, 16)
        top_hbox.addStretch(1)
        top_hbox.addWidget(self.sldLabel, 1)
        top_hbox.addStretch(2)


        # entry metrics vbox
        text_stat_vbox = QtWidgets.QVBoxLayout()
        text_stat_vbox.addWidget(self.wpm_label)
        text_stat_vbox.addWidget(self.error_label)

        top_hbox.addLayout(text_stat_vbox)
        top_hbox.addStretch(5)

        # top_hbox.addWidget(self.cb_talk, 1)
        top_hbox.addWidget(self.cb_learn, 1)
        top_hbox.addWidget(self.cb_pause, 1)
        top_hbox.addWidget(self.cb_sound, 1)
        top_hbox.addStretch(1)

        # stack layouts vertically
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setSpacing(0)
        self.vbox.addLayout(top_hbox)
        self.vbox.addStretch(1)
        self.vbox.addWidget(HorizontalSeparator())

        self.splitter1 = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter1.addWidget(self.text_box)
        self.splitter1.addWidget(self.histogram)
        self.splitter1.setSizes([1, 1])
        self.histogram.setMaximumHeight(160 * self.size_factor)
        self.text_box.setMaximumHeight(160 * self.size_factor)

        self.vbox.addSpacing(5)
        self.vbox.addWidget(self.splitter1, 4)
        self.layout_clocks()
        self.setLayout(self.vbox)

        self.frame_timer = QtCore.QTimer()
        self.frame_timer.timeout.connect(self.parent.on_timer)
        self.frame_timer.start(config.ideal_wait_s * 1000)

        self.data_save_timer = QtCore.QTimer()
        self.data_save_timer.timeout.connect(self.parent.data_auto_save)
        self.data_save_timer.start(config.auto_save_time * 60000)

        self.pause_timer = QtCore.QTimer()
        self.pause_timer.setSingleShot(True)
        self.pause_timer.timeout.connect(self.parent.end_pause)

        self.highlight_timer = QtCore.QTimer()
        self.highlight_timer.setSingleShot(True)
        self.highlight_timer.timeout.connect(self.parent.end_highlight)

        # Tool Tips
        # noinspection PyCallByClass
        QtWidgets.QToolTip.setFont(QtGui.QFont('Monospace', 12))
        self.setToolTip("This is the Nomon Keyboard. To select an option, \n "
                        "find the clock immediately to its left. Press the \n"
                        "spacebar when the moving hand is near noon.")
        self.speed_slider_label.setToolTip("This slider scales the speed of clock rotation. Higher \nvalues correspond "
                                           "to the clock hand moving faster.")
        self.speed_slider.setToolTip("This slider scales the speed of clock rotation. Higher \n"
                                     "values correspond to the clock hand moving faster.")
        self.cb_pause.setToolTip("If this button is checked, there will be a brief \n"
                                 "pause and minty screen flash after each selection \n"
                                 "you make.")
        # self.cb_talk.setToolTip("If this button is checked and if you have festival \n"
        #                         "installed and working on your system, there will be \n"
        #                         "spoken feedback after each selection you make.")
        self.cb_learn.setToolTip("If this button is checked, the program will adapt \n"
                                 "to how you click around noon (illustrated in the \n"
                                 "histogram below).")
        self.histogram.setToolTip("This is Nomon's estimate of where you click relative \n"
                                  "to noon on the clocks. The thinner the distribution, \n"
                                  "the more precisely Nomon thinks you are clicking.")

        self.setMinimumWidth(800*self.size_factor)

        if self.parent.phrase_prompts:
            self.parent.phrases.sample()
            self.parent.update_phrases("")

    def paintEvent(self, e):
        if (self.parent.pretrain or self.parent.pause_animation) and self.in_focus:
            qp = QtGui.QPainter()
            qp.begin(self)
            brush = qp.brush()
            brush.setColor(QtGui.QColor(0, 0, 0, 10))
            qp.setBrush(brush)
            qp.fillRect(0, 0, self.geometry().width(), self.geometry().height(),QtGui.QColor(220,220,220))
            qp.end()
            self.text_box.setStyleSheet("background-color:#e6e6e6;")
            self.splitter1.setStyleSheet("background-color:#e0e0e0;")
            self.in_focus = False
            for clock in self.clocks:
                clock.in_focus = False
                clock.redraw_text = True
                clock.update()
        elif not self.in_focus and not (self.parent.pretrain or self.parent.pause_animation):
            self.text_box.setStyleSheet("background-color:;")
            self.splitter1.setStyleSheet("background-color:;")
            self.in_focus = True
            for clock in self.clocks:
                clock.in_focus = True
                clock.redraw_text = True
                clock.update()

    def change_value(self, value):  # Change clock speed
        if self.parent.phrase_prompts:
            inc_dir = np.sign(value - self.parent.rotate_index)
            value = self.parent.rotate_index + inc_dir
            self.speed_slider.setValue(value)
            self.speed_slider.setEnabled(False)
            self.speed_slider_label.setStyleSheet('QLabel { color: grey }')
            self.sldLabel.setStyleSheet('QLabel { color: grey }')

        self.sldLabel.setText(str(self.speed_slider.value()))
        self.parent.change_speed(value)
        self.parent.rotate_index = value

    def get_words(self, char):  # Reformat word list into blueprint for GUI construction
        i = 0
        output = []
        for word in self.parent.word_list:
            index = len(self.parent.context)
            
            if word[index] == char:
                i += 1
                if i > 3:
                    break
                if word not in output:
                    output += [word]
        return output

    def generate_clocks(self):  # Generate the clock widgets according to blueprint from self.get_words
        self.reduced_word_clocks = [ClockWidget('INIT', self) for i in range(self.parent.reduce_display)]
        self.clocks = []
        for row in self.layout:
            for text in row:
                if text == kconfig.mybad_char:
                    text = "Undo"
                elif text == kconfig.back_char:
                    text = "Backspace"
                elif text == kconfig.clear_char:
                    text = "Clear"
                elif text == " ":
                    text = "_"
                clock = ClockWidget(text, self)
                clock.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
                words = self.get_words(clock.text.lower())
                
                word_clocks = ['' for i in range(kconfig.N_pred)]
                i = 0
                for word in words:
                    if word[:-1] in list(string.ascii_letters):
                        word = word[0]+"_"
                    clockf = ClockWidget(word, self)
                    clockf.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
                    word_clocks[i] = clockf

                    i += 1
                for n in range(i, kconfig.N_pred):
                    clockf = ClockWidget('', self, filler_clock=True)
                    clockf.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
                    word_clocks[n] = clockf
                self.clocks += word_clocks
                self.clocks += [clock]

    def update_clocks(self):  # Used to change text and turn off clocks after initialization
        index = 0
        word_clocks = []
        for row in self.layout:
            for text in row:
                if text == kconfig.mybad_char:
                    text = "Undo"
                elif text == kconfig.back_char:
                    text = "Backspace"
                elif text == kconfig.clear_char:
                    text = "Clear"
                elif text == " ":
                    text = "_"
                words = self.get_words(text.lower())
                for word in words:
                    if word[:-1] in list(string.ascii_letters):
                        word = word[0]+"_"
                    if self.parent.word_pred_on == 1:
                        word_clocks += [self.clocks[index]]
                    self.clocks[index].filler_clock = False
                    self.clocks[index].set_text(word)
                    index += 1
                for i in range(len(words), 3):
                    self.clocks[index].set_text('')
                    self.clocks[index].filler_clock = True
                    self.clocks[index].update()
                    index += 1
                self.clocks[index].set_text(text)
                index += 1

        if self.parent.word_pred_on == 1:
            word_clocks = word_clocks[:5]
            print(word_clocks)
            self.reduced_word_clock_indices = [self.clocks.index(clock) for clock in word_clocks]
            for clock_num in range(len(word_clocks)):
                shadow_clock = self.reduced_word_clocks[clock_num]
                true_clock = self.clocks[self.reduced_word_clock_indices[clock_num]]

                shadow_clock.set_text(true_clock.text)
                shadow_clock.filler_clock = False
            for clock_num in range(len(word_clocks), 5):
                shadow_clock = self.reduced_word_clocks[clock_num]
                shadow_clock.filler_clock = True
                shadow_clock.set_text("")
                shadow_clock.background = False
                shadow_clock.repaint()

        QtCore.QTimer.singleShot(200, self.parent.init_clocks)

    def layout_clocks(self):  # called after self.generate_clocks, arranges clocks in grid
        qwerty = (self.parent.layout_preference == 'qwerty')
        target_layout_list = [j for i in self.parent.target_layout for j in i]
        combine_back_clocks = 'BACKUNIT' in target_layout_list
        combine_space_clocks = 'SPACEUNIT' in target_layout_list
        combine_break_clocks = 'BREAKUNIT' in target_layout_list
        # layout keyboard in grid
        self.keyboard_grid = QtWidgets.QGridLayout()
        self.punctuation_grid = QtWidgets.QGridLayout()
        self.back_clear_vbox = QtWidgets.QVBoxLayout()

        def make_grid_unit(main_clock, sub_clocks=None):
            key_grid = QtWidgets.QGridLayout()
            if self.parent.word_pred_on == 2:
                if sub_clocks is not None:
                    if qwerty:
                        key_grid.addWidget(VerticalSeparator(), 0, 0, 6, 1)
                        key_grid.addWidget(VerticalSeparator(), 0, 2, 6, 1)
                        key_grid.addWidget(HorizontalSeparator(), 0, 0, 1, 2)
                        key_grid.addWidget(HorizontalSeparator(), 6, 0, 1, 2)
                        key_grid.addWidget(main_clock, 1, 1)
                        clock_index = 0
                        for sub_clock in sub_clocks:
                            key_grid.addWidget(sub_clock, 2 + clock_index, 1)
                            clock_index += 1
                        for row in range(4):
                            key_grid.setRowStretch(row+1, 2)
                    else:
                        key_grid.addWidget(VerticalSeparator(), 0, 0, 4, 1)
                        key_grid.addWidget(VerticalSeparator(), 0, 3, 4, 1)
                        key_grid.addWidget(HorizontalSeparator(), 0, 0, 1, 3)
                        key_grid.addWidget(HorizontalSeparator(), 4, 0, 1, 3)
                        key_grid.addWidget(main_clock, 1, 1, 3, 1)
                        clock_index = 0
                        for sub_clock in sub_clocks:
                            key_grid.addWidget(sub_clock, 1+clock_index, 2)
                            clock_index += 1
                        key_grid.setColumnStretch(1, 4)
                        key_grid.setColumnStretch(2, 5)
                else:
                    key_grid.addWidget(VerticalSeparator(), 0, 0, 4, 1)
                    key_grid.addWidget(VerticalSeparator(), 0, 3, 4, 1)
                    key_grid.addWidget(HorizontalSeparator(), 0, 0, 1, 3)
                    key_grid.addWidget(HorizontalSeparator(), 4, 0, 1, 3)
                    key_grid.addWidget(main_clock, 1, 1, 3, 2)
            else:
                key_grid.addWidget(VerticalSeparator(), 0, 0, 4, 1)
                key_grid.addWidget(VerticalSeparator(), 0, 3, 4, 1)
                key_grid.addWidget(HorizontalSeparator(), 0, 0, 1, 3)
                key_grid.addWidget(HorizontalSeparator(), 4, 0, 1, 3)
                key_grid.addWidget(main_clock, 1, 1, 3, 2)
                key_grid.setColumnStretch(1, 4)
                key_grid.setRowStretch(1, 4)
            return key_grid

        if self.parent.word_pred_on != 2:  # allow clocks to take up more space if fewer words on
            for clock in self.clocks:
                clock.maxSize = round(80 * clock.size_factor)
                clock.setMaximumHeight(clock.maxSize)
                clock.calculate_clock_size()
                self.parent.update_clock_radii()
                clock.update()

        self.grid_units=[]
        clock_index = 0
        break_clocks=[]
        undo_clocks=[]
        space_clocks=[]
        word_clocks = []
        for key in self.parent.key_chars:
            if key in list(string.ascii_letters):
                main_clock = self.clocks[clock_index + kconfig.N_pred]
                sub_clocks = [self.clocks[clock_index + i] for i in range(kconfig.N_pred)]
                clock_index += kconfig.N_pred + 1
            elif key in kconfig.break_chars:
                if combine_break_clocks:
                    break_clocks += [self.clocks[clock_index + kconfig.N_pred]]
                else:
                    main_clock = self.clocks[clock_index + kconfig.N_pred]
                    sub_clocks = []
                clock_index += kconfig.N_pred + 1
            elif key == kconfig.mybad_char:
                undo_clocks += [self.clocks[clock_index + kconfig.N_pred]]
                clock_index += kconfig.N_pred + 1
            elif key in [kconfig.back_char, kconfig.clear_char]:
                if combine_back_clocks:
                    undo_clocks += [self.clocks[clock_index + kconfig.N_pred]]
                else:
                    main_clock = self.clocks[clock_index + kconfig.N_pred]
                    sub_clocks = []
                clock_index += kconfig.N_pred + 1
            elif key in [" ", "\'"]:
                if combine_space_clocks:
                    space_clocks += [self.clocks[clock_index + kconfig.N_pred]]
                else:
                    main_clock = self.clocks[clock_index + kconfig.N_pred]
                    sub_clocks = []
                clock_index += kconfig.N_pred + 1
            else:
                main_clock = self.clocks[clock_index + kconfig.N_pred]
                sub_clocks = []
                clock_index += kconfig.N_pred + 1
            word_clocks += [clock for clock in sub_clocks if clock.text != '']
            self.grid_units += [make_grid_unit(main_clock, sub_clocks)]

        # make break unit:
        if combine_break_clocks:
            self.break_unit = QtWidgets.QGridLayout()
            i = 1
            for clock in break_clocks:

                self.break_unit.addWidget(VerticalSeparator(), 0, 0, 4, 1)
                self.break_unit.addWidget(VerticalSeparator(), 0, 3, 4, 1)
                self.break_unit.addWidget(HorizontalSeparator(), 0, 0, 1, 3)
                self.break_unit.addWidget(HorizontalSeparator(), 4, 0, 1, 3)
                if i > 2:
                    col = 2
                else:
                    col = 1

                if i%2:
                    row = 3
                else:
                    row = 1
                self.break_unit.addWidget(clock, row, col)
                self.break_unit.setRowStretch(row, 2)
                i+=1

        # make undo unit
        self.undo_unit = QtWidgets.QGridLayout()
        self.undo_label = QtWidgets.QLabel(self.parent.previous_undo_text)
        undo_font = QtGui.QFont('Consolas', 20)
        undo_font.setStretch(80)
        self.undo_label.setFont(undo_font)

        self.undo_unit.addWidget(VerticalSeparator(), 0, 0, 3, 1)
        self.undo_unit.addWidget(VerticalSeparator(), 0, 2, 3, 1)
        self.undo_unit.addWidget(HorizontalSeparator(), 0, 0, 1, 2)
        self.undo_unit.addWidget(HorizontalSeparator(), 3, 0, 1, 2)
        if combine_back_clocks:
            self.undo_unit.addWidget(undo_clocks[2], 1, 1)
            self.undo_unit.addWidget(self.undo_label, 2, 1)
        else:
            self.undo_unit.addWidget(undo_clocks[0], 1, 1)
            self.undo_unit.addWidget(self.undo_label, 2, 1)

        # make back unit
        if combine_back_clocks:

            self.back_unit = QtWidgets.QGridLayout()
            self.back_unit.addWidget(VerticalSeparator(), 0, 0, 4, 1)
            self.back_unit.addWidget(VerticalSeparator(), 0, 2, 4, 1)
            self.back_unit.addWidget(HorizontalSeparator(), 0, 0, 1, 2)
            self.back_unit.addWidget(HorizontalSeparator(), 4, 0, 1, 2)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(undo_clocks[0], 3)
            vbox.addStretch(1)
            vbox.addWidget(undo_clocks[1], 3)
            self.back_unit.addLayout(vbox, 2, 1)

        # make space ' unit
        if combine_space_clocks:
            self.space_unit = QtWidgets.QGridLayout()
            self.space_unit.addWidget(VerticalSeparator(), 0, 0, 4, 1)
            self.space_unit.addWidget(VerticalSeparator(), 0, 2, 4, 1)
            self.space_unit.addWidget(HorizontalSeparator(), 0, 0, 1, 2)
            self.space_unit.addWidget(HorizontalSeparator(), 4, 0, 1, 2)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(space_clocks[0], 3)
            vbox.addStretch(1)
            vbox.addWidget(space_clocks[1], 3)
            self.space_unit.addLayout(vbox, 2, 1)

        self.layout_from_target(self.parent.target_layout)
        self.vbox.insertLayout(3, self.keyboard_grid, 25)  # add keyboard grid to place in main layout
        self.words_grid = QtWidgets.QHBoxLayout()
        if self.parent.word_pred_on == 1:
            for clock in self.reduced_word_clocks:
                clock.maxSize = round(50 * clock.size_factor)
                clock.setMaximumHeight(clock.maxSize)
                self.words_grid.addWidget(clock)
            self.vbox.insertLayout(4, self.words_grid, 4)
            self.update_clocks()

        self.laid_out = True
        QtCore.QTimer.singleShot(500, self.parent.init_clocks)

    def layout_from_target(self, target_layout):
        qwerty = (self.parent.layout_preference == 'qwerty')
        row_num = 0
        for row in target_layout:
            col_num = 0
            for key in row:
                if key in self.parent.key_chars:
                    if key == kconfig.back_char:
                        if qwerty:
                            self.keyboard_grid.addLayout(self.grid_units[self.parent.key_chars.index(key)], row_num,
                                                         col_num, 1, 3)
                            col_num += 2
                        else:
                            self.keyboard_grid.addLayout(self.grid_units[self.parent.key_chars.index(key)], row_num,
                                                         col_num)
                    if key == kconfig.clear_char:
                        if qwerty:
                            self.keyboard_grid.addLayout(self.grid_units[self.parent.key_chars.index(key)], row_num,
                                                         col_num, 1, 2)
                            col_num += 1
                        else:
                            self.keyboard_grid.addLayout(self.grid_units[self.parent.key_chars.index(key)], row_num,
                                                         col_num)
                    else:
                        self.keyboard_grid.addLayout(self.grid_units[self.parent.key_chars.index(key)], row_num,
                                                     col_num)
                elif key == 'BREAKUNIT':
                    self.keyboard_grid.addLayout(self.break_unit, row_num, col_num)
                elif key == 'UNDOUNIT':
                    if qwerty:
                        self.keyboard_grid.addLayout(self.undo_unit, row_num, col_num, 1, 2)
                        col_num += 1
                    else:
                        self.keyboard_grid.addLayout(self.undo_unit, row_num, col_num)
                elif key == 'BACKUNIT':
                    self.keyboard_grid.addLayout(self.back_unit, row_num, col_num)
                elif key == 'SPACEUNIT':
                    self.keyboard_grid.addLayout(self.space_unit, row_num, col_num)
                col_num += 1

            self.keyboard_grid.setRowStretch(row_num, 1)
            row_num += 1

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child)

    def clear_layout_without_delete(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                layout.removeWidget(child.widget())
                layout.update()
            elif child.layout():
                self.clear_layout(child)

def main():
    print("****************************\n****************************\n[Loading...]")

    app = QtWidgets.QApplication(sys.argv)
    screen_res = (app.desktop().screenGeometry().width(), app.desktop().screenGeometry().height())

    # splash = StartWindow(screen_res, True)
    app.processEvents()
    ex = Keyboard(screen_res, app)

    # if first_load:
    #     ex.first_load = True
    #     welcome = Pretraining(screen_res, ex)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()