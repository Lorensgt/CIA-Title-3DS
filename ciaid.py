import os, math,sys,re,datetime,time
from os import listdir
from os.path import isfile, join
from struct import unpack
import zlib
import xml.etree.ElementTree as ET

def crc(fileName):
    prev = 0
    for eachLine in open(fileName,"rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

def cia_tile(path):
    if not os.path.isfile(path):
        sys.exit(0)

    cia_file = open(path, 'r+b')
    cia_header = cia_file.read(0x20)

    # Find offset for tmd
    cert_offset = 0x2040
    cert_size = unpack('<I', cia_header[0x08:0x0C])[0]
    tik_size = unpack('<I', cia_header[0x0C:0x10])[0]
    tmd_size = unpack('<I', cia_header[0x10:0x14])[0]
    tmd_offset = cert_offset + cert_size + 0x30 + tik_size

    # Read titleid from tmd
    cia_file.seek(tmd_offset + 0x18C)
    result =  format(unpack('>Q', cia_file.read(0x8))[0], '016x').upper()
    cia_file.close()
    return result

def find_data(id_title):
    tree = ET.parse('3dsreleases.xml')
    root = tree.getroot()
    # Get all ID of 3DS Games
    for title in root.findall('release'):
        name = title.find('name').text
        titleidxml = title.find('titleid').text
        region =  title.find('region').text
        publisher =  title.find('publisher').text
        language =  title.find('languages').text
        crc_xml = title.find('imgcrc').text

        if titleidxml == id_title:
            return id_title , name, region, language, publisher, crc_xml

    return "Desconegut","Desconegut","Desconegut","Desconegut","Desconegut","Desconegut"

def getFile(extension,path_):
    try:
        if path_:
            path=path_
        else:
            path = os.getcwd()
    except:
        path = os.getcwd()

    extension_len=len(extension)
    files_list = []

    if RECURSIVE == True:
        for root, directories, filenames in os.walk(path):
            for filename in filenames:
                if filename[-extension_len:] == extension:
                    files_list.append({"root":root,"filename":filename})

        return len(files_list),files_list

    else:
        for f in listdir(path):
            if isfile(join(path, f)):
                if f[-extension_len:] == extension:
                    files_list.append({"root":path,"filename":f})

        return len(files_list),files_list

INPUT_PATH = ""
RECURSIVE = True
if os.path.exists(os.path.dirname(sys.argv[1])):
    INPUT_PATH = sys.argv[1]+"\\"

sizefiles,files = getFile('cia',INPUT_PATH)

for index,rom in enumerate(files):
    ID = cia_tile(os.path.join(rom["root"],rom["filename"]))
    id_title , name, region, language, publisher, crc_xml = find_data(ID)
    print('Filename:',rom['filename'])
    print(id_title , name, region, language, publisher, crc_xml,"\n")
