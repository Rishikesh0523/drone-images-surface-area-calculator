import cv2
import numpy as np

a4_real_width_mm = 210
a4_real_height_mm = 297

a4_points = []
polygon_points = []
step = 'a4'  # Step toggles between 'a4' and 'polygon'

def click_event(event, x, y, flags, param):
    global a4_points, polygon_points, step

    if event == cv2.EVENT_LBUTTONDOWN:
        if step == 'a4' and len(a4_points) < 4:
            a4_points.append((x, y))
            print(f"A4 corner selected: {(x, y)}")
            if len(a4_points) == 4:
                print("Selected all 4 corners of A4. Now select polygon points around object.")
                step = 'polygon'
        elif step == 'polygon':
            polygon_points.append((x, y))
            print(f"Polygon point added: {(x, y)}")

    elif event == cv2.EVENT_RBUTTONDOWN and step == 'polygon':
        print("Calculating area...")
        calculate_area()

def calculate_area():
    # Order A4 points and compute width/height
    pts = np.array(a4_points, dtype="float32")
    rect = order_points(pts)
    width = np.linalg.norm(rect[0] - rect[1])
    height = np.linalg.norm(rect[0] - rect[3])
    scale_x = a4_real_width_mm / width
    scale_y = a4_real_height_mm / height
    scale = (scale_x + scale_y) / 2

    # Shoelace formula
    area_px = 0.5 * abs(sum(polygon_points[i][0]*polygon_points[(i+1)%len(polygon_points)][1] -
                            polygon_points[(i+1)%len(polygon_points)][0]*polygon_points[i][1]
                            for i in range(len(polygon_points))))
    
    area_mm = area_px * scale * scale
    area_cm = area_mm / 100  # Convert mm^2 to cm^2
    print(f"Estimated area: {area_mm:.2f} square mm")
    print(f"Estimated area: {area_cm:.2f} square cm")

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]     # Top-left
    rect[2] = pts[np.argmax(s)]     # Bottom-right
    rect[1] = pts[np.argmin(diff)]  # Top-right
    rect[3] = pts[np.argmax(diff)]  # Bottom-left

    return rect

def main():
    image_path = input("Enter path to image: ").strip()
    image = cv2.imread(image_path)

    if image is None:
        print("Failed to load image.")
        return

    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", click_event)

    while True:
        temp_image = image.copy()

        # Draw A4 corners
        for pt in a4_points:
            cv2.circle(temp_image, pt, 5, (255, 0, 0), -1)

        # Draw polygon
        for i in range(len(polygon_points)):
            cv2.circle(temp_image, polygon_points[i], 3, (0, 255, 0), -1)
            if i > 0:
                cv2.line(temp_image, polygon_points[i-1], polygon_points[i], (0, 255, 0), 2)
        if len(polygon_points) > 2:
            cv2.line(temp_image, polygon_points[-1], polygon_points[0], (0, 255, 0), 2)

        cv2.imshow("Image", temp_image)
        key = cv2.waitKey(1)
        if key == 13:  # Enter key
            if step == 'polygon':
                calculate_area()
                break
        elif key == 27:  # Esc to exit
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()