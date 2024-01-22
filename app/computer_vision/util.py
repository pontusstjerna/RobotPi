from math import isqrt

def calc_focal_length(know_distance, known_width, image_width):
    '''This function calculates the focal length. which is used to find the distance between  object and camera 
    :param1 known_distance(int/float) : it is Distance form object to camera measured in real world.
    :param2 known_width(float): it is the real width of object, in real world
    :param3 image_width(float): the width of object in the image, it will be in pixels.
    return focal_length(float): '''
    
    return ((image_width * know_distance) / known_width)

def calc_dist_with_focal_length(focal_length, known_width, image_width):
    '''
    this function basically estimate the distance, it takes the three arguments: focal_length, known_width, image_width
    :param1 focal_length: focal length found through another function .
    param2 known_width : it is the width of object in the real world.
    param3 width of object: the width of object in the image .
    :returns the distance:


    '''
    return ((known_width * focal_length) / image_width)

def calc_dist(known_distance, known_width, image_width):
    focal_length = calc_focal_length(known_distance, known_width, image_width)
    return calc_dist_with_focal_length(focal_length, known_width, image_width)


def get_dist(a, b):
    return isqrt(int(pow(b[0] - a[0], 2)) + int(pow(b[1] - a[1], 2)))

def get_width(img_box):
    return get_dist(img_box[1], img_box[2])
