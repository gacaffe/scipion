# **************************************************************************
# *
# * Authors:     Jose Luis Vilas (jlvilas@cnb.csic.es)
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



from pyworkflow.protocol.params import (PointerParam, BooleanParam, FloatParam, LEVEL_ADVANCED)
from pyworkflow.em.protocol.protocol_3d import ProtRefine3D
from convert import readSetOfVolumes
from shutil import copyfile




class XmippProtMonoRes(ProtRefine3D):
    """    
    Given a map the protocol assings local resolutions to each pixel of the map.
    """
    _label = 'MonoRes - Monogenic Resolution'
    
    def __init__(self, *args, **kwargs):
        ProtRefine3D.__init__(self, *args, **kwargs)
        #self.stepsExecutionMode = STEPS_PARALLEL
        
    #--------------------------- DEFINE param functions --------------------------------------------   
    def _defineParams(self, form):
        form.addSection(label='Input')
  
        form.addParam('halfVolumens', BooleanParam, default=False, label="Would you like to use half volumens?", 
                      help='The noise estimation for determining the local resolution is performed via half volumnes.')
       
        form.addParam('inputVolume', PointerParam, pointerClass='Volume', 
                      label="Input Volume", 
                      help='Select a volume for determining its local resolucion.')
        
        form.addParam('inputVolume2', PointerParam, pointerClass='Volume', 
                      label="Second Half Volumen",  condition = 'halfVolumens', 
                      help='Select a second volume for determining a local resolucion.')
        
        form.addParam('Mask', PointerParam, label="Mask", pointerClass='VolumeMask', allowsNull=True,
                      help='The mask determines the those points of the sphere where the macromolecle is')

        form.addParam('premask', BooleanParam, default=False,
                      label="Is the volume in a circular mask?",
                      help='Sometimes the volume is in an sphere, then this option ought to be selected')
        form.addParam('circularRadius', FloatParam, label="Radius Circular Mask",  condition = 'premask', 
                      default=50, 
                      help='This is the radius of the circular mask.')

        line = form.addLine('Resolution Range (A)', 
                      help="If the user knows the range of resolutions or only a"
                      " range of frequency needs to be analysed", expertLevel=LEVEL_ADVANCED)
        line.addParam('minRes', FloatParam, default=1, label='Min')
        line.addParam('maxRes', FloatParam, default=100, label='Max')
        
#         form.addParam('freqNumber', FloatParam, label="Number of frequencies analyzed",  default=50, expertLevel=LEVEL_ADVANCED,
#                       help='The resolution is computed at a number of frequencies between mininum and'
#                       'maximum resolution px/A. This parameter determines that number')
        form.addParam('trimming', BooleanParam, default=False, expertLevel=LEVEL_ADVANCED,
                      label="Remove bad resolution values?",
                      help='In some situations bad voxels appear. This option allow to remove those voxels')
#         form.addParam('exact', BooleanParam, default=False, expertLevel=LEVEL_ADVANCED,
#                       label="Find exact resolution?",
#                       help='The noise estimation can be performed exact (slow) or approximated (fast)'
#                       'ussually there has not difference between them')
        form.addParam('kValue', FloatParam, label="Trimming Value",  condition = 'trimming', 
                      default=0.5, 
                      help='This value performs post-processing, smoothing the output resolutions.'
                      'If a resolution value is lesser than mean-Trimming*sigma the voxel value will' 
                      'be given by mean-Trimming*sigma. On the other hand if the a resolution value'
                      'is higher than mean+Trimming*sigma, the resolution will be mean+Trimming*sigma')
        
        form.addParam('filterInput', BooleanParam, default=False, expertLevel=LEVEL_ADVANCED,
                      label="Filter input volume with local resolution?",
                      help='The input map is locally filtered at the local resolution map.')

        form.addParallelSection(threads=1, mpi=1)

    #--------------------------- INSERT steps functions --------------------------------------------


    def _insertAllSteps(self):        
        self.micsFn = self._getPath()
        
        # Convert input into xmipp Metadata format
        convertId = self._insertFunctionStep('convertInputStep')
        deps = []
                 
        fnVol = self._getExtraPath('input_volume.vol')

        MS = self._insertFunctionStep('resolutionMonogenicSignalStep', fnVol, prerequisites=[convertId])
       
        self._insertFunctionStep('createOutputStep', prerequisites=[MS])
        
        self._insertFunctionStep("createChimeraScript")
        
        self._insertFunctionStep("createHistrogram")

       

    def convertInputStep(self):
        """ Read the input volume.
        """
        # Get the converted input micrographs in Xmipp format

        path_vol = self._getExtraPath() + '/input_volume.vol'
        vol_ = self.inputVolume.get().getFileName()
        copyfile(vol_,path_vol)
        path_vol = self._getExtraPath() + '/input_mask.vol'
        vol_ = self.Mask.get().getFileName()
        copyfile(vol_,path_vol)
   
    def resolutionMonogenicSignalStep(self, fnVol):

        if self.halfVolumens.get() is False:
            params =  ' --vol %s' % self.inputVolume.get().getFileName()
        else:
            params =  ' --vol1 %s' % self.inputVolume.get().getFileName()
            params =  ' --vol2 %s' % self.inputVolume2.get().getFileName()
        params +=  ' --mask %s' % self.Mask.get().getFileName()
        params +=  ' -o %s' % self._getExtraPath('MGresolution.vol')
        params +=  ' --sampling_rate %f' % self.inputVolume.get().getSamplingRate()
        
        params +=  ' --number_frequencies %f' % 50
        params +=  ' --minRes %f' % self.minRes.get()
        params +=  ' --maxRes %f' % self.maxRes.get()
        params +=  ' --chimera_volume %s' %self._getExtraPath('MG_Chimera_resolution.vol')
        params +=  ' --linear '
#         if self.exact.get():
#             params +=  ' --exact_resolution'
        if self.filterInput.get():
            params +=  ' --filtered_volume %s' %self._getExtraPath('filteredMap.vol')
        else:
            params +=  ' --filtered_volume'

        if self.premask.get() is True:
            params +=  ' --circular_mask %f' % self.circularRadius.get()
        if self.trimming.get() is True:
            params +=  ' --trimmed %f' % self.kValue.get()
        else:
            params +=  ' --trimmed %f' % 0
            
            
 
        self.runJob('xmipp_resolution_monogenic_signal', params)
        
        
    def createChimeraScript(self):
        fnRoot = "extra/"
        scriptFile = self._getPath('Chimera_resolution.cmd') 
        fhCmd = open(scriptFile, 'w')
        fhCmd.write("open %s\n" % (fnRoot+ "input_volume.vol"))
        fhCmd.write("open %s\n" % (fnRoot+ "MG_Chimera_resolution.vol") )
        fhCmd.write("vol #1 hide\n")
        fhCmd.write("scolor #0 volume #1 cmap rainbow reverseColors True\n")
        fhCmd.close()
        
        
    def createHistrogram(self):

        params =  ' -i %s' % self._getExtraPath('MGresolution.vol')
        params +=  ' --mask binary_file %s' % self.Mask.get().getFileName()
        params +=  ' --steps %f' % 30
        params +=  ' --range %f %f' % (self.minRes.get(), self.maxRes.get())
        params +=  ' -o %s' % self._getExtraPath('hist.xmd')

        self.runJob('xmipp_image_histogram', params)

    
    def createOutputStep(self):
        volume_path = self._getExtraPath('MGresolution.vol')
         
        volumesSet = self._createSetOfVolumes()
        volumesSet.setSamplingRate(self.inputVolume.get().getSamplingRate())
                 
        readSetOfVolumes(volume_path, volumesSet)
         
        self._defineOutputs(outputVolume=volumesSet)
        self._defineSourceRelation(self.inputVolume, volumesSet)

    
    #--------------------------- INFO functions -------------------------------------------- 
    def _validate(self):
        
        validateMsgs = []
        if not self.inputVolume.get().hasValue():
            validateMsgs.append('Please provide input volume.')  
        if not self.Mask.get().hasValue():
            validateMsgs.append('Please provide input mask.')         
        return validateMsgs


#     def _summary(self):
#         summary = []
# 
#         if  (not hasattr(self,'outputParticles')):
#             summary.append("Output tilpairs not ready yet.")
#         else:
#             summary.append("Three-uples of Tilt pairs angles assigned: %d" %self.outputParticles.__len__())
#             #
#         return summary
    
    def _methods(self):
        messages = []
        if (hasattr(self,'outputParticles')):
            messages.append('An angular assignment of untilted and tilted particles is carried out [Publication: Not yet]')
        return messages
    
    def _citations(self):
        return ['Not yet']
    
#     def getSummary(self):
#         summary = []
#         summary.append("Particles analyzed:")
#         #summary.append("Particles picked: %d" %coordsSet.getSize())
#         return "\n"#.join(summary)