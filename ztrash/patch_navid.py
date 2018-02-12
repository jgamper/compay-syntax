import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import openslide as ops
import glob
from scipy.misc import imsave
import random



region_name = 'Normal'
# overlap_ratio = -0.25
patch_size = 448



if not os.path.exists(region_name):
    os.makedirs(region_name)

# wsi_path = 'wsi'+'/'
wsi_path ='F:/Camelyon_Dataset/Original/Train/Tumor/'
wsi_image = glob.glob(wsi_path + '*.tif')

mask_path = 'F:/Camelyon_Dataset/Original/Train/Tumor/Tissue_Mask_WSI/'
mask_image = glob.glob(mask_path + '*.tif')

mask_Tumor_path = 'F:/Camelyon_Dataset/Original/Train/Tumor/Mask_Tumor/'
mask_Tumor_image = glob.glob(mask_Tumor_path + '*.tif')


for i in range(len(wsi_image)):
    individual_wsi_path = wsi_image[i]
    directory = os.path.basename(individual_wsi_path)
    wsi= ops.OpenSlide(individual_wsi_path)
    width = wsi.dimensions[0]
    height = wsi.dimensions[1]

    individual_mask_path = mask_image[i]
    wsi_mask = ops.OpenSlide(individual_mask_path)

    individual_mask_Tumor_path = mask_Tumor_image[i]
    wsi_mask_Tumor = ops.OpenSlide(individual_mask_Tumor_path)


    image = wsi.read_region((0, 0), 4, (int(width / 16), int(height / 16)))
    image = np.asarray(image)
    r, g, b, a = cv2.split(image)
    image = cv2.merge([r, g, b])

    # For Randomly extract 1000 patches from tissue regions
    im_mask = wsi_mask.read_region((0, 0), 4, (int(width / 16), int(height / 16)))
    im_mask = np.asarray(im_mask)
    r, g, b, a = cv2.split(im_mask)
    im_mask = cv2.merge([r, g, b])
    imgray = cv2.cvtColor(im_mask, cv2.COLOR_BGR2GRAY)
    tissue_coordinates= np.nonzero(imgray == 1)
    tissue_coordinates = np.array(tissue_coordinates)
    tissue_coordinates = np.transpose(tissue_coordinates,(1,0))
    if tissue_coordinates.shape[0] <= 1000:
        sampled_tissue_coordinates = tissue_coordinates
    else:
        a = random.sample(range(tissue_coordinates.shape[0]), 1000)
        sampled_tissue_coordinates = tissue_coordinates[a,:]



    # For Randomly extraction of 1000 patches from Tumor regions
    im_mask_tumor = wsi_mask_Tumor.read_region((0, 0), 2, (int(width / 4), int(height / 4)))
    im_mask_tumor = np.asarray(im_mask_tumor)
    r, g, b, a = cv2.split(im_mask_tumor)
    im_mask_tumor = cv2.merge([r, g, b])
    imgray_tumor = cv2.cvtColor(im_mask_tumor, cv2.COLOR_BGR2GRAY)
    #here instead of 1, tumor regions are 255
    tumor_tissue_coordinates= np.nonzero(imgray_tumor == 255)
    tumor_tissue_coordinates = np.array(tumor_tissue_coordinates)
    tumor_tissue_coordinates = np.transpose(tumor_tissue_coordinates,(1,0))
    if tumor_tissue_coordinates.shape[0] <= 1000:
        sampled_tumor_tissue_coordinates = tumor_tissue_coordinates
    else:
        b = random.sample(range(tumor_tissue_coordinates.shape[0]), 1000)
        sampled_tumor_tissue_coordinates = tumor_tissue_coordinates[b,:]


    # this for-loop is for extarcting normal patches within tissue regions excluding Tumor
    for y,x in sampled_tissue_coordinates:
        im_mask_s = wsi_mask.read_region((x* 16, y *16), 1, (patch_size, patch_size))
        im_mask_Tumor_s = wsi_mask_Tumor.read_region((x * 16, y * 16), 1, (patch_size, patch_size))

        im_s = wsi.read_region((x * 16, y * 16), 1, (patch_size, patch_size))
        im_s = np.asarray(im_s)
        r, g, b, a = cv2.split(im_s)
        im_s = cv2.merge([r, g, b])

        im_mask_s = np.asarray(im_mask_s)
        r, g, b, a = cv2.split(im_mask_s)
        im_mask_s = cv2.merge([r, g, b])
        imgray_s = cv2.cvtColor(im_mask_s, cv2.COLOR_BGR2GRAY)

        im_mask_Tumor_s = np.asarray(im_mask_Tumor_s)
        r, g, b, a = cv2.split(im_mask_Tumor_s)
        im_mask_Tumor_s = cv2.merge([r, g, b])
        imgray_s_Tumor = cv2.cvtColor(im_mask_Tumor_s, cv2.COLOR_BGR2GRAY)

        sum_imgray_crop_Tumor = np.sum(imgray_s_Tumor/255)
        print(sum_imgray_crop_Tumor)
        if sum_imgray_crop_Tumor / (patch_size * patch_size) > 0.05:#check if patch containes tumor
            continue
        else:
            sum_imgray_crop = np.sum(imgray_s)
            print(sum_imgray_crop)
            if sum_imgray_crop / (patch_size * patch_size) > 0.9:#check if we are in tissue region
                new_directory = directory[:-4]
                ddir = 'New_20x_normal_tumor448'
                if not os.path.exists(ddir  + '/' + new_directory):
                    os.makedirs(ddir  + '/' + new_directory)
                name = ddir + '/' + new_directory + '/' + new_directory + '_' + str(y) + '_' + str(x) + '.png'
                imsave(name, im_s)

    #This for-loop is for extracting tumor regions
    for y, x in sampled_tumor_tissue_coordinates:
        # im_mask_s = wsi_mask.read_region((x * 4, y * 4), 0, (patch_size, patch_size))
        im_mask_Tumor_s = wsi_mask_Tumor.read_region((x* 4, y* 4), 1, (patch_size, patch_size))
        im_s = wsi.read_region((x * 4, y * 4), 1, (patch_size, patch_size))
        im_s = np.asarray(im_s)
        r, g, b, a = cv2.split(im_s)
        im_s = cv2.merge([r, g, b])


        im_mask_Tumor_s = np.asarray(im_mask_Tumor_s)
        r, g, b, a = cv2.split(im_mask_Tumor_s)
        im_mask_Tumor_s = cv2.merge([r, g, b])
        imgray_s_Tumor = cv2.cvtColor(im_mask_Tumor_s, cv2.COLOR_BGR2GRAY)

        sum_imgray_crop_Tumor = np.sum(imgray_s_Tumor/255)
        print(sum_imgray_crop_Tumor)
        if sum_imgray_crop_Tumor / (patch_size * patch_size) > 0.05:#check if patch contains tumour
            new_directory = directory[:-4]
            dir = 'New_20x_tumor_tumor448'
            if not os.path.exists(dir + '/' + new_directory):
                os.makedirs(dir + '/' + new_directory)
            name = dir + '/' + new_directory + '/' + new_directory + '_' + str(y) + '_' + str(x) + '.png'
            imsave(name, im_s)









