#!/usr/bin/env python

import math, os, sys, tempfile
from PIL import Image

SJPG_FILE_FORMAT_VERSION = "V1.00"
JPEG_SPLIT_HEIGHT = 16

max_sjpg_width = 240
max_sjpg_height = 100


def convert_sjpg(jpgfile, sjpgfile):
    try:
        im = Image.open(jpgfile)
    except:
        print("File " + jpgfile + " is not a valid jpeg file")
        return
    width, height = im.size
    print("Input:")
    print("\t" + jpgfile)
    print("\tResolution = " + str(width) + " x " + str(height))
    # resize image when necessary
    if width > max_sjpg_width or height > max_sjpg_height:
        im.thumbnail([max_sjpg_width, max_sjpg_height], resample=Image.LANCZOS)
        width, height = im.size
        print("\tResize = " + str(width) + " x " + str(height))
    # split jpg into blocks
    tempdir = tempfile.gettempdir()
    lenbuf = []
    block_size = JPEG_SPLIT_HEIGHT;
    spilts = math.ceil(height/block_size)
    sjpeg_data = bytearray()
    sjpeg = bytearray()
    row_remaining = height;
    for i in range(spilts):
        if row_remaining < block_size:
            crop = im.crop((0, i*block_size, width, row_remaining + i*block_size))
        else:
            crop = im.crop((0, i*block_size, width, block_size + i*block_size))
        row_remaining = row_remaining - block_size;
        crop.save(os.path.join(tempdir, str(i)+".jpg"), subsampling=0, quality=95)
    # read back blocks
    for i in range(spilts):
        f = open(os.path.join(tempdir, str(i)+".jpg"), "rb")
        a = f.read()
        f.close()
        sjpeg_data = sjpeg_data + a
        lenbuf.append(len(a))
    # file header
    header = bytearray()
    #4 BYTES
    header = header + bytearray("_SJPG__".encode("UTF-8"));
    #6 BYTES VERSION
    header = header + bytearray(("\x00" + SJPG_FILE_FORMAT_VERSION + "\x00").encode("UTF-8"));
    #WIDTH 2 BYTES
    header = header + width.to_bytes(2, byteorder='little');
    #HEIGHT 2 BYTES
    header = header + height.to_bytes(2, byteorder='little');
    #NUMBER OF ITEMS 2 BYTES
    header = header + spilts.to_bytes(2, byteorder='little');
    #NUMBER OF ITEMS 2 BYTES
    header = header + int(JPEG_SPLIT_HEIGHT).to_bytes(2, byteorder='little');
    for item_len in lenbuf:
        # WIDTH 2 BYTES
        header = header + item_len.to_bytes(2, byteorder='little');
    sjpeg = header + sjpeg_data
    if 1:
        for i in range(len(lenbuf)):
            os.remove(os.path.join(tempdir, str(i)+".jpg"))
    f = open(sjpgfile,"wb")
    f.write(sjpeg)
    f.close()
    print("Output:")
    print("\t" + sjpgfile)
    print("\tSize = " + str(round(len(sjpeg)/1024, 1)) + " KB\n" )
    

def process_folder(abs_dir, base_name):
    for afile in os.listdir(abs_dir):
        if afile.lower().endswith(".jpg"):
            name = os.path.splitext(afile)[0]
            # if we have a file with name "foldername.jpg", convert it to "foldername.sjpg" and "VGMPlayer.sjpg"
            if name.lower() == base_name.lower():
                convert_sjpg(os.path.join(dir, afile), os.path.join(dir, "VGMPlayer.sjpg"))
                convert_sjpg(os.path.join(dir, afile), os.path.join(dir, name + ".sjpg"))
            else:
                convert_sjpg(os.path.join(dir, afile), os.path.join(dir, name + ".sjpg"))


if __name__ == '__main__':
    if len(sys.argv) != 1:
        root_dir = sys.argv[1]
    else:
        print("usage:\n\t python " + sys.argv[0] + " [root of VGM folders]")
        sys.exit(0)
    # iterate dirs
    for adir in os.listdir(root_dir):
        dir = os.path.join(root_dir, adir)
        if (os.path.isdir(dir)):
            process_folder(dir, adir) # absolute_dir, folder_name
    