#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

# Author: funchan
# CreateDate: 2021-07-15 13:18:02
# Description: 为图片、PDF文件添加文字水印和防伪底纹

import os
import tempfile
import traceback
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

from dirs import *
from log import Logger


def add_watermask(file, mark_text, density=None, transparency=30):
    if isinstance(file, Image.Image):
        image = file

    if isinstance(file, (str, Path)):
        image = Image.open(file)

    image_width, image_height = image.size

    # 水印数量
    if density:
        scale = density
    else:
        watermark_width, watermark_height = 500, 500

        scale_width, scale_height = image_width / watermark_width, image_height / watermark_height
        scale = max(scale_width, scale_height)

    if scale < 1:
        watermark_size = ((int(scale * watermark_width),
                           int(scale * watermark_height)))
        scale = 1
    else:
        scale = int(scale)
        if scale_width > scale_height:
            watermark_size = (image_width // scale, image_width // scale)
        else:
            watermark_size = (image_height // scale, image_height // scale)

    watermark_width, watermark_height = watermark_size
    watermark = Image.new('RGBA', watermark_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)

    font_size = int(watermark_width * 72 / 96 / len(mark_text))
    watermark_font = ImageFont.truetype('simsun', font_size)
    text_position = ((watermark_width - font_size * len(mark_text)) // 2,
                     (watermark_height - font_size) // 2)
    draw.text(text_position,
              mark_text,
              fill=(0, 0, 0, transparency),
              font=watermark_font)

    watermark = watermark.rotate(45)

    r, g, b, a = watermark.split()
    for i in range(scale):
        for j in range(scale):
            watermark_position = (watermark_width * i, watermark_height * j)
            image.paste(watermark, watermark_position, a)

    return image


def add_shade(file, transparency=30):
    if isinstance(file, Image.Image):
        image = file

    if isinstance(file, (str, Path)):
        image = Image.open(file)

    image_width, image_height = image.size

    shade_path = res_dir / 'shade.png'
    shade = Image.open(shade_path)
    shade_width, shade_height = shade.size

    scale_width, scale_height = image_width / shade_width, image_height / shade_height
    scale = min(scale_width, scale_height)
    shade = shade.resize(
        (int(image_height * scale), int(image_height * scale)))

    shade = shade.convert('RGBA')
    shade_width, shade_height = shade.size
    for i in range(shade_width):
        for j in range(shade_height):
            color = shade.getpixel((i, j))
            if sum(color[:-1]) != 0:
                color = color[:-1] + (transparency, )
                shade.putpixel((i, j), color)

    r, g, b, a = shade.split()
    image.paste(shade, (0, 0), a)

    return image


def pdf_to_image(pdf_path, image_dir, zoom_x=1, zoom_y=1, rotation_angle=0):
    # 打开PDF文件
    pdf = fitz.open(pdf_path)
    page_count = pdf.pageCount
    # 逐页读取PDF
    for pg in range(page_count):
        page = pdf[pg]
        # 设置缩放和旋转系数
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotation_angle)
        pm = page.getPixmap(matrix=trans, alpha=False)
        # 开始写图像
        old_name = pdf_path.stem
        image_dir.mkdir(parents=True, exist_ok=True)
        new_file = str(
            image_dir /
            (old_name + str(pg).zfill(len(str(page_count))) + '.png'))
        pm.writePNG(new_file)
    pdf.close()


def image_to_pdf(image_dir, pdf_path):
    image_list = []
    for image in image_dir.iterdir():
        image_open = Image.open(image)
        if image_open.mode != 'RGB':
            image_open = image_open.convert('RGB')
        image_list.append(image_open)

    image_one = image_list[0]
    image_others = image_list[1:]
    image_one.save(pdf_path,
                   "PDF",
                   resolution=100,
                   save_all=True,
                   append_images=image_others)


def main():
    print(f'请将需添加水印的图片或PDF文件复制到【{input_dir}】')
    os.system('echo 文件放置好后，按任意键继续&&pause >nul')

    mark_text = input('请输入水印文字 [默认为空]：') or ' '

    while True:
        need_shade = input('是否添加底纹 [Y/N]：')
        if need_shade.lower() in ('y', 'yes', '是'):
            need_shade = True
            break
        if need_shade.lower() in ('n', 'no', '否'):
            need_shade = False
            break

    logger = Logger(log_dir)
    suffix_filter = ('.bmp', '.jpg', '.jpeg', '.gif', '.png', '.pdf')

    for file in input_dir.rglob('*.*'):
        if file.suffix.lower(
        ) in suffix_filter and file.stat().st_size < 1024 * 1024 * 50:
            relative_path = file.relative_to(file.parent)
            new_file_path = output_dir / relative_path

            try:
                if file.suffix in '.pdf':
                    tmp_dir = Path(tempfile.mkdtemp())
                    # os.system(f'EXPLORER {tmp_dir}')
                    pdf_to_image(file, tmp_dir, zoom_x=4, zoom_y=4)
                    for image in tmp_dir.iterdir():
                        new_image = add_watermask(image, mark_text)

                        if need_shade:
                            new_image = add_shade(new_image)

                        new_image.save(image)

                    image_to_pdf(tmp_dir, new_file_path)
                else:
                    new_image = add_watermask(file, mark_text)

                    if need_shade:
                        new_image = add_shade(new_image)

                    new_image.save(new_file_path)

                logger.info(f'【{file}】处理成功')

            except:
                traceback.print_exc()

    os.system(f'EXPLORER {output_dir}')


if __name__ == '__main__':
    main()
