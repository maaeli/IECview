#Questions: how to remember sutractions in orer to compare them?



from __future__ import print_function, division
import h5py
import numpy
from freesas.autorg import autoRg

class HPLCrun:
    
    sum_I = None
    runLength =  None
    
    def __init__(self, h5file = None):
        if h5file:         
            with h5py.File(h5file, "r") as data:
                self.q = numpy.asarray(data['q'])[:]
                self.I = numpy.asarray(data['scattering_I'])
                self.Ierr = numpy.asarray(data['scattering_Stdev'])
                
                if "sum_I" in data.keys():
                    self.sum_I = numpy.asarray(data['sum_I'])
                self.trim()
                
                    
    def trim(self):
        """
        Remove data points of 0 signal from sum_I so that they don't srew up plotting
        """
        if self.sum_I is not None:
            self.sum_I[numpy.where(self.sum_I == 0.0)] = numpy.nan
            self.sum_I = self.sum_I[~numpy.isnan(self.sum_I)]
            self.runLength = self.sum_I.shape[0]
            self.I = self.I[:self.runLength+1,:]
            self.Ierr = self.Ierr[:self.runLength+1,:]
            
            
            
    def IinQ(self, qmin, qmax = None):
        if qmax is None:
            qmax = qmin + 0.1
        imin = numpy.argmin(abs(self.q-qmin))
        imax= numpy.argmin(abs(self.q-qmax))
        return self.I[:,imin:imax].mean(axis = 1) 
    
    def subtractBuffer(self, puffer, diff = 0):
        if diff == 0:
            bufferI = puffer.I
            bufferErr = puffer.Ierr
        else:   
            bufferI = numpy.roll(puffer.I,diff,axis = 0)
            bufferErr = numpy.roll(puffer.Ierr*puffer.Ierr,diff,axis=0)
        self.subI = self.I - bufferI
        self.subI_err = numpy.sqrt(self.Ierr*self.Ierr + bufferErr*bufferErr)
        
        self.subI[numpy.where(self.sum_I is numpy.nan)] = numpy.nan 
        if diff != 0:
            self.subI[0:diff+1,:] = numpy.nan 
            self.subI[min(self.runLength,puffer.runLength+diff):,:] = numpy.nan 
           
        self.calculate_ratio()
        self.RunRg()

       
    def calculate_ratio(self):
        BC = self.subI
        self.ratio = BC[:,16:101].mean(axis=1)/BC[:,310:530].mean(axis=1)
      
    def RunRg(self):
        self.I0 = numpy.zeros(self.sum_I.shape[0])
        self.Rg = numpy.zeros(self.sum_I.shape[0])
        for i in range(self.sum_I.shape[0]):
            try:
                rg = autoRg(numpy.array((self.q, self.subI[i,:],self.subI_err[i,:])).transpose())
                self.I0[i] = rg[2]
                self.Rg[i] = rg[0] 
            except Exception as e:          
                #print(e) 
                self.I0[i] = numpy.nan
                self.Rg[i] = numpy.nan
                pass
                #raise e  
                
            #else: 
                #self.I0[i] = numpy.nan  