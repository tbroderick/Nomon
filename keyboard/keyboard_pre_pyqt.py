from __future__ import division
import sys
import math
import random
import config
import kconfig
from PyQt4 import QtGui, QtCore

import broderclocks
import dtree
import keyboard
# import glob
import string
import time
import numpy

if kconfig.target_evt == kconfig.joy_evt:
    import pygame
import cPickle, pickle
import os
import pre_broderclocks_pyqt
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
from PyQt4.QtGui import QSound


class Keyboard_pre(QtGui.QWidget):
    
    #Added screen_res
    def __init__(self, screen_res):
        super(Keyboard_pre, self).__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.started = 0
        self.screen_res = screen_res
        #MAYBE UNCOMMENT LATER
        #self.size_factor = min(self.screen_res) / 1080.
        
        #Used to be in keyboard_pre.py
        if len(sys.argv) < 3:
             self.user_id = 0
             self.use_num = 0
            # read arguments
        else:
            user_id = string.atoi(sys.argv[1])
            use_num = string.atoi(sys.argv[2])
            self.user_id = user_id
            self.use_num = use_num
            
        
        
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        self.center = centerPoint
        self.radius = kconfig.pre_clock_rad
        
        
        self.w_canvas = kconfig.base_window_width
        self.h_canvas = kconfig.base_window_height
        self.height_bot = 30
        
        
        
        
        #Temporary
        self.in_pause = False
        self.time_rotate = 2.0
        
        #self.gen_canvas()
        
        self.prev_data = None
        #self.file_handle = None
        self.num_presses = 0
        
        
        
        if config.is_write_data:
            print "yeah writing data!"
            self.gen_handle()
            self.num_presses = 0
            #self.file_handle.write("params " + str(config.period_li[config.default_rotate_ind]) + " " + str(config.theta0) + "\n")
            #self.file_handle.write("start " + str(time.time()) + "\n")
        else:
            self.file_handle = None
        
        self.num_stop_training = 20
        
        
#         #IMPLEMENT PBC AND UNCOMMENT!!
        
        
        self.gen_start_page()
        
        
        
        
        self.pbc = pre_broderclocks_pyqt.Pre_broderclocks(self, self.file_handle, self.time_rotate, self.use_num, self.user_id, time.time(), self.prev_data)
#         
        self.wait_s = self.pbc.get_wait()
         ##UNCOMMENT!!!
        self.num_stop_training = self.pbc.hsi.n_training
#         
        
        
        
        
        self.deactivate_press = False
        ### animate ###
        #self.last_anim_call = self.canvas.after(0, self.on_timer)
        
        #def gen_canvas(self):
    def gen_handle(self):
        # file handle
        data_file = "preconfig.pickle"
        #self.file_handle = open(os.path.join(os.getcwd(), data_file),'w')
        self.file_handle = open( data_file,'w')
    
    
            
    def gen_start_page(self):
        self.setGeometry(0,0,self.w_canvas, self.h_canvas)
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        
        self.move(frameGm.topLeft())
        #self.start_text1  = QtGui.QLabel()
        #self.start_text1.setAlignment(QtCore.Qt.AlignCenter)
        #self.center = self.rect().center()
        #screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        #extraqpoint = QtCore.QPoint(self.x() , self.y())
        #self.center = QtGui.QApplication.desktop().screenGeometry(screen).center() - self.frameGeometry().center() + extraqpoint
        #c = self.rect().center()
        #extraqpoint = self.pos()
        self.center = self.rect().center()
        self.x = self.center.x()
        self.y = self.center.y()
        
# =============================================================================
#         resolution = QtGui.QDesktopWidget().screenGeometry()
#          
#         self.center = ((resolution.width() / 2) - (self.frameSize().width() / 2),
#                   (resolution.height() / 2) - (self.frameSize().height() / 2)) 
#         self.x = self.center[0]
#         self.y = self.center[1]
# =============================================================================
        self.v = (0,self.radius)
        
        
        self.ulx = self.x - self.radius
        self.uly = self.y - self.radius
        #lower right corner
        self.lrx = self.x + self.radius
        self.lry = self.y + self.radius
    
        
        
        
        
        
        self.start_text  = QtGui.QLabel("Welcome! \nBefore starting Nomon, please try to click around the red noon hand " + str(self.num_stop_training)  + " times.")
        self.start_text.setAlignment(QtCore.Qt.AlignCenter)
        self.start_text.setAlignment(QtCore.Qt.AlignTop)
        self.start_button = QtGui.QPushButton("Start Training!")
        self.start_button.clicked.connect(self.start_pbc)

        
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addStretch(0.1)
        hbox1.addWidget(self.start_text)
        hbox1.addStretch(0.1)
        #self.hbox1.setAlignment(QtCore.Qt.AlignTop)
        
        #hbox1.addWidget(self.start_text1)
        
        
        hbox2 = QtGui.QHBoxLayout()
        #hbox2.addWidget(self.start_text2)
        #change later
        #hbox2
        
        hbox3 = QtGui.QHBoxLayout()
        hbox3.addStretch(1)
        hbox3.addWidget(self.start_button)
        hbox3.addStretch(1)
        
        vbox = QtGui.QVBoxLayout()
        
        #vbox.addWidget(self.start_text)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox3)
        
# =============================================================================
#         self.pbc = pre_broderclocks_pyqt.Pre_broderclocks(self, self.canvas, self.w_canvas / 2.0, self.h_canvas/2.0, kconfig.pre_clock_rad, \
#                                                     self.file_handle, self.time_rotate, self.use_num, self.user_id, time.time(), self.prev_data)
#         vbox.addLayout(hbox3)
# =============================================================================
        #vbox.addWidget(self.start_button)
        
        self.setLayout(vbox)  
            
            
# =============================================================================
#             hbox = QtGui.QHBoxLayout()
#             hbox.addStretch(1)
#             hbox.addWidget(okButton)
#             #hbox.addWidget(cancelButton)
#             
#             vbox = QtGui.QVBoxLayout()
#             vbox.addStretch(1)
#             vbox.addLayout(hbox)
#             
#             self.setLayout(vbox) 
# =============================================================================
            
            

        
        self.setWindowTitle('Test')
        self.show()
    
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.gen_clock(qp)
        qp.end()
        #Qt.QFrame.paintEvent(self, e)
    
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Space:
            self.on_press()
        self.play()
        
    def play(self):
        sound_file = "bell.mp3"
        QSound.play(sound_file)
    
    def gen_clock(self, qp):
        
        
# =============================================================================
#         x = self.center[0]
#         y = self.center[1]
# =============================================================================
        
        
# =============================================================================
#         #upper left corner
#         radius = kconfig.pre_clock_rad  
#         ulx = x - radius
#         uly = y - radius
#         #lower right corner
#         lrx = x + radius
#         lry = y + radius
#         
# =============================================================================
        #draw clock face
        #self.v = (0,self.radius)
        
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        
        
        qp.setPen(pen)
        qp.setBrush(brush)

        qp.drawEllipse(self.center, self.radius, self.radius)
        #qp.drawEllipse(self.x, self.y, self.radius, self.radius)
        
        
        # draw hands
        clock_thickness = 1
        #pen = QtGui.QPen(QtGui.QColor(0, 0, 0), clock_thickness)
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
                
        pen.setCapStyle(QtCore.Qt.RoundCap)
        qp.setPen(pen)
        
        #HourHand
        qp.drawLine(self.x,self.y,self.v[0]+self.x,self.y + self.v[1])
        
        #NoonHand
        #red
        #QtGui.QPen(QtGui.QColor(0,255,255),  clock_thickness)
        pen = QtGui.QPen(QtCore.Qt.red)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        qp.setPen(pen)
        
        qp.drawLine(self.x,self.y,self.x,self.uly)
     
        
    def gen_next_button(self):
        self.start_button.show()
        self.start_button.setText("Start Nomon!")
        #self.start_button.clicked.disconnect(self.start_pbc)
        

    
    def training_end_message(self):
        self.start_text.setText("Training for your click time has ended! \n Please begin using Nomon.")
        
    
    def start_nomon(self):
        print "quitting"
        self.force_quit()
        #keyboard.main()
        
    
    
    def on_timer(self):
        if not self.in_pause and self.num_presses < self.num_stop_training:
            self.setFocus()
            start_t = time.time()
            self.pbc.increment(start_t)
            self.start_text.setText("Click when the hour hand hits the red noon hand! \n clicks remaining = " + str(self.num_stop_training - self.num_presses))
    
        
        elif self.num_presses == self.num_stop_training:
            self.gen_next_button()
            self.start_text.setText("")
            self.training_end_message()
            self.deactivate_press = True

    
    
# =============================================================================
#     def on_timer(self):
#         if not self.in_pause:
#             start_t = time.time()
#             ####Change this line
#             self.pbc.increment(start_t)
#             
# =============================================================================
    def on_press(self):
        print "pressed!"
        self.setFocus()
        print "focused!"
        if (not self.in_pause) and self.deactivate_press == False:
            print "first if"
            if config.is_write_data:
                print "second if"
                self.num_presses += 1
                #print "Pressed " + str(self.num_presses) + " times"
                #self.file_handle.write("press " + str(time.time()) + " " + str(self.num_presses) + "\n")
            self.pbc.select(time.time())
        
        if self.num_presses == self.num_stop_training:
            print "finished calculating density"
            self.pbc.hsi.calculate_density()
    
    def start_pbc(self):
        if self.started ==0:
            self.start_text.setText("Click when the hour hand hits the red noon hand! \n clicks remaining = " + str(self.num_stop_training - self.num_presses) )
            self.start_button.hide()
            self.frame_timer = QtCore.QTimer()
            self.frame_timer.timeout.connect(self.on_timer)
            self.frame_timer.start(config.ideal_wait_s*1000)
            self.started = 1
            
        else:
            self.start_nomon()
    
    
        
    def force_quit(self):
        ## close write ie
        print "quitting"
        if config.is_write_data:
            try:
                #pickle.dump([self.pbc.hsi.dens_li, self.pbc.hsi.Z, self.pbc.hsi.optimal_bandwith()], self.file_handle, protocol=pickle.HIGHEST_PROTOCOL)
                li = self.pbc.hsi.dens_li
                z = self.pbc.hsi.Z
                pickle.dump([li, z, self.pbc.hsi.opt_sig, self.pbc.hsi.y_li], self.file_handle, protocol=pickle.HIGHEST_PROTOCOL)
                print "I'm quitting and the density is" + str(li)
                print "And the Z is " + str(z)
                #self.file_handle.write("mu0 = " + str())
                self.file_handle.close()
                print "file closed"
            except IOError as (errno,strerror):
                print "I/O error({0}): {1}".format(errno, strerror)
        
        #sys.exit()
        self.deleteLater()
        #QtCore.QCoreApplication.quit()
        #app.quit()
        
        
            
def main():
    from PyQt4.QtCore import pyqtRemoveInputHook
    pyqtRemoveInputHook()
    app = QtGui.QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    screen_res = (app.desktop().screenGeometry().width(), app.desktop().screenGeometry().height())
    keyboard_pre = Keyboard_pre(screen_res)
    
    timer = QtCore.QTimer()
    timer.start(500)  # You may change this if you wish.
    timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
    
    app.exec_()


if __name__ == '__main__':
    main()
            
            
            
        
    