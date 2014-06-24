# **************************************************************************
# *
# * Authors:     Roberto Marabini (roberto@cnb.csic.es)
# *              J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
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
from pyworkflow.utils.path import makePath
"""
This sub-package implement projection matching using xmipp 3.1
"""

from pyworkflow.utils import getFloatListFromValues, getBoolListFromValues
from pyworkflow.em import ProtRefine3D, ProtClassify3D

from projmatch_initialize import createFilenameTemplates, initializeLists
from projmatch_form import _defineProjectionMatchingParams
from projmatch_steps import *

       
        
class XmippProtProjMatch(ProtRefine3D, ProtClassify3D):
    """ 3D reconstruction and classification using multireference projection matching"""

    _label = 'projection matching'

    def __init__(self, **args):        
        ProtRefine3D.__init__(self, **args)
        ProtClassify3D.__init__(self, **args)
        
    def _initialize(self):
        """ This function is mean to be called after the 
        working dir for the protocol have been set. (maybe after recovery from mapper)
        """
        # Setup the dictionary with filenames templates to 
        # be used by _getFileName
        createFilenameTemplates(self)
        # Load the values from several params generating a list
        # of values per iteration or references
        initializeLists(self)

    
    #--------------------------- DEFINE param functions --------------------------------------------   
        
    def _defineParams(self, form):
        """ Since the form definition is very very large,
        we have do it in a separated function.
        """
        _defineProjectionMatchingParams(self, form)
         
         
    #--------------------------- INSERT steps functions --------------------------------------------  
    
    def _insertAllSteps(self):
        self._insertInitSteps()
        self._insertIterationSteps()
        self._insertEndSteps()
        
    def _insertInitSteps(self):
        """ Insert some initialization steps required
        before executing the steps per iteration. 
        """
        pass
                                                    
    def _insertItersSteps(self):
        """ Insert several steps needed per iteration. """
        
        for iterN in self.allIters():
            stepId = self._insertFunctionStep('createIterDirsStep', iterN)

            ProjMatchRootNameList = ['']
            
            # Insert some steps per reference volume
            for refN in self.allRefs():
                # Mask the references in the iteration
                insertMaskReferenceStep(self, iterN, refN)
                
                # Create the library of projections
                insertAngularProjectLibraryStep(self, iterN, refN)
                
                # Projection matching steps
                insertProjectionMatchingStep(self, iterN, refN)
                
            # Select the reference that best fits each image
            insertAssignImagesToReferencesStep(self, iterN)
            
            # Create new class averages with images assigned
            insertAngularClassAverageStep(self, iterN)
    
            # Reconstruct each reference with new averages
            for refN in self.allRefs():
                insertReconstructionStep(self, iterN, refN)
                
                if self.DoSplitReferenceImages[iterN]:
                    if self.DoComputeResolution[iterN]:
                        # Reconstruct two halves of the data
                        insertReconstructionStep(self, iterN, refN, 'Split1')
                        insertReconstructionStep(self, iterN, refN, 'Split2')
                        # Compute the resolution
                        insertComputeResolutionStep(self, iterN, refN)
                    
                # FIXME: in xmipp this step is inside the if self.DoSplit.. a bug there?    
                insertFilterVolumeStep(self, iterN, refN)
                    
                
    def _insertEndSteps(self):
        """ Insert steps after the iteration steps 
        have been performed.
        """ 
        self._insertFunctionStep('createOutputStep')
                 
                                       
    #--------------------------- STEPS functions --------------------------------------------       
    def createIterDirsStep(self, iterN):
        """ Create the necessary directory for a given iteration. """
        iterDirs = [self._getFileName(k) for k in ['IterDir', 'ProjMatchDirs', 'LibraryDirs']]
    
        for d in iterDirs:
            makePath(d)
            
        return iterDirs
    
    def createOutputStep(self):
        print "output generated..........."


    #--------------------------- INFO functions -------------------------------------------- 
    
    def _validate(self):
        errors = []
        return errors
    
    def _citations(self):
        cites = []
        return cites
    
    def _summary(self):
        summary = []
        return summary
    
    def _methods(self):
        return self._summary()  # summary is quite explicit and serve as methods
    
    #--------------------------- UTILS functions --------------------------------------------
    
    def allIters(self):
        """ Iterate over all iterations. """
        for i in range(1, self.numberOfIterations.get()+1):
            yield i
            
    def allRefs(self):
        """ Iterate over all references. """
        for i in range(1, self.numberOfReferences.get()+1):
            yield i
            
    def itersFloatValues(self, attributeName, firstValue=-1):
        """ Take the string of a given attribute and
        create a list of floats that will be used by 
        the iteratioins. An special first value will be
        added to the list for iteration 0.
        """
        valuesStr = self.getAttributeValue(attributeName)
        return [firstValue] + getFloatListFromValues(valuesStr, length=self.numberOfIterations.get())
    
    def itersBoolValues(self, attributeName, firstValue=False):
        """ Take the string of a given attribute and
        create a list of booleans that will be used by 
        the iteratioins. An special first value will be
        added to the list for iteration 0.
        """
        valuesStr = self.getAttributeValue(attributeName)
        return [firstValue] + getBoolListFromValues(valuesStr, length=self.numberOfIterations.get())
        