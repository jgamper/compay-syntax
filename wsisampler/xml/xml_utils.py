import xmltodict
import numpy as np


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


class XMLDirectoryMissing(Exception):
    pass


class XMLFileMissing(Exception):
    pass
