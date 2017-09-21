import os
from os import path
import numpy as np
from PIL import Image, ImageOps, ImageDraw
import math

##### TODO #####
# 1. Add 'Center Shift' to draw_circle(inner circle)
# 2. Add 'Varying Thickness' to draw_line
# 3. Add Other Patterns (Like Defocus, Dounut, Radial Lines ...)
# 4. Add a fuction to draw Arc Patterns(Not a Circle)
# 5. Enhance Noise Pattern

# To write files
relpath = "./"
abspath = path.abspath(relpath)

# Constants
BLACK = 0
WHITE = 255
die_area = (8, 9, 64, 43)
arr_dim = (die_area[3]-die_area[1], die_area[2]-die_area[0])
img_dim = 299

# --------------------------------
# Make Circle using a Radius
# --------------------------------
def draw_circle(array, center, radius=140, weight=10, color='black'):
    img = Image.new(mode='1', size=(img_dim, img_dim), color='white')
    draw = ImageDraw.Draw(img)
    draw.ellipse([(center[0]-radius, center[1]-radius),
                  (center[0]+radius, center[1]+radius)],
                 outline=color, fill=color) # outer
    draw.ellipse([(center[0]-radius+weight, center[1]-radius+weight),
                  (center[0]+radius-weight, center[1]+radius-weight)],
                 outline=color, fill='white') # innor
    del draw
    mask_arr = np.array(img.resize((arr_dim[1], arr_dim[0])).getdata(), np.uint8)\
                 .reshape(arr_dim)
    mask = mask_arr == BLACK
    array[mask] = BLACK
    return array

# --------------------------------
# Draw Straight Line
# --------------------------------
def draw_line(array, position, weight=10, color='black'):
    img = Image.new(mode='1', size=(img_dim, img_dim), color='white')
    draw = ImageDraw.Draw(img)
    draw.line(position, fill=color, width=weight)
    del draw
    mask_arr = np.array(img.resize((arr_dim[1], arr_dim[0])).getdata(), np.uint8)\
                 .reshape(arr_dim)
    mask = mask_arr == BLACK
    array[mask] = BLACK
    return array

# --------------------------------
# Add Noise
# --------------------------------
def add_noise(array, count, color=BLACK):
    mask = np.zeros(shape=arr_dim[0]*arr_dim[1], dtype=np.bool)
    mask[:count] = True
    np.random.shuffle(mask)
    mask = mask.reshape(arr_dim)
    array[mask] = color
    return array

# --------------------------------
# Make Wafer Map Mask
# --------------------------------
def adjust_mask(array):
    # ellipse aprameters(x0, y0, a, b) for mask of ellipse shape
    x0 = arr_dim[1]/2;
    y0 = arr_dim[0]/2;
    a = (img_dim+1)/arr_dim[0]+0.1;
    b = (img_dim+1)/arr_dim[1]
    x = np.linspace(0, arr_dim[1], arr_dim[1])
    y = np.linspace(0, arr_dim[0], arr_dim[0])[:,None]
    mask_threshold = 14 # mask ellipse has 2 different curvatures. threshold height
    mask_upper = ((x-x0)/a)**2 + ((y-y0)/b)**2 <= 8.0 # 8.0 is heuristic value
    mask_lower = ((x-x0)/a)**2 + ((y-y0)/b)**2 <= 8.2 # 8.2 is heuristic value
    mask = np.concatenate((mask_upper[:mask_threshold, :],
                           mask_lower[mask_threshold:, :]), axis=0)
    mask[-3,21:35] = True;
    array[~mask] = WHITE
    return array

# --------------------------------
# Draw Outline (arc + line)
# --------------------------------
def draw_outline(img):
    wf_dim = 140
    offset_y = 2
    offset_cut = 135
    x = math.sqrt(wf_dim**2 - offset_cut**2)
    theta = math.atan(x / offset_cut) * 180 / math.pi

    draw = ImageDraw.Draw(img)
    draw.arc([(img_dim/2-wf_dim, img_dim/2-wf_dim+offset_y),
              (img_dim/2+wf_dim, img_dim/2+wf_dim+offset_y)],
             start=90.+theta, end=450.-theta, fill='black')
    draw.line([(img_dim/2-x, img_dim/2+offset_cut+offset_y),
               (img_dim/2+x, img_dim/2+offset_cut+offset_y)],
              fill='black', width=1)
    del draw
    return img

def make_random_wafer_img(filename, arc_para, line_para, noise_para, outline=True):
    # 1. Set Parameters
    arc_num = arc_para[0]
    arc_para= arc_para[1]

    line_num = line_para[0]
    line_para = line_para[1]

    noise_black_num = noise_para[0]
    noise_white_num = noise_para[1]

    # 2. Make an Empty Wafer as array
    array = np.full(shape=arr_dim, fill_value=WHITE, dtype=np.uint8)

    # 3. Draw Random Arcs
    for i in range(0, arc_num):
        array = draw_circle(array, center=arc_para[i][0],
                                   radius=arc_para[i][1],
                                   weight=arc_para[i][2])

    # 4. Draw Random Lines
    for i in range(0, line_num):
        array = draw_line(array, position=line_para[i][0],
                                 weight=line_para[i][1])

    # 5. Add Noise
    array = add_noise(array, noise_black_num, color=BLACK)
    array = add_noise(array, noise_white_num, color=WHITE)

    # 6. Adjust Mask
    array = adjust_mask(array)

    # 7. Resize
    img = Image.fromarray(array).resize((img_dim, img_dim)) # resizing

    # 8. Draw Outline
    if outline:
        img = draw_outline(img)

    # 9. Save Image
    #img.show()
    img.save(abspath + path.sep + filename + '.png')
    print(filename + ' -- image generated')


if __name__ == '__main__':
    # --------------------------------
    # Set Parameters
    # --------------------------------
    filename = 'test'

    arc_num = 2
    arc_para = []
    # ((center.x, center.y), radius, stroke_weight)
    arc_para.append(((0,0), 160, 13))
    arc_para.append(((250,50), 160, 13))
    arc_para = (arc_num, arc_para)

    line_num = 1
    line_para = []
    # (position([start.x, start.y), (end.x, end.y)]), stroke_weight)
    line_para.append(([(0,0), (150, 350)], 9))
    line_para = (line_num, line_para)

    noise_black_num = 130 # num of black noise
    noise_white_num = 50 # num of black noise
    noise_para = (noise_black_num, noise_white_num)

    # --------------------------------
    # Make Wafer Image
    # --------------------------------
    make_random_wafer_img(filename, arc_para, line_para, noise_para, outline=True)