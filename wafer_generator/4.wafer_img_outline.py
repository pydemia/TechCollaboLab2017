import os
from os import path
import numpy as np
from PIL import Image, ImageOps, ImageDraw
import math

# To read/write files
path_src = "./data/txt"
path_out = "./data/img"
abspath_src = path.abspath(path_src)
abspath_out = path.abspath(path_out)
file_pathes = [path.join(abspath_src, name)\
               for name in os.listdir(path_src)\
               if path.isfile(path.join(abspath_src, name))]

# To draw outlines
img_dim = 299
wf_dim = 140
offset_y = 2
offset_cut = 135
x = math.sqrt(wf_dim**2 - offset_cut**2)
theta = math.atan(x / offset_cut) * 180 / math.pi

# Drawing Wafer Map
for file iin file_paths:
    data = np.genfromtxt(file, delimiter=';', dtype=None)
    coordinates = data[data[:,4]==b'W'][:,2:4].astype(np.uint8)
    array = np.zeros(shape=(50,70), dtype=np.unit8)
    array[coordinates[:,1], coordinates[:,0]] = 255
    img = Image.fromarray(array).crop((8, 9, 64, 43))\
                                .resize((img_dim, img_dim))
    img = ImageOps.invert(img)

    # Drawing Outline
    draw = ImageDraw.Draw(img)
    draw.arc([(img_dim/2-wf_dim, img_dim/2-wf_dim+offset_y),
              (img_dim/2+wf_dim, img_dim/2+wf_dim+offset_y)],
              start=90.+theta, end=450.-theta, fill='black')
    draw.line([(img_dim/2, img_dim/2+offset_cut+offset_y),
              (img_dim/2, img_dim/2+offset_cut+offset_y)],
              fill='black', width=1)
    del draw

    #img.show()
    img_filename = file.replace(path.sep+'txt'+path.sep,
                                path.sep+'img'+path.sep)[:-4] + '.png'
    img.save(img_filename)

    # Loogging
    lot_id = file.split(path.sep)[-1].split('.')[0]
    print(lot_id, '-- image generated')
    #break
