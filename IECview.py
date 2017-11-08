
#Questions: 
#Y-scaling which can be turned on and off
# Selct a point (synchronized with frame slider) -> x value
# Select a region -> x values
#recommended reading
#Add plot wihtout updating axis

#boxes: imageview 

from silx.gui import qt
from silx.gui import plot
import numpy
import silx.test.utils
from silx.gui.plot.utils.axis import SyncAxes
import threading
import time
from silx.gui.plot import Plot1D
from silx.gui.widgets.ThreadPoolPushButton import ThreadPoolPushButton
from silx.gui.widgets.WaitingPushButton import WaitingPushButton
from PyQt4.QtGui import QSlider, QLabel
from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import pyqtSlot
import random


class IECwindow(qt.QMainWindow):
     
    updateThread = None
    frameslide = None
    runLength = 0
    
    frameSelected = pyqtSignal(int)
    diffSelected = pyqtSignal(int)

    def __init__(self, parent = None):
        qt.QMainWindow.__init__(self)
        self.setWindowTitle("Plot with synchronized axes")
        widget = qt.QWidget(self)
        self.setCentralWidget(widget)
        self.updateThread = None
        layout = qt.QGridLayout()
        widget.setLayout(layout)
        backend = "mpl"
        #self.plot2d = plot.Plot2D(parent=widget, backend=backend)
        #self.plot2d.setInteractiveMode('pan')
        self.plot1d_chromo = self.createChromoPLot(widget,backend)
        self.plot1d_log = plot.Plot1D(parent=widget, backend=backend)
        self.plot1d_subchromo =  self.createChromoPLot(widget,backend)
        self.plot1d_ratio = self.createChromoPLot(widget,backend)
        self.plot1d_log.getYAxis().setScale("log")
        
        self.frameSlider = self.createFrameSlider(widget)
        self.diffSlider = self.createDiffSlider(widget)
        
     
        self.l1 = QLabel( str(self.plot1d_chromo.getXAxis().getLimits()[0]) + "," + str(self.frameSlider.minimum))
        self.l1.setAlignment(Qt.AlignCenter)
        #self.semi = self.plot1d_log.addCurve(x=self.q,y=I)
        #self.plot1d_loglog.addCurve(x=self.q,y=I)
        #self.plot1d_kratky.addCurve(x=self.q, y=I*self.q*self.q)
        #self.plot1d_holtzer.addCurve(x=self.q, y=I*self.q)
              
        #self.constraint1 = SyncAxes([self.plot2d.getXAxis(), self.plot1d_x1.getXAxis(), self.plot1d_x2.getXAxis()])
        #self.constraint2 = SyncAxes([self.plot2d.getYAxis(), self.plot1d_y1.getYAxis(), self.plot1d_y2.getYAxis()])
        self.constraint3 = SyncAxes([self.plot1d_chromo.getXAxis(), self.plot1d_subchromo.getXAxis(),self.plot1d_ratio.getXAxis()])
        #self.constraint3 = SyncAxes([self.plot1d_chromo.getXAxis(), self.plot1d_ratio.getXAxis()])
        #self.constraint1 = SyncAxes([self.plot1d_log.getXAxis(), self.plot1d_loglog.getXAxis(),self.plot1d_kratky.getXAxis(),self.plot1d_holtzer.getXAxis()], syncScale=False)

        #self.plot1d_kratky.getYAxis().setLimits(0,medfilt(I*self.q*self.q,21).max())
        layout.addWidget(self.plot1d_chromo, 0, 0)
        layout.addWidget(self.plot1d_log, 0, 1)
        
        layout.addWidget(self.frameSlider,1,0)
        layout.addWidget(self.diffSlider,2,0)
        layout.addWidget(self.plot1d_subchromo, 3, 0)
        layout.addWidget(self.plot1d_ratio, 3, 1)
        layout.addWidget(self.l1)
    
    def createCenteredLabel(self, text):
        label = qt.QLabel(self)
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
        self.frameslide  = QSlider(Qt.Horizontal,parent=widget )
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
        self.diffslide  = QSlider(Qt.Horizontal,parent=widget )
        self.diffslide.setMinimum(0)
        self.diffslide.setMaximum(3000)
        self.diffslide.setValue(0)
        self.diffslide.valueChanged.connect(self.diffSelectedDo)
        #self.frameslide.sigLimitsChanged.connect(self.frameRangeChange)
        return self.diffslide  
    
    def diffSelectedDo(self):
        self.plot1d_subchromo.setGraphTitle("Shift " + str(self.diffslide.value()))
        self.diffSelected.emit(self.diffslide.value())   
    
    def addOneCurve(self,q,I, handle, frameNr):
        color = self.getColor(handle)
        self.plot1d_log.addCurve(x=q,y=I,  legend = handle, color= color)
        self.plot1d_log.setGraphTitle("Frame number " + str(frameNr))
        
    def addChromo(self,intensity,handle,cType, yScale = True):
        color = self.getColor(handle)
        runlength = intensity.shape[0]
        if handle in ("data","buffer"):
            self.plot1d_chromo.addCurve(x = numpy.arange(runlength),y=intensity, legend = handle+cType, color = color)
            self.plot1d_chromo.getXAxis().setAutoScale(flag=False)
        if handle in ("sub", "I0", "Rg"):
            self.plot1d_subchromo.addCurve(x = numpy.arange(runlength),y=intensity, legend = handle+cType, color = color)   
            self.plot1d_subchromo.getXAxis().setAutoScale(flag=False)
        if handle in ("ratio"):
            self.plot1d_ratio.addCurve(x = numpy.arange(runlength),y=intensity, legend = handle+cType, color = color)        
            self.plot1d_ratio.getXAxis().setAutoScale(flag=False)
       
    def getColor(self,handle):
        if "data" in handle:
            return "red"
        if "buffer" in handle:
            return "black"
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
    
    

class SyncSlide(QSlider):
    """Synchronize a slider to an axis
    """
    sigLimitsChanged = pyqtSignal(float, float)
    minimum = 0
    maximum = 0
    
    def __init__(self, axes, syncLimits = None, parent = None, *args, **kwargs):
        """
        Constructor
        :param axes: The axis to synchrnoize to
        :param slider: The slider
        """
        super(SyncSlide, self).__init__(parent=parent, *args, **kwargs)
        self.__axes = [axes]
        self.__locked = True
        self.__syncLimits = syncLimits
        self.__callbacks = []

        self.start()
        
#     def setMinimum(self, *args, **kwargs):
#         minimum = args[0]
#         return super(SyncSlide, self).setMinimum(self, *args, **kwargs)
#     
#     def setMaximum(self, *args, **kwargs):
#         maximum = args[0]
#         return super(SyncSlide, self).setMaximum(self, *args, **kwargs)


    def start(self):
        """Start synchronizing axes together.
        The first axis is used as the reference for the first synchronization.
        After that, any changes to any axes will be used to synchronize other
        axes.
        """
        if len(self.__callbacks) != 0:
            raise RuntimeError("Axes already synchronized")

        # register callback for further sync
        axis = self.__axes[0]    
        # the weakref is needed to be able ignore self references
        callback = weakref.WeakMethodProxy(self.__axisLimitsChanged)
        callback = functools.partial(callback, axis)
        sig = axis.sigLimitsChanged
        sig.connect(callback)
        self.__callbacks.append((sig, callback))

        # the weakref is needed to be able ignore self references
        callback = weakref.WeakMethodProxy(self.__axisScaleChanged)
        callback = functools.partial(callback, axis)
        sig = axis.sigScaleChanged
        sig.connect(callback)
        self.__callbacks.append((sig, callback))

        # the weakref is needed to be able ignore self references
        callback = weakref.WeakMethodProxy(self.__axisInvertedChanged)
        callback = functools.partial(callback, axis)
        sig = axis.sigInvertedChanged
        sig.connect(callback)
        self.__callbacks.append((sig, callback))

        # sync the current state
        mainAxis = self.__axes[0]
       
        self.__axisLimitsChanged(mainAxis, *mainAxis.getLimits())
  
        self.__axisScaleChanged(mainAxis, mainAxis.getScale())
   
        self.__axisInvertedChanged(mainAxis, mainAxis.isInverted())

    def stop(self):
        """Stop the synchronization of the axes"""
        if len(self.__callbacks) == 0:
            raise RuntimeError("Axes not synchronized")
        for sig, callback in self.__callbacks:
            sig.disconnect(callback)
        self.__callbacks = []

    def __del__(self):
        """Destructor"""
        # clean up references
        if len(self.__callbacks) != 0:
            self.stop()

    @contextmanager
    def __inhibitSignals(self):
        self.__locked = True
        yield
        self.__locked = False


    def __axisLimitsChanged(self, changedAxis, vmin, vmax):
        if self.__locked:
            return
        with self.__inhibitSignals():
            self.setMinimum(vmin)
            self.setMaximum(vmax)
            self.sigLimitsChanged.emit(vmin,vmax)

    def __axisScaleChanged(self, changedAxis, scale):
        """"
        This does not do anything yet, not sure if it should
        """
        if self.__locked:
            return
        return

    def __axisInvertedChanged(self, changedAxis, isInverted):
        if self.__locked:
            return
        with self.__inhibitSignals():
            self.setInvertedAppearance(isInverted)
            
    
        