import xmltodict
import numpy as np
from .xml_utils import poly_area, sort_polygons

class XMLPolygons(object):
    """
    Abstract class to read polygons from XML file
    """
    def __init__(self):

        self.init_codes()

    def init_codes(self):
        """
        Method to be defined by user for specific XML type.
        This method initialises the mapping from HEX to labels, etc.
        """
        raise NotImplementedError

    def get_freehand_polygons(self):
        """
        Method to be defined by user for specific XML type.
        This method should xml formated free hand annotations
        to numpy arrays.

        The method should have an input named: xml_path, which is a string/path
        to the xml file.
        The method should return a list of polygon coords and a list of their classes
        encoded as a HEX color.
        """
        raise NotImplementedError

    def hex_to_pixel(self, hex):
        """
        Given pixel values, convert to label
        :param hex: color HEX string
        """
        assert hasattr(self, '_hex_to_pixel'), '_hex_to_pixel mapping has not been defined'
        assert hex in self._hex_to_pixel.keys(), 'Unseen hex color code'
        return self._hex_to_pixel[hex]

    def pixel_to_label(self, pixel):
        """
        Given pixel values, convert to label
        :param pixel: a tuple of pixel a values
        """
        assert hasattr(self, '_pixel_to_label'), '_pixel_to_label mapping has not been defined'
        assert pixel in self._pixel_to_label.keys(), 'Unseen pixel type'
        return self._pixel_to_label[pixel]

    def label_to_pixel(self, lbl):
        """
        Given label, returns pixel pattern
        :param lbl: integer label
        """
        assert hasattr(self, '_label_to_pixel'), '_label_to_pixel mapping has not been defined'
        assert lbl in self._label_to_pixel.keys(), 'Unseen label'
        return self._label_to_pixel[lbl]


class XMLVirtualSlideMaker(XMLPolygons):
    """
    XML reader for Virtual slide maker.
    """

    def __init__(self):

        super(XMLVirtualSlideMaker, self).__init__()

    def init_codes(self):
        """
        Custom function for Virtual Slide Maker free hand annotations
        # NOTE: THIS CLASS IS BUILT AND TESTED ONLY FOR VIRTUAL SLIDE MAKER
        """

        self._hex_to_pixel = {'#FFFF00':(255,255,0), '#000000':(0,0,0), '#0000FF':(0,0,255),
                '#008000':(0,128,0), '#00FFFF':(0,255,255), '#800080':(128,0,128),
                '#FF0000':(255,0,0)}

                                # YELLOW       BLACK      BLUE
        self._pixel_to_label = {(255,255,0):1, (0,0,0):2, (0,0,255):3,
                                # GREEN        LIGHT BLUE   PURPLE
                                (0,128,0):4, (0,255,255):5, (128,0,128):6,
                                # RED         WHITE/BACKGROUND
                                (255,0,0):7, (255, 255, 255):0}

                                # YELLOW       BLACK      BLUE
        self._label_to_pixel = {1:[255,255,0], 2:[0,0,0], 3:[0,0,255],
                                # GREEN        LIGHT BLUE   PURPLE
                                4:[0,128,0], 5:[0,255,255], 6:[128,0,128],
                                # RED         WHITE/BACKGROUND
                                7:(255,0,0), 0:[255, 255, 255]}

    def get_freehand_polygons(self, xml_path):
        """
        Convert xml formated free hand annotations
        to numpy arrays.

        # NOTE: Built and tested on Virtual Slide Maker free-hand
        annotations only!!

        :param xml_path: string, path to xml file
        :return: list of polygon coords and a list of their classes
        """

        with open(xml_path) as xml_file:
            xml = xmltodict.parse(xml_file.read())

        polygons = []
        classes = []
        for polygon_dict in xml['ZAS']['POI']['LABELS']['LABEL']:
            if polygon_dict['@MEDIATYPE'] == "freehand":
                coords = np.array([[float(_['@Y']), float(_['@X'])] for _ in polygon_dict['POLYGON']['POINT']])
                color = polygon_dict['@LINECOLOR']
                polygons.append(coords)
                classes.append(color)
        # Return sorted polygons and their classes
        return sort_polygons(polygons, classes)


class XMLAsap(XMLPolygons):
    """
    This object is by far not exhaustive wrt to all possible colors in ASAP.
    For ASAP most likely new xml object will have to made for a specific task.
    """

    def __init__(self):

        super(XMLAsap, self).__init__()

    def init_codes(self):
        """
        Custom function for ASAP free hand annotations
        # NOTE: THIS CLASS WILL NOT WORK WITH ALL ASAP ANNOTATION COLORS
        """

        self._hex_to_pixel = {'#000000':(0,0,0), '#ffaa00':(255,170,0), '#64FE2E':(100,254,46),
                '#5555ff':(85,85,255), '#ff00ff':(255,0,255), '#ffff00':(255,255,0)}


        self._pixel_to_label = {(0,0,0):1, (255,170,0):2, (100,254,46):3,

                                (85,85,255):4, (255,0,255):5, (255,255,0):6,

                                (255, 255, 255):0}


        self._label_to_pixel = {1:[0,0,0], 2:[255,170,0], 3:[100,254,46],

                                4:[85,85,255], 5:[255,0,255], 6:[255,255,0],

                                0:[255, 255, 255]}

    def get_freehand_polygons(self, xml_path):
        """
        Convert xml formated free hand annotations
        to numpy arrays.

        # NOTE: Built and tested on Virtual Slide Maker free-hand
        annotations only!!

        :param xml_path: string, path to xml file
        :return: list of polygon coords and a list of their classes
        """

        with open(xml_path) as xml_file:
            xml = xmltodict.parse(xml_file.read())

        name_to_color = {}
        for d in xml['ASAP_Annotations']['AnnotationGroups']['Group']:
            name_to_color[d['@Name']] = d['@Color']

        polygons = []
        classes = []
        for polygon_dict in xml['ASAP_Annotations']['Annotations']['Annotation']:
            color = name_to_color[polygon_dict['@PartOfGroup']]
            coords = polygon_dict['Coordinates']['Coordinate'] # list of ordered
            coords = np.array([[float(_['@Y']), float(_['@X'])] for _ in coords])
            polygons.append(coords)
            classes.append(color)
        # Return sorted polygons and their classes
        return sort_polygons(polygons, classes)
