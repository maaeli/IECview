from IECview import IECwindow
from silx.gui import qt
from HPLCrun import HPLCrun
from PyQt4.QtCore import pyqtSlot
import numpy


#bufferrun = None
#samplerun = None


@pyqtSlot(int)
def frameSelectedDo(frame):
    window.addOneCurve(samplerun.q,samplerun.I[frame,:], handle = "data", frameNr= frame)
    window.addOneCurve(bufferrun.q,bufferrun.I[frame,:],handle = "buffer",frameNr= frame)
    window.addOneCurve(samplerun.q, samplerun.subI[frame,:],handle = "sub",frameNr= frame)

@pyqtSlot(int)
def diffSelectedDo(diff):
    
    samplerun.subtractBuffer(bufferrun,diff)
    window.addChromo(samplerun.subI.mean(axis=1), handle = "sub", cType= "mean")
    window.addChromo(samplerun.ratio, handle = "ratio", cType= str(diff))
    window.addChromo(samplerun.I0, handle = "I0", cType= "I0")
    window.addChromo(samplerun.Rg, handle = "Rg", cType= "Rg")


def main():   
    global app
    global window
    global samplerun, bufferrun
    app = qt.QApplication([])
    samplerun = HPLCrun("BSA_010.h5")
    bufferrun = HPLCrun("buffer_006.h5")
    samplerun.subtractBuffer(bufferrun)
    # Create a ThreadSafePlot1D, set its limits and display it
    #plot1d = ThreadSafePlot1D()
    #plot1d.setLimits(0., 1000., 0., 1.)
    #plot1d.show()
    
    window = IECwindow()
    window.frameSelected.connect(frameSelectedDo)
    window.diffSelected.connect(diffSelectedDo)
    window.addOneCurve(samplerun.q,samplerun.I[1200,:], handle = "data",frameNr= 1200)
    window.addOneCurve(bufferrun.q,bufferrun.I[1200,:],handle = "buffer",frameNr= 1200)
    window.addChromo(samplerun.sum_I, handle = "data", cType= "sum")
    window.addChromo(bufferrun.sum_I, handle = "buffer", cType= "sum")
    window.addChromo(samplerun.IinQ(1.0), handle = "data", cType= "1nm")
    window.addChromo(bufferrun.IinQ(1.0), handle = "buffer", cType= "1nm")
    window.addChromo(samplerun.subI.mean(axis=1), handle = "sub", cType= "mean")
    window.addChromo(samplerun.ratio, handle = "ratio", cType= "0")
    window.addChromo(samplerun.I0, handle = "I0", cType= "I0")
    window.addChromo(samplerun.Rg, handle = "Rg", cType= "Rg")
    #window.addOneCurve(samplerun.q,samplerun.I[1040,:])
    window.setVisible(True)
    
    # Create the thread that calls ThreadSafePlot1D.addCurveThreadSafe
   # updateThread = UpdateThreadSAXS(window)
    #updateThread.start()  # Start updating the plot

    app.exec_()

   # updateThread.stop()  # Stop updating the plot    
    
if __name__ == '__main__':
    
    main()