#Questions: how to remember sutractions in orer to compare them?



#from __future__ import print_function, division
import h5py
import numpy
from freesas.autorg import autoRg
from freesas.cormap import gof

class HPLCrun:

    sum_I = None
    runLength =  None
    lowQmin = 0.05
    lowQmax = 0.15
    highQmin = 3.5
    highQmax = 4.9
    subI=  None
    subI_err = None

    def __init__(self, h5file = None):
        if h5file:
            with h5py.File(h5file, "r") as data:
                self.q = numpy.asarray(data['q'])[:]
                self.I = numpy.asarray(data['scattering_I'])
                self.Ierr = numpy.asarray(data['scattering_Stdev'])

                if "sum_I" in data.keys():
                    self.sum_I = numpy.asarray(data['sum_I'])
            self.trim()
            self.cormapData =   numpy.full((self.sum_I.shape[0],self.sum_I.shape[0]), numpy.nan )

    def save(self, fileName):
        #this would profit from some exception throwing
        with h5py.File(fileName, "w")  as file:
            file.create_dataset('subtraction', data=self.subI)
            file.create_dataset('subtraction_err', data=self.subI_err)
            file.create_dataset('I0', data=self.I0)
            file.create_dataset('Rg', data=self.Rg)
            file.create_dataset('ratio', data=self.ratio)


    def trim(self):
        """
        Remove data points of 0 signal from sum_I so that they don't srew up plotting
        """
        if self.sum_I is not None:
            self.sum_I[numpy.where(self.sum_I == 0.0)] = numpy.nan
            validPoints = ~numpy.isnan(self.sum_I)
            self.I = self.I[validPoints]
            self.Ierr = self.Ierr[validPoints]
            self.sum_I = self.sum_I[validPoints]
            self.runLength = self.sum_I.shape[0]
            #Note: Here we assume a padding of 1 pont at the beginning!
            #self.I = self.I[1:self.runLength+2,:]
            #self.Ierr = self.Ierr[1:self.runLength+2,:]



    def IinQ(self, qmin, qmax = None, total = True):
        if qmax is None:
            qmax = qmin + 0.1
        imin = numpy.argmin(abs(self.q-qmin))
        imax= numpy.argmin(abs(self.q-qmax))
        if total is True:
            return self.I[:,imin:imax].mean(axis = 1)
        else:
            return self.subI[:,imin:imax].mean(axis = 1)

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
        if diff > 0:
            self.subI[0:diff+1,:] = numpy.nan
            self.subI[min(self.runLength,puffer.runLength+diff):,:] = numpy.nan
        if diff < 0:
            self.subI[diff:,:] = numpy.nan
        #    self.subI[min(self.runLength,puffer.runLength+diff):,:] = numpy.nan
        self.calculate_ratio()
        self.RunRg()
        #self.cormap()



    def calculate_ratio(self, q1min = None, q1max = None, q2min = None, q2max = None):
        if q1min is None:
            q1min = self.lowQmin
        if q1max is None:
            q1max = self.lowQmax
        if q2min is None:
            q2min = self.highQmin
        if q2max is None:
            q2max = self.highQmax
        self.ratio = self.IinQ(q1min,q1max,total = False)/self.IinQ(q2min,q2max,total = False)

        mean = numpy.nanmean(self.ratio)
        std = numpy.nanstd(self.ratio)

        outliers = numpy.append(numpy.where((mean + 5 * std) <  self.ratio),numpy.where((mean - 5 * std) >  self.ratio))

        self.ratio[outliers] = numpy.nan



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

    def cormap(self):
        """Very computation intensive
        Only calculates within a window of +-100 frames"""
        self.cormapData =   numpy.full((self.sum_I.shape[0],self.sum_I.shape[0]), numpy.nan )
        for i in range(self.sum_I.shape[0]):
            self.cormapData[i,i] = 1.0
            for j in  range(max(self.sum_I.shape[0]-100,0),min(self.sum_I.shape[0]+101,self.sum_I.shape[0])):
                self.cormapData[i,j] = self.cormapData[j,i] = gof(self.subI[i,:],self.subI[j,:])[2]
