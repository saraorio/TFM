# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 18:13:08 2022

@author: sorio
"""

#%%
"""
1. Imports
"""
import os
import shutil
import pydicom
from dcmrtstruct2nii import dcmrtstruct2nii
from DicomRTTool import DicomReaderWriter
import SimpleITK as sitk
import csv

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
if not os.path.exists(my_dataset_path):
    os.mkdir(my_dataset_path)

#%%
"""
3. Read DICOM files and separate them according to PatientID
"""

#CREATE A LIST SORTING ALL PATIENTS BY ID

#List with all DICOM files organized by PatientID, using different arrays
list_all = []
#List with all the DICOM files
dicom_files_list = os.listdir(data_path)

for file_name in dicom_files_list:
    
    #Extraction of the FileDataset object of the DICOM file to obtain the PatientID
    file_path = os.path.join(data_path, file_name)
    ds = pydicom.dcmread(file_path)
    patient_id = ds.PatientID
    #Remove starting '0' from patientID number
    patient_id = patient_id.lstrip('0')
    
    #The first element is always added to 'list_all' list
    if len(list_all) == 0:
        list_all.append([patient_id, file_name])
        
    found = False
    for idx, id_vector in enumerate(list_all):
        
        #If the PatientID is already inside the list, the DICOM file is added in the existing array
        if patient_id == id_vector[0]:
            list_all[idx].append(file_name)
            found = True
            
    #If the PatientID is not inside the list, one more array is added with the new PatientID
    if found == False:
        list_all.append([patient_id, file_name])
        
        
#CREATE CSV WITH ALL PARTICIPANTS

#Create file
participants = 'participants.csv'

with open(participants, 'w', newline='') as file: 
    
   #Write the file
   writer = csv.writer(file, delimiter=';')
   writer.writerow(['FOLDER', 'Patient ID', 'CT slices'])
   
   for idx, id_vector in enumerate(list_all):
       
       #Folder number
       sub_id = 'sub-' + format(idx + 1, '03')
       #PatientID
       patient_id = id_vector[0]
       #Number of slices of the CT
       ct_slices = len(id_vector) - 4 #Subtract 4 in order to dismiss rt-struct files & patientID
       writer.writerow([sub_id, patient_id, ct_slices])
       
print("Participants File Created Successfully!")

#Move file
shutil.move(os.path.join(os.getcwd(), participants), os.path.join(work_path, participants))

        
#%%        
"""
4. Create 'my_dataset'
"""   

#REORGANIZE PATH FOLDERS

dicom_extension = '.dcm'
     
for idx, id_vector in enumerate(list_all):
    
    #PatientID
    patient_id = id_vector[0]
    
    #A new folder is created for each patient
    sub_id = 'sub-' + format(idx + 1, '03')
    sub_path = os.path.join(my_dataset_path, sub_id)
    if not os.path.exists(sub_path):
        os.mkdir(sub_path)
    
    #Copy the DICOM files into each respective patient folder
    for pos, file_name in enumerate(id_vector[1:]): #Skip the first position of the vector (patientID) as there's no file referenced with it
        
        #Rename files
        output_file_name = file_name[0:2] + '_' + sub_id + '_' + patient_id
        #If the file is a CT, a slice number is added
        if file_name.startswith('CT'):
            output_file_name += '_' + 'slice' + format(pos+1, '03')
        output_file_name += dicom_extension
        
        #Move files
        from_path = os.path.join(data_path, file_name)
        to_path = os.path.join(sub_path, output_file_name)
        shutil.copyfile(from_path, to_path)
        
#%%
"""
5.1. Obtain CT and Segmentations in NIFTI format
     Version using dcmrtstruct2nii
"""

#CONVERT TO NIFTI

list_sub = os.listdir(my_dataset_path)
nifti = 'nifti'
        
for sub_id in list_sub:
    
    #A new folder is created inside every patient folder to save NIFTI files
    sub_path = os.path.join(my_dataset_path, sub_id)
    nifti_path = os.path.join(sub_path, nifti)
    if not os.path.exists(nifti_path):
        os.mkdir(nifti_path)
    
    #Inside every sub folder
    sub_content = os.listdir(sub_path)
    for rt in sub_content:
        
        #Find RT-Struct file and convert CT and Segmentations
        if rt.startswith('RS'):
            rt_struct = os.path.join(sub_path, rt)
            dcmrtstruct2nii(rt_struct, sub_path, nifti_path)
            print ('Conversion to NIFTI of ' + sub_id  + ' done')
            print ('___________________________________________________')
            print ()
            break


#%%
"""
5.2. Obtain CT and Segmentations in NIFTI format
     Version using DicomRTTool
"""

#CONVERT TO NIFTI

list_sub = os.listdir(my_dataset_path)
nifti = 'nifti2'
       
for sub_id in list_sub:
    
    #A new folder is created inside every patient folder to save NIFTI files
    sub_path = os.path.join(my_dataset_path, sub_id)
    nifti_path = os.path.join(sub_path, nifti)
    #if os.path.exists(nifti_path):
    #    shutil.rmtree(nifti_path)
    if not os.path.exists(nifti_path):
        os.mkdir(nifti_path)
    
    #Inside every sub folder
    reader = DicomReaderWriter()
    reader.walk_through_folders(sub_path)
    # To obtain image.nii.gz (too long)
    #reader.get_images()
    #path_image = os.path.join(nifti_path, 'image.nii.gz')
    #sitk.WriteImage(reader.dicom_handle, path_image)
    rois = reader.return_rois(print_rois=True)
    for r in rois:
        reader.set_contour_names_and_associations([r])
        reader.get_mask()
        mask = 'mask_' + r.replace(" ", "_") + '.nii.gz'
        path_mask = os.path.join(nifti_path, mask)
        sitk.WriteImage(reader.annotation_handle, path_mask)
    print ('Conversion to NIFTI of ' + sub_id  + ' done')
    print ('___________________________________________________')
    print ()

