import os
import xmltodict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from ..utils.slide_utils import get_level

def poly_area(x,y):
    """
    Computes area of the polygon
    """
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))


def sort_polygons(polygons, classes):
    """
    Sorts polygons from highest area to lowest
    :param polygons: list of polygon coordinates
    :param classes: list of classes
    :return: polygons, classes but sorted
    """
    areas = np.zeros(len(polygons))
    for i, pts in enumerate(polygons):
        areas[i] = poly_area(pts[:,1], pts[:,0])
    sorted = np.argsort(-areas)
    poly_sorted = [polygons[i] for i in sorted]
    cls_sorted = [classes[i] for i in sorted]
    return poly_sorted, cls_sorted


def generate_annotation_mask(file, save_dir, wsi, xml_reader, mag=2.5):
    """
    Generates annotation mask from XML file
    :param file: path to xml file
    :param save_dir: directory to save the annotation mask
    :param wsi: reference whole slide image
    :param xml_reader: an object to deal with XML file
    :param mag: preferred maginification to get level
    """
    # Prepare mask template
    level = get_level(mag=mag, mags=wsi.mags, threshold=5.0)
    w, h = wsi.level_dimensions[level]
    mask = np.ones((h, w, 3), dtype=np.uint8)*255
    ref_factor = mask.shape[1] / wsi.level_dimensions[0][0]

    # Get sorted polygon coordinates and classes
    polygons, classes = xml_reader.get_freehand_polygons(file)

    # Iterate over polygons and populate the mask
    for i, pts in enumerate(polygons):
        pts *= ref_factor
        code = xml_reader.hex_to_pixel(classes[i])
        rr, cc = polygon(pts[:,0], pts[:,1], mask.shape)
        mask[rr, cc, :] = code

    # Save the mask
    filename = os.path.join(save_dir, wsi.ID + '_AnnotationMask.png')
    plt.imsave(filename, mask, cmap=cm.gray)


class XMLDirectoryMissing(Exception):
    pass


class XMLFileMissing(Exception):
    pass
