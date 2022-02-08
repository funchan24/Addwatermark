#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

# Author: funchan
# CreateDate: 2021-07-15 13:20:02
# Description: 为图片、PDF文件添加文字水印

import tempfile
import time
from datetime import datetime
from math import ceil, sqrt
from pathlib import Path
from tkinter import *
from tkinter.filedialog import askdirectory, askopenfilenames
from typing import Tuple, Union

import fitz
import qrcode
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont, ImageTk
from ttkbootstrap import *
from ttkbootstrap.constants import *

from dirs import *
from gui import GUI

now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def reverse_color(
        image: Union[Path, str, Image.Image]) -> Tuple[int, int, int]:
    assert isinstance(image, (Path, str, Image.Image))
    if isinstance(image, (Path, str)):
        image = Image.open(image)

    image = image.resize((100, 100))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    r_total = g_total = b_total = 0
    for x in range(100):
        for y in range(100):
            r, g, b = image.getpixel((x, y))
            r_total += r
            g_total += g
            b_total += b
    r_average = r_total // 10000
    g_average = g_total // 10000
    b_average = b_total // 10000
    r_reverse = 255 - r_average
    g_reverse = 255 - g_average
    b_reverse = 255 - b_average

    return r_reverse, g_reverse, b_reverse


def add_text(image_file: Union[Path, str, Image.Image],
             text: str,
             font_family: str = 'simhei',
             angle: int = 45,
             opacity: int = 30) -> Image.Image:
    assert isinstance(image_file, (Path, str, Image.Image))
    assert len(text) <= 20, '水印文字不能超过20个字'

    if opacity < 0:
        opacity = 0
    if opacity > 100:
        opacity = 100

    if isinstance(image_file, (Path, str)):
        image_layer = Image.open(image_file)
    else:
        image_layer = image_file

    if image_layer.mode != 'RGBA':
        image_layer = image_layer.convert('RGBA')

    text_layer = Image.new(
        'RGBA', (int(sqrt(image_layer.size[0]**2 + image_layer.size[1]**2)),
                 int(sqrt(image_layer.size[0]**2 + image_layer.size[1]**2))),
        (255, 255, 255, 0))
    text_canvas = ImageDraw.Draw(text_layer)

    if len(text) <= 8:
        text_row = 1
        text_list = [text]
    else:
        text_row = 2
        edge_num = ceil(len(text) / 2)
        text_list = [text[:edge_num], text[edge_num:]]

    font_size = 9
    while True:
        font = ImageFont.truetype(font_family, font_size, encoding='utf-8')
        text_w, text_h = text_canvas.textsize(text_list[0], font=font)
        min_nums = min(text_layer.size[0] // text_w,
                       text_layer.size[1] // text_h)
        max_nums = max(text_layer.size[0] // text_w,
                       text_layer.size[1] // text_h)

        if min_nums >= 10:
            font_size += 1
        else:
            break

    r, g, b = reverse_color(image_layer)
    fill = (r, g, b, opacity)

    for x in range(max_nums):
        for y in range(max_nums):
            for row in range(text_row):
                text_pos = (int(1.5 * x * text_w),
                            int((1.5 * min(3, len(text_list[0])) * y + row) *
                                text_h))
                text_canvas.text(text_pos,
                                 text_list[row],
                                 font=font,
                                 fill=fill)

    text_layer = text_layer.rotate(angle)
    crop_box = ((text_layer.size[0] - image_layer.size[0]) // 2,
                (text_layer.size[1] - image_layer.size[1]) // 2,
                (text_layer.size[0] + image_layer.size[0]) // 2,
                (text_layer.size[1] + image_layer.size[1]) // 2)
    text_layer = text_layer.crop(crop_box)

    new_image = Image.alpha_composite(image_layer, text_layer)
    new_image = new_image.convert('RGB')
    return new_image


def add_pic(image_file: Union[Path, str, Image.Image],
            wm_file: Union[None, Path, str, Image.Image] = None,
            angle: int = 0,
            opacity: int = 30) -> Image.Image:
    assert isinstance(image_file, (Path, str, Image.Image))
    assert (isinstance(wm_file,
                       (Path, str, Image.Image, qrcode.image.pil.PilImage))
            or wm_file is None)

    if opacity < 0:
        opacity = 0
    if opacity > 100:
        opacity = 100

    if isinstance(image_file, (Path, str)):
        image_layer = Image.open(image_file)
    else:
        image_layer = image_file

    if image_layer.mode != 'RGBA':
        image_layer = image_layer.convert('RGBA')

    if wm_file is None:
        wm_layer = Image.new('RGBA', (200, 200), (255, 255, 255, opacity))
    else:
        if isinstance(wm_file, (Path, str)):
            wm_layer = Image.oepn(wm_file)
        else:
            wm_layer = wm_file

        wm_layer = wm_layer.resize((200, 200))
        if wm_layer.mode != 'RGBA':
            wm_layer = wm_layer.convert('RGBA')

        for i in range(200):
            for j in range(200):
                color = wm_layer.getpixel((i, j))
                color = color[:-1] + (opacity, )
                wm_layer.putpixel((i, j), color)

    layer = Image.new(
        'RGBA', (int(sqrt(image_layer.size[0]**2 + image_layer.size[1]**2)),
                 int(sqrt(image_layer.size[0]**2 + image_layer.size[1]**2))),
        (255, 255, 255, 0))
    if min(layer.size) < 50:
        wm_layer.resize((min(layer.size), min(layer.size)))

    num_x, num_y = layer.size[0] // wm_layer.size[0], layer.size[
        1] // wm_layer.size[1]

    for i in range(num_x):
        for j in range(num_y):
            layer.paste(wm_layer, (int(
                1.5 * i * wm_layer.size[0]), int(1.5 * j * wm_layer.size[1])))

    layer = layer.rotate(angle)
    crop_box = ((layer.size[0] - image_layer.size[0]) // 2,
                (layer.size[1] - image_layer.size[1]) // 2,
                (layer.size[0] + image_layer.size[0]) // 2,
                (layer.size[1] + image_layer.size[1]) // 2)
    layer = layer.crop(crop_box)
    new_image = Image.composite(layer, image_layer, layer)
    new_image = new_image.convert('RGB')
    return new_image


def pdf_to_image(pdf_path: Path,
                 image_dir: Path,
                 zoom_x: int = 2,
                 zoom_y: int = 2,
                 rotation_angle: int = 0) -> None:
    pdf = fitz.open(pdf_path)
    page_count = pdf.pageCount
    for pg in range(page_count):
        page = pdf[pg]
        # 设置缩放和旋转系数，zoom_x和zoom_y一般设置为相同的值，值越大图片越清晰
        trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotation_angle)
        pm = page.get_pixmap(matrix=trans, alpha=False)
        old_name = pdf_path.stem
        image_dir.mkdir(parents=True, exist_ok=True)
        new_file = str(
            image_dir /
            (old_name + str(pg).zfill(len(str(page_count))) + '.png'))
        pm.save(new_file)
    pdf.close()


def image_to_pdf(image_dir: Path, pdf_path: Path) -> None:
    image_list = image_dir.iterdir()

    pdf = FPDF()
    pdf.set_auto_page_break(0)
    pdf.set_margin(0)
    for image in image_list:
        _image = Image.open(image)
        w_image, h_image = _image.size
        if w_image > h_image:
            pdf.add_page('landscape')
        else:
            pdf.add_page()
        pdf.image(str(image), w=pdf.epw, h=pdf.eph)

    pdf.output(pdf_path)


class App(GUI):

    def __init__(self,
                 title="ttkbootstrap",
                 version=1.0,
                 base_size=8,
                 icon_path=None,
                 themename="litera",
                 iconphoto='',
                 size=None,
                 position=None,
                 minsize=None,
                 maxsize=None,
                 resizable=None,
                 hdpi=True,
                 scaling=None,
                 transient=None,
                 overrideredirect=False,
                 alpha=0.95):
        super().__init__(title, base_size, icon_path, themename, iconphoto,
                         size, position, minsize, maxsize, resizable, hdpi,
                         scaling, transient, overrideredirect, alpha)

        self.version = version
        self.dict_font_family = {
            '宋体': 'simsun',
            '楷体': 'simkai',
            '仿宋': 'simfang',
            '黑体': 'simhei'
        }
        self.start_flag = 0
        self.src_files = None

        self.after(100, self.update_status)
        self.get_view()

    def add_widget(self):
        menu = Menu(self)
        menu.add_command(label='关于', command=self.get_about)
        self.config(menu=menu)

        frame_1 = Labelframe(self, text='选择文件', labelanchor=N)
        self.frame_1_widgets = [[
            Text(frame_1, width=5 * self.base_size, height=3), '-'
        ],
                                [
                                    Button(frame_1,
                                           text='清除文件',
                                           command=self.clear_src),
                                    Button(frame_1,
                                           text='选择文件',
                                           command=self.choose_src)
                                ]]
        self.grid_widget(self.frame_1_widgets,
                         frame_1,
                         self.base_size,
                         sticky=None)

        self.scroll = Scrollbar(frame_1)
        self.scroll.grid(row=0, column=1, sticky=E)
        self.scroll.config(command=self.frame_1_widgets[0][0].yview)
        self.frame_1_widgets[0][0].config(yscrollcommand=self.scroll.set)

        frame_2 = Labelframe(self, text='水印选项', labelanchor=N)
        self.var_wm_text = StringVar()
        self.var_font_family = StringVar()
        self.var_qrcode = BooleanVar()
        self.frame_2_widgets = [[
            Label(frame_2, text='水印文字'),
            Combobox(frame_2,
                     values=['机密文件', '内部资料', now_str],
                     textvariable=self.var_wm_text)
        ],
                                [
                                    Label(frame_2, text='水印字体'),
                                    Combobox(frame_2,
                                             state='readonly',
                                             values=['宋体', '楷体', '仿宋', '黑体'],
                                             textvariable=self.var_font_family)
                                ],
                                [
                                    Label(frame_2,
                                          text='不透明度\n30%',
                                          justify=CENTER),
                                    Scale(frame_2, from_=0, to=100)
                                ],
                                [
                                    Label(frame_2,
                                          text='旋转角度\n45°',
                                          justify=CENTER),
                                    Scale(frame_2, from_=0, to=90)
                                ],
                                [
                                    Checkbutton(frame_2,
                                                text='文字水印转为二维码水印',
                                                variable=self.var_qrcode), '-'
                                ]]

        self.var_font_family.set('黑体')
        self.frame_2_widgets[2][1].set(30)
        self.frame_2_widgets[3][1].set(45)
        self.var_qrcode.set(False)
        self.grid_widget(self.frame_2_widgets, frame_2,
                         (self.base_size, self.base_size // 2, self.base_size,
                          self.base_size))

        self.var_progress = IntVar()
        self.var_progress.set(0)
        frame_3 = Frame(self)
        frame_4 = Frame(frame_3)
        self.frame_4_widgets = [[
            Progressbar(frame_4,
                        maximum=100,
                        variable=self.var_progress,
                        length=440), '-'
        ], [Canvas(frame_4, width=440, height=580), '-']]
        self.grid_widget(self.frame_4_widgets, frame_4, 0)

        self.frame_3_widgets = [[frame_4, '-'],
                                [
                                    Button(frame_3,
                                           text='预览效果',
                                           command=self.get_view),
                                    Button(frame_3,
                                           text='添加水印',
                                           command=self.start_work)
                                ]]
        self.grid_widget(self.frame_3_widgets,
                         frame_3, (0, self.base_size, 0, self.base_size),
                         sticky=None)

        self.grid_widget([[frame_1], [frame_2]], self,
                         (self.base_size, self.base_size, 0, 0))
        frame_3.grid(row=0,
                     column=1,
                     rowspan=2,
                     padx=self.base_size,
                     pady=self.base_size,
                     sticky=NSEW)

    @GUI.multi_thread
    def start_work(self):
        self.start_flag = 1
        self.disable_widgets()
        output = askdirectory(title='文件保存到')
        output = Path(output)

        text = self.var_wm_text.get()
        font_family = self.dict_font_family.get(self.var_font_family.get())
        opacity = int(self.frame_2_widgets[2][1].get())
        angle = int(self.frame_2_widgets[3][1].get())
        use_qrcode = self.var_qrcode.get()

        if use_qrcode:
            wm_file = qrcode.make(text)
        else:
            text = text[:20]

        i = 0
        for file in self.src_files:
            file = Path(file)
            if file.suffix == '.pdf':
                tmp_dir = Path(tempfile.mkdtemp())
                pdf_to_image(file, tmp_dir, zoom_x=3, zoom_y=3)

                j = 0
                for image in tmp_dir.iterdir():
                    if use_qrcode:
                        new_image = add_pic(image, wm_file, angle, opacity)
                    else:
                        new_image = add_text(image, text, font_family, angle,
                                             opacity)
                    new_image.save(image)
                    j += 1
                    self.var_progress.set(
                        int((i + (j / len(list(tmp_dir.iterdir())))) /
                            len(self.src_files) * 100))

                image_to_pdf(tmp_dir, output / f'[水印] {file.name}')

            else:
                if use_qrcode:
                    new_image = add_pic(file, wm_file, angle, opacity)
                else:
                    new_image = add_text(file, text, font_family, angle,
                                         opacity)

                new_image.save(output / f'[水印] {file.name}')
                self.var_progress.set(int((i + 1) / len(self.src_files) * 100))
            i += 1

        time.sleep(2)
        self.var_progress.set(0)
        self.enable_widgets()
        self.start_flag = 0

    def clear_src(self):
        self.src_files = None
        self.frame_1_widgets[0][0].delete(1.0, END)

    def choose_src(self):
        if self.src_files is None:
            self.src_files = []
        filenames = askopenfilenames(filetypes=[('all files',
                                                 ('*.pdf', '*.bmp', '*.gif',
                                                  '*.jpg', '*.png'))])
        for filename in filenames:
            if filename not in self.src_files:
                self.src_files.append(filename)

        filenames = [f'* {i[:14]}...{i[-14:]}' for i in self.src_files]
        filenames = '\n'.join(filenames)

        self.frame_1_widgets[0][0].delete(1.0, END)
        self.frame_1_widgets[0][0].insert(INSERT, filenames)

    def update_status(self):
        text = self.var_wm_text.get()[:20]
        opacity = int(self.frame_2_widgets[2][1].get())
        angle = int(self.frame_2_widgets[3][1].get())

        self.frame_2_widgets[2][0].config(text=f'不透明度\n{opacity}%')
        self.frame_2_widgets[3][0].config(text=f'旋转角度\n{angle}°')

        if not self.start_flag:
            if text and self.src_files:
                self.frame_3_widgets[1][1].config(state=NORMAL)
            else:
                self.frame_3_widgets[1][1].config(state=DISABLED)

        self.after(100, self.update_status)

    def get_view(self):
        font_family = self.dict_font_family.get(self.var_font_family.get())
        opacity = int(self.frame_2_widgets[2][1].get())
        angle = int(self.frame_2_widgets[3][1].get())
        use_qrcode = self.var_qrcode.get()

        if use_qrcode:
            text = self.var_wm_text.get()
            text = text or '示例文字'
            wm_file = qrcode.make(text)
            image = Image.new('RGBA', (440, 580), (248, 249, 250, 100))
            new_image = add_pic(image, wm_file, angle, opacity)
            x = self.frame_4_widgets[1][0].winfo_width() // 2
            y = self.frame_4_widgets[1][0].winfo_height() // 2
            global new_photo
            new_photo = ImageTk.PhotoImage(new_image)
            self.frame_4_widgets[1][0].create_image(x, y, image=new_photo)
        else:
            text = self.var_wm_text.get()[:20]
            text = text or '示例文字'
            image = Image.new('RGBA', (440, 580), (248, 249, 250, 100))
            new_image = add_text(image, text, font_family, angle, opacity)
            x = self.frame_4_widgets[1][0].winfo_width() // 2
            y = self.frame_4_widgets[1][0].winfo_height() // 2
            new_photo = ImageTk.PhotoImage(new_image)
            self.frame_4_widgets[1][0].create_image(x, y, image=new_photo)

    def get_about(self):
        self.toplevel_about = Toplevel(self, resizable=(False, False))
        self.toplevel_about.grab_set()
        text = f'''名称：水印助手
版本：{self.version}
功能：为图片、PDF文件添加文字水印
作者：funchan
邮箱：funchan@msn.cn
感谢：Python、fitz、fpdf2、Nuitka、
Pillow、qrcode、ttkbootstrap'''

        self.toplevel_about.grid_anchor(CENTER)
        Label(self.toplevel_about, text=text,
              bootstyle=PRIMARY).grid(padx=self.base_size,
                                      pady=self.base_size,
                                      ipadx=self.base_size,
                                      ipady=self.base_size)
        self.center_horizontally(self.toplevel_about)

        self.toplevel_about.iconbitmap(self.icon_path)
        self.toplevel_about.wm_attributes('-alpha', 0.95)

    def disable_widgets(self):
        for widgets in (self.frame_1_widgets + self.frame_2_widgets +
                        self.frame_3_widgets):
            for widget in widgets:
                if widget not in ('/', '-'):
                    try:
                        widget.config(state=DISABLED)
                    except Exception:
                        pass

    def enable_widgets(self):
        for widgets in (self.frame_1_widgets + self.frame_2_widgets +
                        self.frame_3_widgets):
            for widget in widgets:
                if widget not in ('/', '-'):
                    try:
                        widget.config(state=NORMAL)
                    except Exception:
                        pass


def main():
    title = '水印助手'
    version = 1.2
    icon_path = str(res_dir / 'main_32.ico')
    resizable = (False, False)
    app = App(title=title,
              version=version,
              base_size=6,
              icon_path=icon_path,
              resizable=resizable)

    app.mainloop()


if __name__ == '__main__':
    main()
