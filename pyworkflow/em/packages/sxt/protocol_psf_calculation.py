# **************************************************************************
# *
# * Authors:     Mohsen Kazemi  (mkazemi@cnb.csic.es)
# *              Joaquin Oton   (joton@cnb.csic.es)
# *              Marc Rosanes   (mrosanes@cells.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'jmdelarosa@cnb.csic.es'
# *
# **************************************************************************

import pyworkflow.protocol.params as params
from pyworkflow.em import Protocol
from os.path import basename
from pyworkflow.utils.path import removeExt
from h5py import File
import xmipp
from pyworkflow.utils import getFloatListFromValues
import numpy as np
import pyworkflow.em as em
import pickle
from pyworkflow.em.packages.sxt.data import PSF3D


class ProtPsfCalculation(Protocol):

    """    
    This protocol is aimed to calculate PSF from input Siemens star pattern.        
    """
    
    _label = 'calculating PSF from SS'    
    #--------------------------- DEFINE param functions --------------------------------------------   
   
    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('inputSiemensStar', params.PathParam, 
                      label="Siemens star pattern",  
                      help="Siemens star pattern is the input image or the "
                           "stack of input images with different ZP "
                           "(and same angle) for calculating the MTF.\n"
                           "Note: There is a different MTF for each different "
                           "ZP position.")
        form.addParam('refNumber', params.IntParam, default=-1,
                      expertLevel=params.LEVEL_ADVANCED,
                      label="Reference number",
                      help="image index of siemens star pattern used to "
                           "calculate de reference image.\n"
                           "By default, nRef = -1  automatically selects central "
                           "image (floor(N/2)+1).")
        form.addParam('fractionOrders', params.NumericListParam,
                      default="1 3",
                      expertLevel=params.LEVEL_ADVANCED,
                      label="Orders",
                      help="Diffraction orders used to calculate MTF profiles.") 
        form.addParam('ringPosition', params.NumericListParam,
                      default="1.5e3 3e3 6e3 12e3",
                      expertLevel=params.LEVEL_ADVANCED,
                      label="Ring positions (nm)",
                      help="Center radius in nm of the void rings of "
                           "Siemens star pattern to be removed from the "
                           "calculation. Default values are set to match "
                           "Xradia manufactured SS pattern")
        form.addParam('pixelSizeX', params.FloatParam, default=5.0,
                      expertLevel=params.LEVEL_ADVANCED,
                      label="PSF pixel size along X axis (nm)")
        form.addParam('pixelSizeZ', params.FloatParam, default=150,
                      expertLevel=params.LEVEL_ADVANCED,
                      label="PSF pixel size along Z axis (nm)") 
                      
        form.addParallelSection(threads=1, mpi=2)
    #--------------------------- INSERT steps functions --------------------------------------------
    
    def _insertAllSteps(self):         
        fnOutPsf = self._defineOutputName()                   
        inputSS = self.inputSiemensStar.get()        
        nRef = self.refNumber.get()
        orders = getFloatListFromValues(self.fractionOrders.get())
        ringPos = getFloatListFromValues(self.ringPosition.get())
               
        self._insertFunctionStep('validateSiemensStar', inputSS)   
        self._insertFunctionStep('getPsfFromSiemensStar', inputSS, nRef, 
                                 orders, ringPos, fnOutPsf)
        self._insertFunctionStep('createOutputStep', fnOutPsf)            
    #--------------------------- STEPS functions --------------------------------------------
    
    def validateSiemensStar(self, inputSS):
        fnIn = self._getExtraPath(basename(inputSS))                   
        fnStack = removeExt(fnIn) + '.mrc'
        fnOutMd = removeExt(fnIn) + '.xmd'  
        fhHdf5 = File(inputSS, 'r')
        
        imgArray = fhHdf5 ["NXtomo/data/data"][()]                                 
        ih = em.ImageHandler()
        outputImg = ih.createImage()
        i = 0
        for j in range(np.shape(imgArray)[0]):
            outputImg.setData(imgArray[j, :, :])
            i += 1
            outputImg.write((i,fnStack))    
             
        anglesArray = fhHdf5 ["NXtomo/data/rotation_angle"][()]            
        mdOut = xmipp.MetaData()            
        for k in range(np.shape(anglesArray)[0]):
            objId = mdOut.addObject()
            mdOut.setValue(xmipp.MDL_IMAGE, "%d@%s" % (k+1,fnStack), objId)
            mdOut.setValue(xmipp.MDL_ANGLE_TILT, anglesArray[k], objId)
            if k != 0 and anglesArray[k] != anglesArray[k-1]:
                raise Exception ("Selected input file is not a "
                                 "Siemens Star pattern!!!")                 
        mdOut.write(fnOutMd)  
    
    def getPsfFromSiemensStar(self, inputSS, nRef, orders, ringPos, fnOutPsf):        
        fhHdf5 = File(inputSS, 'r')
        imgSS = fhHdf5 ["NXtomo/data/data"][()]
        print "Input Siemense Star pattern dimensions are:\n", np.shape(imgSS)        
        
        imgNumberTotal = np.shape(imgSS)[0]
        imgNumber = np.floor(imgNumberTotal / 2)
        from xpytools.getResolutionfromSiemensStar import MTFgetResolution
        resolutionObj = MTFgetResolution()
        imgSsResolution = resolutionObj.getResolutionfromSiemensStar(
                                                                     imgSS[imgNumber],
                                                                     ringPos)
        print "Resolution of Siemens star image is:\n" , imgSsResolution [0]        
        dx = imgSsResolution [0]
        
        imgSingle = imgSS[imgNumber]
        from xpytools.getMTFfromSiemensStar import MTFfromSiemensStar
        MTFObj = MTFfromSiemensStar()
        mtfOut = MTFObj.getMTFfromSiemensStar(imgSS, dx, nRef, orders, ringPos)  
        pickle.dump(mtfOut, open(self._defineMtfDicName(), "wb"))
        fx = mtfOut['fx']
        mtf = mtfOut['mtf']
        print "MTF dimension is:\n" , np.shape(mtf)
        
        from xpytools.mtf2psf import MTF2PSFClass
        mtf2psfObj = MTF2PSFClass()
        psfdict = mtf2psfObj.mtf2psf(mtf, fx, self.pixelSizeX.get(), fov=400, fc=-1) 
        pickle.dump(psfdict, open(self._definePsfDicName(), "wb"))        
        psfArray = psfdict['psf']
        psfPixelSize = psfdict['dx']
        print "PSF dimension is:\n" , np.shape(psfArray)
        print "PSF pixelSize(nm) is:\n" , psfPixelSize
        
        ih = em.ImageHandler()
        outputImg = ih.createImage()        
        i = 0
        for j in range(np.shape(psfArray)[0]):
            outputImg.setData(psfArray[j, :, :])
            i += 1
            outputImg.write((i,fnOutPsf))    
        
    def createOutputStep(self, fnOutPsf): 
        psfDict = pickle.load(open(self._definePsfDicName(), "rb"))
        psfPixelSizeX = psfDict['dx']
        psfPixelSizeZ = self.pixelSizeZ.get()
        
        #calculating DoF
        psfArray = psfDict['psf']
        from xpytools.getDOF import GetDOFClass
        getDoFObj = GetDOFClass()
        psfDof = getDoFObj.getDOF(psfArray)
        print "DoF = ", psfDof
        
        #calculating Rayleigh resolution
        BestPsfArray = self._psfSelection(psfArray)
        from xpytools.rayleighResolution import RayleighResolutionClass
        RayleighResolutionClassObj = RayleighResolutionClass()
        rayleighResolution = RayleighResolutionClassObj.getRayleighResolution(
                                                            BestPsfArray, psfPixelSizeX)
                
        print "RayLeighResolution = ", rayleighResolution
        
        outPsf = PSF3D()
        outPsf.setLocation(fnOutPsf)
        outPsf.setSamplingRate(psfPixelSizeX * 10)
        outPsf.setZpixelSize(psfPixelSizeZ)
        outPsf.setDoF(psfDof)
        outPsf.setRayleighResolution(rayleighResolution)      
        self._defineOutputs(output3DPSF=outPsf)
              
    #--------------------------- INFO functions -------------------------------------------- 
    def _summary(self):
        summary = []
        outputSet = self._getOutputSet3DPsf()
        if outputSet is None:
            summary.append("Output 3DPSF is not ready yet.") 
        else:
            summary.append("Output 3DPSF is ready.")
        
        return summary
    def _validate(self):
        errors = []
        hdf5 = self.inputSiemensStar.get().endswith('hdf5')
        if self.inputSiemensStar.get():
            if not hdf5:
                errors.append ("Expected hdf5 files for importing!!!") 
        else:
            errors.append("The path can not be empty!!!")      
        return errors              
    #--------------------------- UTILS functions --------------------------------------------
    
    def _defineOutputName(self):
        return self._getExtraPath('psf.mrc')
    
    def _defineMtfDicName(self):
        return self._getExtraPath('mtfDic.p')
    
    def _definePsfDicName(self):
        return self._getExtraPath('psfDic.p')
    
    def _getOutputSet3DPsf(self):
        return getattr(self, 'output3DPSF', None)
    
    def _psfSelection(self, psfArray):    
        psfPixelSizeZ = self.pixelSizeZ.get() 
        #psfPixelSizeZ = 150
        #claculating best psf image to get their mean and use in calculating RayleighResolution
        xCenter = np.floor(np.shape(psfArray)[1]/2)
        centerValues = psfArray[:, xCenter, xCenter]
        thr = 0.3
        thrv = max(centerValues) * thr
        #finding indices based on centerValues curne and thrv      
        #mp: indices array above threshold, zm: central index
        #zN: indices range that will use to select psf images to get their average
        mp = np.where(centerValues > thrv)
        zm = mp[0][np.floor((mp[0][0] - mp[0][-1])/2)]
        zN = np.floor(np.shape(psfArray)[0]/psfPixelSizeZ/2);
        zPos = []
        for i in range(2*int(zN)+1):
            zPos.append(int(zm-zN+i))
        print "PSF image indices to calculate their mean are: ", zPos        
        BestPsfArray = np.mean(psfArray[zPos, :, :], axis=0)
        return BestPsfArray