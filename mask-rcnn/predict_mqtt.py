import os
import sys
import random
import math
import tensorflow as tf
import numpy as np
import skimage.io
import matplotlib
from matplotlib import patches
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
from io import BytesIO
from tensorflow.python.keras.models import load_model
from tensorflow.python.keras.backend import set_session
from skimage.measure import find_contours

# Root directory of the project
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize
# Import COCO config
sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version
import coco
#----------------------------------------------------------
# tf_config = some_custom_config
# sess = tf.Session(config=tf_config)
# dict = {0: "Maine_Coon", 1: "Ocelot", 2: "Singapura", 3: "Turkish_Van"}
dict = {0:"battery", 1:"cloth", 2:"plasticbottle", 3:"snack_package", 4:"soda_can"}
colors = visualize.random_colors(100)
#----------------------------------------------------------
# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

# Local path to trained weights file
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "checkpoint/mask_rcnn_coco.h5")
INCEP_MODEL_PATH = os.path.join(ROOT_DIR, "checkpoint/rubbish.hd5")

# Download COCO trained weights from Releases if needed
if not os.path.exists(COCO_MODEL_PATH):
    utils.download_trained_weights(COCO_MODEL_PATH)

# Directory of images to run detection on
IMAGE_DIR = os.path.join(ROOT_DIR, "images")

class InferenceConfig(coco.CocoConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

config = InferenceConfig()
config.display()

# Create model object in inference mode.
model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)

sess = tf.Session()
graph = tf.get_default_graph()
set_session(sess)
incep_model = load_model(INCEP_MODEL_PATH)
# incep_model._make_predict_function()

# Load weights trained on MS-COCO
model.load_weights(COCO_MODEL_PATH, by_name=True)
model.keras_model._make_predict_function()

# COCO Class names
# Index of the class in the list is its ID. For example, to get ID of
# the teddy bear class, use: class_names.index('teddy bear')
class_names = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
               'bus', 'train', 'truck', 'boat', 'traffic light',
               'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
               'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
               'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
               'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
               'kite', 'baseball bat', 'baseball glove', 'skateboard',
               'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
               'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
               'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
               'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
               'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
               'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
               'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
               'teddy bear', 'hair drier', 'toothbrush']

############################################################
#  Inception
############################################################
# import paho.mqtt.client as mqtt

def classify(model, image):
    global sess
    global graph
    # graph = tf.get_default_graph()
    image = image.resize((249, 249))
    imgarray = np.array(image)/255.0
    final = np.expand_dims(imgarray, axis=0)
    with graph.as_default():
        set_session(sess)
        result = model.predict(final)
        themax = np.argmax(result)
    return(dict[themax], result[0][themax], themax)

def inception(image, boxes, masks, class_ids, class_names,
                      scores=None, title="",
                      figsize=(16, 16), ax=None,
                      show_mask=True, show_bbox=True,
                      colors=None, captions=None, load_file=None, save_file=None):
    """
    boxes: [num_instance, (y1, x1, y2, x2, class_id)] in image coordinates.
    masks: [height, width, num_instances]
    class_ids: [num_instances]
    class_names: list of class names of the dataset
    scores: (optional) confidence scores for each box
    title: (optional) Figure title
    show_mask, show_bbox: To show masks and bounding boxes or not
    figsize: (optional) the size of the image
    colors: (optional) An array or colors to use with each object
    captions: (optional) A list of strings to use as captions for each object
    """
    imgg = Image.open(load_file)
    # Number of instances
    N = boxes.shape[0]
    if not N:
        print("\n*** No instances to display *** \n")
    else:
        assert boxes.shape[0] == masks.shape[-1] == class_ids.shape[0]

    # If no axis is passed, create one and automatically call show()
    auto_show = False
    if not ax:
        _, ax = plt.subplots(1, figsize=figsize)
        auto_show = True

    # Generate random colors
    # colors = colors or visualize.random_colors(N)

    # Show area outside image boundaries.
    height, width = image.shape[:2]
    # ax.set_ylim(height + 10, -10)
    # ax.set_xlim(-10, width + 10)
    ax.axis('off')
    ax.set_title(title)
    masked_image = image.astype(np.uint32).copy()
    ss = str(N) #第一个数：总数
    for i in range(N):
        color = colors[i]
        # Bounding box
        if not np.any(boxes[i]):
            # Skip this instance. Has no bbox. Likely lost in image cropping.
            continue
        y1, x1, y2, x2 = boxes[i]
        # print(y1, x1, y2, x2)
        img_cut = imgg.crop((x1, y1, x2, y2))
        ss = ss + ':' + str(int((x1 + x2 - width)/2)) #距离中心的像素值
        _,prob,clas = classify(incep_model, img_cut)

        if show_bbox:
            p = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2,
                                alpha=0.7, linestyle="dashed",
                                edgecolor=color, facecolor='none')
            ax.add_patch(p)

        # Label
        if not captions:
            # class_id = class_ids[i]
            class_id = clas
            # score = scores[i] if scores is not None else None
            score = prob
            # label = class_names[class_id]
            label = dict[clas]
            caption = "{} {} {:.3f}".format(i+1, label, score) if score else label
        else:
            caption = captions[i]

        ax.text(x1, y1 + 8, caption,
                color='w', size=11, backgroundcolor="none")

        # Mask
        mask = masks[:, :, i]
        if show_mask:
            masked_image = visualize.apply_mask(masked_image, mask, color)

        # Mask Polygon
        # Pad to ensure proper polygons for masks that touch image edges.
        padded_mask = np.zeros(
            (mask.shape[0] + 2, mask.shape[1] + 2), dtype=np.uint8)
        padded_mask[1:-1, 1:-1] = mask
        contours = find_contours(padded_mask, 0.5)
        for verts in contours:
            # Subtract the padding and flip (y, x) to (x, y)
            verts = np.fliplr(verts) - 1
            p = Polygon(verts, facecolor="none", edgecolor=color)
            ax.add_patch(p)
    ax.imshow(masked_image.astype(np.uint8))
    if auto_show:
        fig = plt.gcf()
        fig.set_size_inches(width/96.0,height/96.0)
        plt.subplots_adjust(top=1,bottom=0,left=0,right=1,hspace=0, wspace=0)  
        plt.margins(0,0)
        plt.savefig(save_file,dpi=96.0,pad_inches=0.0) 
        return ss
        # plt.show()
        # plt.savefig(image_file, bbox_inches='tight', dpi=image.dpi, pad_inches=0.0)
        # plt.savefig(image_file, transparent=True, bbox_inches='tight', pad_inches=0.0)

def classify_mqtt(load_file, save_file):
    image = skimage.io.imread(load_file)

    # Run detection
    # model.keras_model._make_predict_function()
    results = model.detect([image], verbose=1)

    # Visualize results
    r = results[0]
    s = inception(image, r['rois'], r['masks'], r['class_ids'], 
                                class_names, r['scores'], colors=colors, 
                                load_file=load_file, save_file=save_file)
    return s