#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PIL  import Image  #安装pillow
import os
import sys
from shutil import copyfile
import  re
from io import BytesIO
import getopt

# https://tinypng.com/              在线压缩，但压缩后会变模糊，不考虑。很明显有区别，不明白网上用得最多就是它
# https://www.secaibi.com/tools/    在线压缩，但压缩后颜色有偏差，不考虑
# https://www.cnblogs.com/pms01/p/6895765.html  jpg、jpeg、png... 的区别


# 未压缩文件和压缩文件存放位置
InputTarget = ''
OutputTarget = ''

# 图片压缩大小上限值   单位B
threshold = 300 * 1024

#RGBA 处理模式    RGB(丢弃Alpha)  PNG(保存为PNG文件)
RGBA_TYPE = "RGB"

# 压缩图片  查找所有图片文件
def compress_img():
    for root, subdirs, files in os.walk(InputTarget):
        for filename in files:
            #\.GIF$|\.gif|  这种格式不处理
            if re.search('\.BMP$|\.bmp$|\.JPG$|\.jpg$|\.JPEG$|\.jpeg$|\.PNG$|\.png$', str(filename)):
                # 如果输出压缩文件的文件夹不存在则创建
                ole_file = os.path.join(root, filename)
                new_path = root.replace(InputTarget, OutputTarget)
                if not os.path.exists(new_path):
                    os.makedirs(new_path)
                new_file =  os.path.join(new_path, filename)
                compress_file(ole_file,new_file)

# 压缩单张图片
def compress_file(file_name,newfile_name):
    file_size = os.path.getsize(file_name)
    if file_size ==0:
        print(file_name + " |异常文件大小为0")
        return

    try:
        img = Image.open(file_name)
    except:
        print(file_name + " |文件读取异常")
        return



    b_cslq =  True  #需要转换
    if file_size < threshold:
        if file_name != newfile_name:
            copyfile(file_name, newfile_name)  #直接复制过去
            print(file_name + " |直接复制")
        else:
            print(file_name + " |没有超过大小，不处理")
        b_cslq = False



    #无损转换  PNG
    if b_cslq:
        tmpfile_png = BytesIO()
        img.save(tmpfile_png, "PNG")
        pngsize = sys.getsizeof(tmpfile_png)  # os.path.getsize(tmpfile_png)
        if pngsize  < threshold:
            print(file_name + " |无损转换PNG")
            b_cslq = False
            img.save(newfile_name, "PNG")

    #有损转换   先按比例改尺寸，再把尺寸改回来
    i_lqdwx  = 100  #转换百分比

    lrst =  "JPEG" #转换格式
    #RGBA意思是红色，绿色，蓝色，Alpha的色彩空间，Alpha指透明度。而JPG不支持透明度，
    if img.mode == "RGBA":
        #二选一
        if RGBA_TYPE == "RGB":
            img=img.convert('RGB')  #丢弃Alpha
        else:
            lrst = "PNG"   #保存为.png文件


    if b_cslq and lrst ==  "JPEG":
        tmpfile_png = BytesIO()  # 创建名称唯一的临时文件供使用
        img.save(tmpfile_png, "JPEG")
        jpegsize = sys.getsizeof(tmpfile_png)
        if jpegsize  < threshold:
            print(file_name + " |直接转换为JPEG")
            b_cslq = False
            img.save(newfile_name, "JPEG")


    #二分查找  递归算法
    if b_cslq and lrst ==  "PNG":
        wvd = PNG_search(100,1,lrst,img  )
        compressed_img, nesize = get_new_img(img, lrst, wvd)
        compressed_img.save(newfile_name, lrst)
        b_cslq = False
        print(file_name + " |二分查找递归"+lrst+str(wvd))

    if b_cslq and lrst ==  "JPEG":
        wvd = JPEG_search(100,1,lrst,img  )
        img.save(newfile_name, lrst , quality=wvd)
        b_cslq = False
        print(file_name + " |二分查找递归"+lrst+str(wvd))


def PNG_search( left, right, lrst,img):
    if left - right == 1 or left - right == 0  : #递归结束条件
        return right
    i_lqdwx = (left + right) // 2
    # print("二分百分" + str(left) + "  " + str(right) + "  " + str(i_lqdwx))
    compressed_img,nesize =  get_new_img( img,lrst,i_lqdwx)
    if nesize < threshold:
        return PNG_search(left, i_lqdwx, lrst,img)
    else:
        return PNG_search(i_lqdwx, right, lrst, img)


def JPEG_search( left, right, lrst,img):
    if left - right == 1 or left - right == 0  : #递归结束条件
        return right
    i_lqdwx = (left + right) // 2
    tmpfile_jpeg = BytesIO()
    img.save(tmpfile_jpeg, lrst ,  quality= i_lqdwx )
    nesize = sys.getsizeof(tmpfile_jpeg)
    # print("二分百分" + str(left) + "  " + str(right) + "  " + str(i_lqdwx) + "    " +str(nesize))
    if nesize < threshold:
        return JPEG_search(left, i_lqdwx, lrst,img)
    else:
        return JPEG_search(i_lqdwx, right, lrst, img)


def get_new_img(  img,lrst,i_lqdwx):
    # 获取原始图片的宽、高
    width, height = img.size
    tmpfile_jpeg2 = BytesIO()
    compressed_img = img.resize((int(width * i_lqdwx / 100), int(height * i_lqdwx / 100)))
    compressed_img = compressed_img.resize((width, height))
    compressed_img.save(tmpfile_jpeg2, lrst)
    nesize=  sys.getsizeof(tmpfile_jpeg2)
    return  compressed_img,nesize

def usage():
    print('''
    -h or --help帮助信息
    -i or --input"输入目标"
    -o or --output"输出目标"
    -s or --size"设置最大文件大小"
    -r or --rgba"RGBA处理模式  RGB(丢弃Alpha)  PNG(保存为PNG文件)"
    
    ''')
    return 0

if __name__ == '__main__':

    if ( len( sys.argv ) == 1 ):
        usage()
        print('错误:len=1  使用默认值')
        InputTarget = "C:/111"
        OutputTarget = "C:/222"
    else:
        opts, args = getopt.getopt( sys.argv[1:], 'i:o:hs:r:', [  'input=','output=', 'help', 'size=',  'rgba='   ] )
        if args:
            usage()
            print('错误:args='+str(args))
            print(opts, args)
            sys.exit(1)
        for opt,val in opts:
            if opt in ('-h', '--help'):
                usage()
                sys.exit(1)
            if  opt in ('-i', '--input'):
                InputTarget = val
            if opt in ('-o', '--output'):
                OutputTarget = val
            if opt in ('-s', '--size'):
                threshold  = val
            if opt in ('-r', '--rgba'):
                RGBA_TYPE = val

    print('input:' + InputTarget)
    print('output:' + str(OutputTarget) )
    print('size:' + str(threshold) )
    print('rgba:' + RGBA_TYPE )

    if os.path.isdir(InputTarget) and os.path.isdir(OutputTarget):
        print("文件夹处理模式")
        compress_img()
    elif os.path.isfile(InputTarget) and (not os.path.isdir(OutputTarget) ) :
        # if  os.path.isfile(OutputTarget):
        #     print("文件替换处理模式")
        # elif not os.path.exists(OutputTarget):
        #     print("文件新增处理模式")
        print("文件处理模式")
        compress_file(InputTarget,OutputTarget)
    else:
        print("无法处理")
        sys.exit(1)

