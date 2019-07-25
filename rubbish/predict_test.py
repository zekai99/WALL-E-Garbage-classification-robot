from __future__ import print_function
from tensorflow.python.keras.models import load_model
import tensorflow as tf
import numpy as np
from PIL import Image
import os
#MODEL_NAME="cats.hd5"
dict={0: "sodacan", 1: "snack_package", 2: "cloth", 3: "battery",4:"plasticbottle"}
graph=tf.get_default_graph()
def classify(model,image):
    global graph
    with graph.as_default():
        result=model.predict(image)
        themax=np.argmax(result)
    return(dict[themax],result[0][themax],themax)
def load_image(image_fname):
    img=Image.open(image_fname)
    #img=img.resize((249,249))
    imgarray=np.array(img)/255.0
    final=np.expand_dims(imgarray,axis=0)
    return final
def main():
    imagelist = os.listdir(fileDir)
    model=load_model("garbage.hd5")
    acc = 0
    total = 0
    for name in imagelist:
        img=load_image(os.path.join(fileDir, name))
        print("name of image is %s"%(os.path.join(fileDir,name)))
        ground_truth = name.split('_')[0]
        label,prob,clas=classify(model,img)
        #print("Ground Truth: {0},  class: {1},  prob: {2:%3.2f},  name: {3}".format(ground_truth, clas, prob, label))
        print("Ground Truth: %s,  class: %d,  prob: %3.2f,  name: %s"%(ground_truth, clas, prob, label))
        #print("we think with certainty %3.2f that it is %s."%(prob,label))
        if int(ground_truth) == clas:
            acc = acc + 1
        total = total + 1
    print("Accuracy: {0}/{1} = {2:.4f}".format(acc, total, (float(acc)/float(total))))
if __name__=="__main__":
    fileDir = "predict/"
    main()
    