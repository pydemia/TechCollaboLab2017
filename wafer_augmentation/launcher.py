from common import ui, common
from tkinter import filedialog
from os import path, listdir, mkdir
from PIL import Image, ImageTk, ImageDraw
import math

DEFAULT_DIR = "./data"
SAVE_DIR = "./patches"
CONFIG_FILE = "config.txt"

class Launcher(ui.AppFrame):
    # Initialize
    def __init__(self, xml):
        super().__init__(xml)
        self.set_title("Wafer Map Augumentation")
        self.config = {"curved" : {},
                       "straight" : {},
                       "defocus" : {},
                       "bull" : {},
                       "dounut" : {},
                       "random" : {},
                       "other" : {}}
        self._load_config()

        # Initalize LabelFrame1 (Save Folder)
        self.set("lbSaveFolder", "Save Folder")
        self.set("lbGenerateNum", "Generate #")

        # Initalize LabelFrame2 (Wafer Image)
        self.set("lbWaferImage", "Wafer")
        self._initCanvas()

        # Initalize LabelFrame3

        # Initalize DynamicLabelFrames
        self.count = {"curved" : 0,
                      "straight" : 0,
                      "defocus" : 0,
                      "bull" : 0,
                      "dounut" : 0,
                      "random" : 0,
                      "other" : 0}

    def run(self):
        while (self.flag_terminate is not True):
            #self.update_idletasks()
            common.delay()
            self.update()

    # Private Functions
    def _initCanvas(self):
        x1, y1, x2, y2 = None, None, None, None
        self.rect = None
        self.area = {"posX" : 0,
                     "posY" : 0,
                     "width" : 0,
                     "height" : 0}
        def draw_outline(img):
            wf_dim = 140
            offset_y = 2
            offset_cut = 135
            img_dim = 299
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
        def bind_img(canvas_name, img):
            canvas = self.find(canvas_name)
            canvas.background = ImageTk.PhotoImage(img)
            canvas.create_image(0, 0, image=canvas.background, anchor='nw') 
        def print_rectangle():
            self.area["posX"] = x1 if(x1<x2) else x2
            self.area["posY"] = y1 if(y1<y2) else y2
            self.area["width"] = abs(x2 - x1)
            self.area["height"] = abs(y2 - y1)
        def reset_rectagle(event):
            nonlocal x1, y1
            x1, y1 = (event.x-1), (event.y-1)
            if(x1 < 0):
                x1 = 0
            if(y1 < 0):
                y1 = 0
            self.elements["cvWaferImage"].delete(self.rect)
        def draw_rectangle(event):
            nonlocal x2, y2
            x2, y2 = (event.x-1), (event.y-1)
            if(x2 <= 1):
                x2 = 1
            elif(x2 >= 299):
                x2 = 299
            if(y2 <= 1):
                y2 = 1
            elif(y2 >= 299):
                y2 = 299
            self.rect = self.elements["cvWaferImage"].create_rectangle(x1+1, y1+1,
                                                                x2+1, y2+1, outline='red')
            print_rectangle()
        self.elements["cvWaferImage"].bind("<Button-1>", reset_rectagle)
        self.elements["cvWaferImage"].bind("<ButtonRelease-1>", draw_rectangle)
        img = Image.new('L', (299, 299), 255)
        img = draw_outline(img)
        bind_img("cvWaferImage", img)

    def _load_config(self):
        self.set("enSaveFolder", path.abspath(DEFAULT_DIR))
        self.curr_file = 1
        if(path.isfile(CONFIG_FILE)):
            with open(CONFIG_FILE, 'r') as f:
                conf = f.readlines()
                for i in range(len(conf)):
                    try:
                        att, val = [text.strip() for text in conf[i].split('=')]
                        pattern, attrib = [text.strip() for text in att.split('_')]
                        self.config[pattern][attrib] = int(val)
                    except:
                        ui.messagebox.showerror("Wrong Configuration", "[Line" + str(i+1) +"] Wrong Configuration. Check the 'config.txt' file")

    # Events
    def btnBrowse_Click(self):
        targetFolder = filedialog.askdirectory(initialdir=self.get("enSaveFolder"),
                                               title="Please select location of raw wafer images")
        if(targetFolder != ""):
            self.set("enSaveFolder", targetFolder)
            self._make_filelist()

    class Options(ui.Tk.LabelFrame):
        def __init__(self, master, pattern, **options):
            ui.Tk.LabelFrame.__init__(self, master.frame, **options)
            self.name = pattern
            self.count = master.count[pattern]
            self.master = master
            self.elements = {}
            self.variables = {}
            self.elements["ckFlip"] = ui.Tk.Checkbutton(self, text="@ Flip", indicatoron=0, width=14, anchor=ui.Tk.constants.W).grid(row=0, column=0, sticky=ui.Tk.constants.W)
            self.variables["ckFlip_Vertical"] = ui.Tk.BooleanVar()
            self.variables["ckFlip_Horizontal"] = ui.Tk.BooleanVar()
            self.elements["ckFlip_Vertical"] = ui.Tk.Checkbutton(self, text="Vertical", width=11, variable=self.variables["ckFlip_Vertical"], anchor=ui.Tk.constants.W).grid(row=1, column=0, sticky=ui.Tk.constants.W)
            self.elements["ckFlip_Horizontal"] = ui.Tk.Checkbutton(self, text="Horizontal", width=11, variable=self.variables["ckFlip_Horizontal"], anchor=ui.Tk.constants.W).grid(row=2, column=0, sticky=ui.Tk.constants.W)
            self.elements["ckRotate"] = ui.Tk.Checkbutton(self, text="@ Rotate", indicatoron=0, width=11, anchor=ui.Tk.constants.W).grid(row=0, column=1, columnspan=2, sticky=ui.Tk.constants.W)
            self.elements["lbRotate_Min"] = ui.Tk.Label(self, text="Min(°)", width=5).grid(row=1, column=1, sticky=ui.Tk.constants.W)
            self.elements["lbRotate_Max"] = ui.Tk.Label(self, text="Max(°)", width=5).grid(row=2, column=1, sticky=ui.Tk.constants.W)
            self.variables["enRotate_Min"] = ui.Tk.IntVar()
            self.variables["enRotate_Max"] = ui.Tk.IntVar()
            self.elements["enRotate_Min"] = ui.Tk.Entry(self, width=5, textvariable=self.variables["enRotate_Min"]).grid(row=1, column=2, sticky=ui.Tk.constants.W)
            self.elements["enRotate_Max"] = ui.Tk.Entry(self, width=5, textvariable=self.variables["enRotate_Max"]).grid(row=2, column=2, sticky=ui.Tk.constants.W)
            self.elements["ckShift"] = ui.Tk.Checkbutton(self, text="@ Shift", indicatoron=0, width=23, anchor=ui.Tk.constants.W).grid(row=0, column=3, columnspan=4, sticky=ui.Tk.constants.W)
            self.elements["lbShift_PosX"] = ui.Tk.Label(self, text="PosX", width=5).grid(row=1, column=3, sticky=ui.Tk.constants.W)
            self.elements["lbShift_PosY"] = ui.Tk.Label(self, text="PosY", width=5).grid(row=2, column=3, sticky=ui.Tk.constants.W)
            self.variables["enShift_PosX"] = ui.Tk.IntVar()
            self.variables["enShift_PosY"] = ui.Tk.IntVar()
            self.elements["enShift_PosX"] = ui.Tk.Entry(self, width=5, textvariable=self.variables["enShift_PosX"]).grid(row=1, column=4, sticky=ui.Tk.constants.W)
            self.elements["enShift_PosY"] = ui.Tk.Entry(self, width=5, textvariable=self.variables["enShift_PosY"]).grid(row=2, column=4, sticky=ui.Tk.constants.W)
            self.elements["lbShift_Width"] = ui.Tk.Label(self, text="Width", width=5).grid(row=1, column=5, sticky=ui.Tk.constants.W)
            self.elements["lbShift_Height"] = ui.Tk.Label(self, text="Height", width=5).grid(row=2, column=5, sticky=ui.Tk.constants.W)
            self.variables["enShift_Width"] = ui.Tk.IntVar()
            self.variables["enShift_Height"] = ui.Tk.IntVar()
            self.elements["enShift_Width"] = ui.Tk.Entry(self, width=5, textvariable=self.variables["enShift_Width"]).grid(row=1, column=6, sticky=ui.Tk.constants.W)
            self.elements["enShift_Height"] = ui.Tk.Entry(self, width=5, textvariable=self.variables["enShift_Height"]).grid(row=2, column=6, sticky=ui.Tk.constants.W)
            self.elements["ckScale"] = ui.Tk.Checkbutton(self, text="@ Scale", indicatoron=0, width=11, anchor=ui.Tk.constants.W).grid(row=0, column=8, columnspan=2, sticky=ui.Tk.constants.W)
            self.elements["lbScale_Min"] = ui.Tk.Label(self, text="Min(%)", width=5).grid(row=1, column=8, sticky=ui.Tk.constants.W)
            self.elements["lbScale_Max"] = ui.Tk.Label(self, text="Max(%)", width=5).grid(row=2, column=8, sticky=ui.Tk.constants.W)
            self.variables["enScale_Min"] = ui.Tk.IntVar()
            self.variables["enScale_Max"] = ui.Tk.IntVar()
            self.elements["enScale_Min"] = ui.Tk.Entry(self, width=5, textvariable=self.variables["enScale_Min"]).grid(row=1, column=9, sticky=ui.Tk.constants.W)
            self.elements["enScale_Max"] = ui.Tk.Entry(self, width=5, textvariable=self.variables["enScale_Max"]).grid(row=2, column=9, sticky=ui.Tk.constants.W)
            self.elements["ckShear"] = ui.Tk.Checkbutton(self, text="@ Shear", indicatoron=0, width=11, anchor=ui.Tk.constants.W).grid(row=0, column=10, columnspan=2, sticky=ui.Tk.constants.W)
            self.elements["lbShear_Min"] = ui.Tk.Label(self, text="Min(°)", width=5).grid(row=1, column=10, sticky=ui.Tk.constants.W)
            self.elements["lbShear_Max"] = ui.Tk.Label(self, text="Max(°)", width=5).grid(row=2, column=10, sticky=ui.Tk.constants.W)
            self.variables["enShear_Min"] = ui.Tk.IntVar()
            self.variables["enShear_Max"] = ui.Tk.IntVar()
            self.elements["enShear_Min"] = ui.Tk.Entry(self, width=5, textvariable=self.variables["enShear_Min"]).grid(row=1, column=11, sticky=ui.Tk.constants.W)
            self.elements["enShear_Max"] = ui.Tk.Entry(self, width=5, textvariable=self.variables["enShear_Max"]).grid(row=2, column=11, sticky=ui.Tk.constants.W)
            self.elements["btnReset"] = ui.Tk.Button(self, text="Reset", width=11).grid(row=0, column=12, sticky=ui.Tk.constants.W)
            self.elements["btnAreaApply"] = ui.Tk.Button(self, text="Area Apply", width=11, command=self.apply).grid(row=1, column=12, sticky=ui.Tk.constants.W)
            self.elements["btnDelete"] = ui.Tk.Button(self, text="Delete", width=11, command=self.destroy).grid(row=2, column=12, sticky=ui.Tk.constants.W)
            self.set_init()
            self.set_config()
            master.count[pattern] += 1

        def set_init(self):
            base=None
            pattern = self.name
            if(pattern=="curved"):
                self.config(text="Curved-Line "+str(self.count+1))
                base=10
            elif(pattern=="straight"):
                self.config(text="Straight-Line "+str(self.count+1))
                base=20
            elif(pattern=="defocus"):
                self.config(text="Defocus "+str(self.count+1))
                base=30
            elif(pattern=="bull"):
                self.config(text="Bull's Eye "+str(self.count+1))
                base=40
            elif(pattern=="dounut"):
                self.config(text="Dounut "+str(self.count+1))
                base=50
            elif(pattern=="random"):
                self.config(text="Random Noise "+str(self.count+1))
                base=60
            elif(pattern=="other"):
                self.config(text="Others "+str(self.count+1))
                base=70
            self.grid(row=base+self.count, column=0, columnspan=6, padx=2, pady=2)

        def set_config(self):
            pattern = self.name
            config = self.master.config[pattern]
            for attrib in config
            self.variables[""]

        def apply(self):
            self.variables["enShift_PosX"].set(self.master.area["posX"])
            self.variables["enShift_PosY"].set(self.master.area["posY"])
            self.variables["enShift_Width"].set(self.master.area["width"])
            self.variables["enShift_Height"].set(self.master.area["height"])

        def destroy(self):
            self.master.count[self.name] -= 1
            ui.Tk.LabelFrame.destroy(self)
            for i in range(self.count + 1, self.master.count[self.name]+1):
                self.master.elements[self.name+str(i+1)].count -= 1
                self.master.elements[self.name+str(i+1)].set_init(self.name)
                self.master.elements[self.name+str(i)] = self.master.elements[self.name+str(i+1)]
                del self.master.elements[self.name+str(i+1)]

    def add_element(self, pattern):
        self.elements[pattern + str(self.count[pattern])] = self.Options(self, pattern)

    def btnCurvedLine_Click(self):
        self.add_element("curved")
    def btnStraightLine_Click(self):
        self.add_element("straight")
    def btnDefocus_Click(self):
        self.add_element("defocus")
    def btnBullsEye_Click(self):
        self.add_element("bull")
    def btnDounut_Click(self):
        self.add_element("dounut")
    def btnRandomNoise_Click(self):
        self.add_element("random")
    def btnOthers_Click(self):
        self.add_element("other")

    def btnGenerate_Click(self):
        return
    def btnClose_Click(self):
        self.flag_terminate = True
        return


if __name__ == '__main__':
    # Load UI Layout
    app = Launcher('layout.xml')
    app.run()