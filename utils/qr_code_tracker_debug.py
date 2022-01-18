from cmath import sqrt
import cv2

def get_dist(a, b):
    return sqrt(pow(b[0] - a[0], 2) + pow(b[1] - a[1], 2))

# set up camera object
cap = cv2.VideoCapture(0)

# QR code detection object
detector = cv2.QRCodeDetector()

while True:
    # get the image
    _, img = cap.read()
    # get bounding box coords and data
    data, bounding_box, _ = detector.detectAndDecode(img)

    height, width, _ = img.shape

    #if there is a bounding box, draw one, along with the data
    if bounding_box is not None:
        points = bounding_box[0]
        top_left_corner = points[0]
        #center_point = [int(points[0][0] - points[2][0] * 0.5), int(points[0][1] + points[2][1] * 0.5)]
        #print(f"Top left corner: {points[0]}")
        print(f"Dist across top left and top bottom: {get_dist(points[0], points[2])}")
        
        print(f"Center point: {top_left_corner}")
        print(f"Width: {width}, Height: {height}")

        print(f"{'top' if top_left_corner[1] < height / 2 else 'bottom'} {'left' if top_left_corner[0] < width / 2 else 'right'}")

        if data: print("data found: ", data)
    
    if(cv2.waitKey(1) == ord("q")):
        break
# free camera object and exit
cap.release()
cv2.destroyAllWindows()