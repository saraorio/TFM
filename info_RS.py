# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 12:57:47 2022

@author: sorio
"""

#%%
"""
1. Imports
"""
import pydicom

#%%

#Llegir DICOMS
file_path = 'D:\imatges\my_dataset\sub-207\RS_sub-207_Cilindre 27-5-19.dcm'
ds = pydicom.dcmread(file_path)

name = ds.PatientName
StructureSetROISequence = ds.StructureSetROISequence._list
