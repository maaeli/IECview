
#Questions: 
#Y-scaling which can be turned on and off
# Selct a point (synchronized with frame slider) -> x value
# Select a region -> x values
#recommended reading
#Add plot wihtout updating axis

#boxes: imageview 
from __future__ import division, print_function

from silx.gui import qt
from silx.gui import plot
from numpy import nanmean, nanstd
import silx.test.utils
from silx.gui.plot.utils.axis import SyncAxes
import threading
import time
from silx.gui.plot import Plot1D
from silx.gui.widgets.ThreadPoolPushButton import ThreadPoolPushButton
from silx.gui.widgets.WaitingPushButton import WaitingPushButton
from PyQt4.QtGui import QSlider, QLabel, QPushButton, QFileDialog
from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import pyqtSlot
import random
from labeledSlider import LabeledSlider
from clearButton import ClearButton
from collections import OrderedDict
#from math import inf
# = float('inf')




class IECwindow(qt.QMainWindow):
     
    updateThread = None
    frameslide = None
    runLength = 0
    
    frameSelected = pyqtSignal(int)
    diffSelected = pyqtSignal(int)
    saveFile = pyqtSignal(str)
    #bufferChromLimits = {} #store pairs of maxima and minima
    #sampleChromLimits = {}
    
    

    def __init__(self, parent = None):
        super(IECwindow,self).__init__(parent) #qt.QMainWindow.__init__(self)
        #self.setWindowTitle("Plot with synchronized axes")
        widget = qt.QWidget(self)
        self.setCentralWidget(widget)
        self.updateThread = None
        layout = qt.QGridLayout()
        widget.setLayout(layout)
        backend = "mpl"
        #self.plot2d_cormap = plot.Plot2D(parent=widget, backend=backend)
        #self.plot2d.setInteractiveMode('pan')
        self.plot1d_chromo = self.createChromoPLot(widget,backend)
        self.plot1d_chromo.getYAxis().setLimits(-0.05, 1.05)
        self.plot1d_chromo.getYAxis().setAutoScale(flag=False)
        

        self.plot1d_log = plot.Plot1D(parent=widget, backend=backend)
        self.plot1d_subchromo =  self.createChromoPLot(widget,backend)
        self.plot1d_ratio = self.createChromoPLot(widget,backend)
        self.plot1d_log.getYAxis().setScale("log")
        
        self.frameSlider = self.createFrameSlider(widget)
        self.diffSlider = self.createDiffSlider(widget)
         
        self.saveButton = self.createSaveButton(widget)
     
        self.l1 = QLabel( str(self.plot1d_chromo.getXAxis().getLimits()[0]) + "," + str(self.frameSlider.minimum), parent = widget)
        self.l1.setAlignment(Qt.AlignCenter)
        
        clearAction = ClearButton(self.plot1d_ratio, parent=widget)
        #actions_menu =   self.plot1d_ratio.menuBar().addMenu("Custom actions")  
        toolbar = qt.QToolBar("My toolbar")
        self.plot1d_ratio.addToolBar(toolbar)
        #actions_menu.addAction(clearAction)    
        toolbar.addAction(clearAction)
      
        self.constraint3 = SyncAxes([self.plot1d_chromo.getXAxis(), self.plot1d_subchromo.getXAxis(),self.plot1d_ratio.getXAxis()])#],self.plot2d_cormap.getXAxis(),self.plot2d_cormap.getYAxis()])
        #self.constraint3 = SyncAxes([self.plot1d_chromo.getXAxis(), self.plot1d_ratio.getXAxis()])
        #self.constraint1 = SyncAxes([self.plot1d_log.getXAxis(), self.plot1d_loglog.getXAxis(),self.plot1d_kratky.getXAxis(),self.plot1d_holtzer.getXAxis()], syncScale=False)

        #self.plot1d_kratky.getYAxis().setLimits(0,medfilt(I*self.q*self.q,21).max())
        layout.addWidget(self.plot1d_chromo, 0, 0)
        layout.addWidget(self.plot1d_log, 0, 1,2,1)
        
        layout.addWidget(self.frameSlider,1,0)
        layout.addWidget(self.diffSlider,2,0)
        layout.addWidget(self.plot1d_subchromo, 3, 0)
        layout.addWidget(self.plot1d_ratio, 3, 1)
        layout.addWidget(self.saveButton,4,1)
        #layout.addWidget(self.l1)
        
        currentRoi = self.plot1d_log.getCurvesRoiWidget().getRois()
        print(currentRoi)
        if len(currentRoi) == 0:
            currentRoi = OrderedDict({"low-q range": {"from":0.1, "to":1, "type":"X"}})
        else:
            currentRoi.update({"low-q range": {"from":0.1, "to":1, "type":"X"}})
        print(currentRoi)
        self.plot1d_log.getCurvesRoiWidget().setRois(currentRoi)
    
    def createCenteredLabel(self, text, parent = None):
        label = qt.QLabel(parent)
        label.setAlignment(qt.Qt.AlignCenter)
        label.setText(text)
        return label
    
    def createChromoPLot(self,widget,backend):
        chromo = plot.Plot1D(parent=widget, backend=backend)
        chromo.getXAxis().sigLimitsChanged.connect(self.chromLimitsChanged)
        return chromo
    
    @pyqtSlot(float,float)
    def chromLimitsChanged(self,minv,maxv):
        self.frameslide.setMinimum(int(minv))
        self.frameslide.setMaximum(int(maxv))

    def createFrameSlider(self,widget):
        #self.frameslide  = SyncSlide(self.plot1d_chromo.getXAxis(), Qt.Horizontal,parent=widget )
        self.frameslide  = LabeledSlider("Frame Number", parent=widget)#(Qt.Horizontal,parent=widget )
        self.frameslide.setMinimum(0)
        self.frameslide.setMaximum(3000)
        self.frameslide.setValue(1200)
        self.frameslide.valueChanged.connect(self.frameSelectedDo)
        #self.frameslide.sigLimitsChanged.connect(self.frameRangeChange)
        return self.frameslide

    def frameSelectedDo(self):
        self.frameSelected.emit(self.frameslide.value())
   
    def createDiffSlider(self,widget):
        #self.frameslide  = SyncSlide(self.plot1d_chromo.getXAxis(), Qt.Horizontal,parent=widget )
        self.diffslide  = LabeledSlider("Frame shift", parent = widget) #QSlider(Qt.Horizontal,parent=widget )
        self.diffslide.setMinimum(-500)
        self.diffslide.setMaximum(500)
        self.diffslide.setValue(0)
        self.diffslide.valueChanged.connect(self.diffSelectedDo)
        #self.frameslide.sigLimitsChanged.connect(self.frameRangeChange)
        return self.diffslide  
    
    
    def diffSelectedDo(self):
        self.plot1d_subchromo.setGraphTitle("Shift " + str(self.diffslide.value()))
        self.diffSelected.emit(self.diffslide.value())   
    
    def addOneCurve(self,q,I, handle, frameNr):
        color = self.getColor(handle,"curve")
        self.plot1d_log.addCurve(x=q,y=I,  legend = handle, color= color)
        self.plot1d_log.setGraphTitle("Frame number " + str(frameNr))
        
        
    def createSaveButton(self, widget):
        saveB = QPushButton("Save", parent = widget)
        saveB.clicked.connect(self.saveClicked)
        return saveB
        
    def saveClicked(self):  
        name = QFileDialog.getSaveFileName(self, 'Save File')
        self.saveFile.emit(name)
        
    def addChromo(self,intensity,handle,cType, yScale = True):
        
        runlength = intensity.shape[0]
        if handle in ("data","buffer"):
            try:
                color = self.plot1d_chromo.getCurve(handle+cType).getCurrentColor()
            except Exception as err:
                #print(err)
                color = self.getColor(handle,cType)
            #color = self.getColor(handle,cType) 
            self.plot1d_chromo.addCurve(x = range(runlength),y=intensity, legend = handle+cType, color = color)
            self.plot1d_chromo.getXAxis().setAutoScale(flag=False)
           
            #self.plot1d_chromo.getYAxis().setLimits(min(self.bufferChromLimits[0],self.sampleChromLimits[0]), max(self.bufferChromLimits[1],self.sampleChromLimits[1]))
        if handle in ("sub", "I0", "Rg"):
            color = self.getColor(handle,cType)
            self.plot1d_subchromo.addCurve(x = range(runlength),y=intensity, legend = handle+cType, color = color)   
            self.plot1d_subchromo.getXAxis().setAutoScale(flag=False)
        if handle in ("ratio"):
            color = self.getColor(handle,cType)
            self.plot1d_ratio.addCurve(x = range(runlength),y=intensity, legend = handle+cType, color = color)        
            self.plot1d_ratio.getXAxis().setAutoScale(flag=False)
       
    def getColor(self,handle, cType = None):
        if "data" in handle:
            if cType in ("sum","curve"):
                return "red"
            else:
                return "#%06x" % random.randint(0, 0xFFFFFF)
        if "buffer" in handle:
            if cType in ("sum","curve"):
                return "black"
            else:
                return "#%06x" % random.randint(0, 0xFFFFFF)
        if "sub" in handle:
            return "blue"
        if "ratio" in handle:
            return "#%06x" % random.randint(0, 0xFFFFFF)
        if "I0" in handle:
            return "red"
        if "Rg" in handle:
            return "green"
        
    def frameRangeChange(self):
        self.l1.setText( str(self.plot1d_chromo.getXAxis().getLimits()[0]) + "," + str(self.frameSlider.minimum))

        
import functools
import logging
from contextlib import contextmanager
from silx.utils import weakref

_logger = logging.getLogger(__name__)


#class LabeledSlider(QSlider):
    
    

        