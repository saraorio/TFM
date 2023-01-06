# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 21:41:17 2022

@author: sorio
"""

#%%
"""
1. Imports
"""
import os
import nibabel as nib
import numpy as np
import shutil

#%%
"""
2. Load directories
"""

#Working path
work_path = "D:\imatges"

#Data path
data = 'data'
data_path = os.path.join(work_path, data)

#Dataset path
my_dataset = 'my_dataset'
my_dataset_path = os.path.join(work_path, my_dataset)

#%%
"""
3. Rename mask labels & move them to final folder
"""
list_sub = os.listdir(my_dataset_path)
nifti = 'nifti'
nifti2 = 'nifti2'
mask = 'mask'
nifti_final = 'nifti_final'
image_nifti = 'image.nii.gz'

pattern = ['vagina', 'ctv', 'vagine']
name = 'mask_VAGINA-CTV.nii.gz'

isPatternFound = False

for sub_id in list_sub:
    
    isPatternFound = False
    sub_path = os.path.join(my_dataset_path, sub_id)
    
    nifti_final_path = os.path.join(sub_path, nifti_final)
    #if os.path.exists(nifti_final_path):
    #    shutil.rmtree(nifti_final_path)
    if not os.path.exists(nifti_final_path):
        os.mkdir(nifti_final_path)
    nifti_path = os.path.join(sub_path, nifti)
    nifti2_path = os.path.join(sub_path, nifti2)
    
    # Copy image.nii.gz to new folder
    # From my_dataset\sub-001\nifti
    from_path = os.path.join(nifti_path, image_nifti)
    to_path = os.path.join(nifti_final_path, image_nifti)    
    if not os.path.exists(to_path):
        shutil.copyfile(from_path, to_path)
    
    # From my_dataset\sub-001\nifti2
    list_nifti = os.listdir(nifti2_path)
    
    #for mask_nifti in list_nifti[1:]: #no agafem 'image.nii.gz'
    for mask_nifti in list_nifti:
    
        # En cas que ja haguem trobat un match, passem a la següent carpeta
        if (isPatternFound == True):
            break
        
        from_path = os.path.join(nifti2_path, mask_nifti)
        to_path = os.path.join(nifti_final_path, name)
        mask_nifti = mask_nifti.lower() #passem a minuscules
        
        if mask in mask_nifti:
            for p in pattern:
                
                if p in mask_nifti:
                    print ('[OK] ' + sub_id + ': Change ' + mask_nifti + ' to ' + name)
                    isPatternFound = True
                    if not os.path.exists(to_path):
                        shutil.copyfile(from_path, to_path)
                        break                                               
                    else:
                        isPatternFound = False
                        
    if isPatternFound == False:
        print ('[KO] ' + sub_id + ': Pattern not found / Pattern already exists')
        print (list_nifti)
            

#%%
"""
4. Create segmentation masks map
"""

list_sub = os.listdir(my_dataset_path)
nifti = 'nifti'
nifti_final = 'nifti_final'
image_nifti = 'image.nii.gz'
mask = 'mask'
        
for sub_id in list_sub:
    sub_path = os.path.join(my_dataset_path, sub_id)    
    
    nifti_final_path = os.path.join(sub_path, nifti_final)
    nifti_path = os.path.join(sub_path, nifti)
    
    list_nifti = os.listdir(nifti_final_path)
    image_nifti_path = os.path.join(nifti_path, image_nifti)
    imageCT = nib.load(image_nifti_path)
    valueCT = imageCT.get_fdata()
    affineCT = imageCT.affine
    # Creem matriu de zeros amb la mida que necessitem 
    dim_image = imageCT.shape
    valueZeros = np.zeros(dim_image)
    value_segmentations = valueZeros
    
    for mask_nifti in list_nifti[1:]: #no agafem 'image.nii.gz'
        mask_path = os.path.join(nifti_final_path, mask_nifti)
        if mask in mask_nifti:
            image_mask = nib.load(mask_path)
            value_mask = image_mask.get_fdata()
            if 'VAGINA-CTV' in mask_nifti:
                value = '10'
            elif 'BLADDER' in mask_nifti:
                value = '20'
            elif 'RECTUM' in mask_nifti:
                value = '30'
            elif 'SIGMA' in mask_nifti:
                value = '40'
            elif 'BOWEL' in mask_nifti:
                value = '50'
            else:
                continue
            
            value_segmentations[value_mask == 1] = value
    
    # Transform to 1byte (8bits)
    data = value_segmentations.copy()
    new_dtype = np.uint8
    data = data.astype(new_dtype)
    
    # Save map
    image = nib.Nifti1Image(data, affineCT)
    nib.save(image, nifti_final_path + '/mask.nii')         

