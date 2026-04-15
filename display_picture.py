# display_image.py
#   Intelligently crop and scale supplied image
#   and then display on e-ink display.

import argparse
import cv2
#from inky.auto import auto
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from omni_epd import displayfactory, EPDNotFoundError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DISPLAY_TYPE = "waveshare_epd.epd5in65f"
DISPLAY_RESOLUTION = (600, 448)

FONT_FILE = '/home/pi/PiArtAI/ressources/CormorantGaramond-Regular.ttf'
FONT_SIZE = 18

font = ImageFont.truetype(FONT_FILE, FONT_SIZE)
epd = displayfactory.load_display_driver(DISPLAY_TYPE)

# ---------------------------------------------------------------------------
# functions
# ---------------------------------------------------------------------------

def load_image(image_path):
    return cv2.imread(image_path)

def save_image(image_path, image):
    print(f"\nSaving to image filepath : {image_path}")
    return cv2.imwrite(image_path, image)

def crop(image, disp_w, disp_h, intelligent=True):
    # Intelligently resize and crop image to display proportions.
    # Largest crop shifted towards maximum saliency. 

    img_h, img_w, img_c = image.shape
    print(f"Input WxH: {img_w} x {img_h}")

    img_aspect = img_w / img_h
    disp_aspect = disp_w / disp_h

    print(f"Image aspect ratio {img_aspect} ({img_w} x {img_h})")
    print(f"Display aspect ratio {disp_aspect} ({disp_w} x {disp_h})")

    if img_aspect < disp_aspect:
        # scale width, crop height.
        resize = (disp_w, int(disp_w / img_aspect))
    else:
        # scale height, crop width
        resize = (int(disp_h * img_aspect), disp_h)

    print(f"Resizing to {resize}")
    image = cv2.resize(image, resize)
    img_h, img_w, img_c = image.shape

    # Cropping
    x_off = int((img_w - disp_w) / 2)
    y_off = int((img_h - disp_h) / 2)
    assert x_off == 0 or y_off == 0, "My logic is broken"

    if intelligent:

        # Initialize OpenCV's static saliency spectral residual detector and
        # compute the saliency map
        saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
        (success, saliencyMap) = saliency.computeSaliency(image)
        saliencyMap = (saliencyMap * 255).astype("uint8")

        if not x_off:
            # Cropping height
            vert = np.max(saliencyMap, axis=1)
            vert = np.convolve(vert, np.ones(64)/64, "same")
             
            sal_centre = int(np.argmax(vert))
            img_centre = int(img_h / 2)
            shift_y = max(min(sal_centre - img_centre, y_off), -y_off)
            y_off += shift_y
        else:
            # Cropping width
            horiz = np.max(saliencyMap, axis=0)
            horiz  = np.convolve(horiz, np.ones(64)/64, "same")
            sal_centre = int(np.argmax(horiz))
            img_centre = int(img_w / 2)
            shift_x = max(min(sal_centre - img_centre, x_off), -x_off)
            x_off += shift_x

    image = image[y_off:y_off + disp_h,
                  x_off:x_off + disp_w]

    img_h, img_w, img_c = image.shape
    print(f"Cropped WxH: {img_w} x {img_h}")
    return image


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("image", 
        help="relative file path to input image")
    ap.add_argument("-p", "--portrait", action="store_true",
                    default=False, help="Portrait orientation")
    ap.add_argument("-c", "--centre_crop", action="store_true",
                    default=False, help="Simple centre cropping")
    ap.add_argument("-r", "--resize_only", action="store_true",
                    default=False, help="Simply resize image to display ignoring aspect ratio")
    ap.add_argument("-s", "--simulate_display", action="store_true",
                    default=False, help="Do not interact with e-paper display to get resolution")
    ap.add_argument("--width", default=0, type=int, help="The width of the display")
    ap.add_argument("--height", default=0, type=int, help="The height of the display")
    args = vars(ap.parse_args())

    
    simulate_display = args["simulate_display"]
    image_path = args["image"]
    if args["width"] != 0 and args["height"] != 0:
        DISPLAY_RESOLUTION = (args["width"], args["height"])
    # # Swap axes for portrait orientation
    if args["portrait"]:
        DISPLAY_RESOLUTION = (DISPLAY_RESOLUTION[1], DISPLAY_RESOLUTION[0])

    canvas = Image.new(mode="RGB", size=DISPLAY_RESOLUTION, color="white")
    image = load_image(image_path)
    
    if args["resize_only"]:
        print(f"Resizing to {DISPLAY_RESOLUTION[0]}x{DISPLAY_RESOLUTION[1]}")
        image = cv2.resize(image, (DISPLAY_RESOLUTION[0], DISPLAY_RESOLUTION[1]))
        save_image(image_path, image)
    else:
        image = crop(image, DISPLAY_RESOLUTION[0], DISPLAY_RESOLUTION[1], args["centre_crop"]==False)
        save_image(image_path, image)

    im2 = Image.open(args["image"])
    canvas.paste(im2, (0,0))
    im3 = ImageDraw.Draw(canvas)    
    
    if not simulate_display:
        epd.prepare()
        epd.display(canvas)
        epd.sleep()


