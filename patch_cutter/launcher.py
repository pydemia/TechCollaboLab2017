from common import ui, common
from tkinter import filedialog
from os import path, listdir, mkdir
from PIL import Image,ImageTk

DEFAULT_DIR = "./data"
SAVE_DIR = "./patches"
CONFIG_FILE = "config.txt"

class Launcher(ui.AppFrame):
    # Initialize
    def __init__(self, xml):
        super().__init__(xml)
        self.set_title("Patch Cutter")

        # Initalize LabelFrame1 (Folder and File)
        self.set("lbTargetFolder", "Target Folder")
        self.set("lbTargetFile", "Current File")
        self.filelist = []
        self._load_config()
        self._make_filelist()

        # Initalize LabelFrame2 (Wafer Image)
        self.set("lbWaferImageRaw", "Raw Wafer Image")
        self.set("lbWaferImagePatch", "Crop Region")
        self._initCanvas()

        # Initalize LabelFrame3
        # Initalize LabelFrame4 (Pattern Class)
        self._initRadioButton()

        # Initalize LabelFrame5
        self.set("lbPatchPositionX", "PositionX")
        self.set("lbPatchPositionY", "PositionY")
        self.set("lbPatchWidth", "Width")
        self.set("lbPatchHeight", "Height")

    def run(self):
        while (self.flag_terminate is not True):
            #self.update_idletasks()
            common.delay()
            self.update()

    # Private Functions
    def _initRadioButton(self):
        self.variables["Class"] = ui.Tk.StringVar()
        self.variables["Class"].set("curved") # initialize
        self.find("rbCurvedLine").config(variable = self.variables["Class"], value = "curved")
        self.find("rbStraightLine").config(variable = self.variables["Class"], value = "straight")
        self.find("rbDefocus").config(variable = self.variables["Class"], value = "defocus")
        self.find("rbBullsEye").config(variable = self.variables["Class"], value = "bull")
        self.find("rbDounut").config(variable = self.variables["Class"], value = "dounut")
        self.find("rbRandomNoise").config(variable = self.variables["Class"], value = "random")
        self.find("rbOthers").config(variable = self.variables["Class"], value = "other")

    def _initCanvas(self):
        x1, y1, x2, y2 = None, None, None, None
        self.area = None
        def print_rectangle():
            self.set("enPatchPositionX", x1 if(x1<x2) else x2)
            self.set("enPatchPositionY", y1 if(y1<y2) else y2)
            self.set("enPatchWidth", abs(x2 - x1))
            self.set("enPatchHeight", abs(y2 - y1))
        def reset_rectagle(event):
            nonlocal x1, y1
            x1, y1 = (event.x-1), (event.y-1)
            if(x1 < 0):
                x1 = 0
            if(y1 < 0):
                y1 = 0
            self.elements["cvWaferImagePatch"].delete(self.area)
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
            self.area = self.elements["cvWaferImagePatch"].create_rectangle(x1+1, y1+1,
                                                                x2+1, y2+1, outline='red')
            print_rectangle()
        self.elements["cvWaferImagePatch"].bind("<Button-1>", reset_rectagle)
        self.elements["cvWaferImagePatch"].bind("<ButtonRelease-1>", draw_rectangle)

    def _load_config(self):
        self.set("enTargetFolder", path.abspath(DEFAULT_DIR))
        self.curr_file = 1
        if(path.isfile(CONFIG_FILE)):
            with open(CONFIG_FILE, 'r') as f:
                for line in f.readlines():
                    attrib, val = [text.strip() for text in line.split('=')]
                    if(attrib == "dir"):
                        self.set("enTargetFolder", val)
                    elif(attrib == "curr_file"):
                        self.curr_file = int(val)

    def _make_filelist(self):
        dir_path = self.get("enTargetFolder")
        self.filelist = [f for f in listdir(dir_path)\
                         if path.isfile(path.join(dir_path, f))]
        print(self.filelist)
        if((len(self.filelist) > 0) and (len(self.filelist) <= self.curr_file)):
            self._update_currentfile()
        else:
            self.set("enTargetFile", "")
            self.set("lbCurrentFileSeq", "")
            ui.messagebox.showerror("파일 부족", "파일이 부족합니다 경로를 다시 설정해 주세요")

    def _update_currentfile(self):
        self.set("enTargetFile", self.filelist[self.curr_file - 1])
        self.set("lbCurrentFileSeq", str(self.curr_file) + '/' + str(len(self.filelist)))
        self._update_img("cvWaferImageRaw")
        self._update_img("cvWaferImagePatch")

    def _update_img(self, canvas_name):
        canvas = self.find(canvas_name)
        img = Image.open(path.join(self.get("enTargetFolder"), self.get("enTargetFile")))
        if(canvas_name == "cvWaferImagePatch"):
            self.img_save = img
        canvas.background = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, image=canvas.background, anchor='nw') 

    # Events
    def btnBrowse_Click(self):
        targetFolder = filedialog.askdirectory(initialdir=self.get("enTargetFolder"),
                                               title="Please select location of raw wafer images")
        if(targetFolder != ""):
            self.set("enTargetFolder", targetFolder)
            self._make_filelist()

    def cbChoMethod_Click(self):
        return
    def cbRemoveEdge_Click(self):
        return
    def cbJoinCount_Click(self):
        return
    def cbFrangi_Click(self):
        return
    def cbHessian_Click(self):
        return
    def cbCRF_Click(self):
        return
    def cbMRF_Click(self):
        return
    def cbROF_Click(self):
        return

    def rbCurvedLine_Click(self):
        return
    def rbStraightLine_Click(self):
        return
    def rbDefocus_Click(self):
        return
    def rbBullsEye_Click(self):
        return
    def rbDounut_Click(self):
        return
    def rbRandomNoise_Click(self):
        return
    def rbOthers_Click(self):
        return

    def btnPrev_Click(self):
        if(self.curr_file > 1):
            self.curr_file -= 1
            self._update_currentfile()
        else:
            ui.messagebox.showinfo("파일 읽기", "첫 번째 파일입니다")
    def btnNext_Click(self):
        if(self.curr_file < len(self.filelist)):
            self.curr_file += 1
            self._update_currentfile()
        else:
            ui.messagebox.showinfo("파일 읽기", "마지막 파일입니다")
    def btnSave_Click(self):
        if((int(self.get("enPatchWidth")) < 10) or (int(self.get("enPatchHeight")) < 10)):
            ui.messagebox.showerror("크기 오류", "패치의 크기가 너무 작습니다")
        else:
            pattern = self.variables["Class"].get()
            if(not path.isdir(SAVE_DIR)):
                mkdir(SAVE_DIR)
            save_path = path.join(SAVE_DIR, pattern)
            if(not path.isdir(save_path)):
                mkdir(save_path)
            count = 1
            # 가장 마지막 파일 찾기
            for img_file in listdir(save_path):
                num = int(img_file[0:-4])
                if(num >= count):
                    count = num + 1
            self.img_save.crop((int(self.get("enPatchPositionX")),
                                int(self.get("enPatchPositionY")),
                                int(self.get("enPatchPositionX")) + int(self.get("enPatchWidth")),
                                int(self.get("enPatchPositionY")) + int(self.get("enPatchHeight"))))\
                         .save(path.join(save_path, (str(count).zfill(8) + '.jpg')))
            print("패치를 저장했습니다")
    def btnSaveProc_Click(self):
        with open(CONFIG_FILE, 'w') as f:
            f.write("dir = " + self.get("enTargetFolder") + "\n")
            f.write("curr_file = " + self.get("enTargetFile").split('/')[0] + "\n")
    def btnClose_Click(self):
        self.flag_terminate = True
        return


if __name__ == '__main__':
    # Load UI Layout
    app = Launcher('layout.xml')
    app.run()