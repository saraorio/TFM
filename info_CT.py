# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 23:00:12 2022

@author: sorio
"""

#%%
"""
1. Imports
"""
import os
import nibabel as nib
import csv
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
3. Obtain CT info (NIFTI)
"""

#OBTAIN IMAGE & VOXEL SIZE

list_sub = os.listdir(my_dataset_path)
nifti = 'nifti'
image = 'image.nii.gz'

list_nifti_info = []
        
for sub_id in list_sub:
    
    #Set paths
    sub_path = os.path.join(my_dataset_path, sub_id)
    nifti_path = os.path.join(sub_path, nifti)
    image_path = os.path.join(nifti_path, image)
    
    if os.path.exists(image_path): #Discart cases where the NIFTI has not been converted successfully
        #Load NIFTI image
        nifti_image = nib.load(image_path)
        header = nifti_image.header
        #Add values to the list
        #Image size
        image_size = header.get_data_shape()
        #Voxel size
        voxel_size = header.get_zooms()
        list_nifti_info.append([sub_id, image_size, voxel_size])
        
#%%    
#Create file
participants = 'participants2.csv'

with open(participants, 'w', newline='') as file: 
    #Write the file
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Image size', 'Voxel size',  'Slice thickness'])
   
    for idx, id_vector in enumerate(list_nifti_info):
       
        #Folder number
        image_size = id_vector[1]
        voxel_size = id_vector[2]
        slice_thickness = voxel_size[2]
        writer.writerow([image_size, voxel_size, slice_thickness])
       
print("Participants File Updated Successfully!")

#Move file
shutil.move(os.path.join(os.getcwd(), participants), os.path.join(work_path, participants))

