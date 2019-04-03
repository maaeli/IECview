from silx.gui import qt
from PyQt4.QtGui import QSlider, QLabel
from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import pyqtSlot
from PyQt4 import QtCore, QtGui

class LabeledSlider(QtGui.QWidget):
    
    valueChanged = pyqtSignal(int, name='valueChanged')
    
    def __init__(self, titel,*var, **kw):
        QtGui.QWidget.__init__(self, *var, **kw)
        self.slider = QtGui.QSlider(parent = self)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.updateCurrent)
        self.minimum = self.slider.minimum()
        self.maximum = self.slider.maximum()
        self._value = self.slider.value()
        self.name = QtGui.QLabel(self)
        self.name.setText(titel)
        self.name.setAlignment(Qt.AlignCenter)
        self.minLabel = QtGui.QLabel(self)
        self.minLabel.setText("")
        self.minLabel.setAlignment(Qt.AlignLeft)
        self.maxLabel = QtGui.QLabel(self)
        self.maxLabel.setText("")
        self.maxLabel.setAlignment(Qt.AlignRight)
        self.valueLabel = QtGui.QLabel(self)
        self.valueLabel.setText(str(self.slider.value()))
        self.valueLabel.setAlignment(Qt.AlignCenter)
  
        self.layout = QtGui.QGridLayout()
        self.layout.setMargin(0)
        self.layout.setSpacing(2)
        self.layout.addWidget(self.name,0,1)
        self.layout.addWidget(self.minLabel,0,0)
        self.layout.addWidget(self.maxLabel,0,2)
        self.layout.addWidget(self.slider,1,0,1,3)
        self.layout.addWidget(self.valueLabel,2,1)
        self.setLayout(self.layout)
        
    def setMinimum(self,minimum):
        self.slider.setMinimum(minimum)
        self.minLabel.setText(str(minimum))
        self.adjustInterval()
        self.minimum = minimum
        
    def setMaximum(self,maximum):
        self.slider.setMaximum(maximum)
        self.maxLabel.setText(str(maximum))
        self.adjustInterval()
        self.maximum = maximum
        
    def adjustInterval(self, numberOfTicks = 6):
        maximum = self.slider.maximum()
        minumum = self.slider.minimum()
        interval = int((maximum - minumum)/numberOfTicks)
        self.slider.setTickInterval (interval)
        
    def setValue(self,value):
        self.slider.setValue(value)
        self._value = value
      
    def updateCurrent(self):
        self._value = self.slider.value()
        self.valueLabel.setText(str(self.slider.value()))
        self.valueChanged.emit(self.slider.value())
        
    def value(self):
        return self.slider.value()
        
        
def test(args):
    app=QtGui.QApplication(args)
    w=LabeledSlider("Test slider")
    w.setMinimum(10)
    w.setMaximum(3000)
    w.show()
    app.exec_()
                                   
if __name__=="__main__":
    import sys
    test(sys.argv)
