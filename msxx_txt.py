#!/usr/bin/env python3

import sys
import json
# import pprint as pp
import numpy as np
from pathlib import Path
from copy import deepcopy
import argparse

# struct (迫真)
Block = {  # 与从前的判断不一致
    "id": 0,  # Block有2个uint32_t数表示这里所述信息，不是从前判断的3个数
    "charCount": 0,
    "strList": []
}

BlockSet = {
    "blockCount": 0,  # 每组Block前，有一个uint32_t数表示包含的Block数
    "blockList": []  # [Block]
}


def get_file_len(file) -> int:
    """
    获取传入文件的总长
    """
    posBackup = file.tell()
    file.seek(0, 2)
    _len = file.tell()
    file.seek(posBackup, 0)

    return _len


class Converter():
    def __init__(self, inFilePath: Path, mode: str, outFilePath: Path = None):
        self.data = []
        self.mode = mode  # "txt2json" "json2txt"

        # 处理文件路径与文件打开

        (self.inFilePath, self.outFilePath) = (inFilePath, outFilePath)
        self.inFileDir = self.inFilePath.parent
        self.inFileName = self.inFilePath.stem

        (self.txtFile, self.jsonFile) = (None, None)
        (self.inFile, self.outFile) = (None, None)

        (self.txtFilePath, self.jsonFilePath) = (None, None)

        match (self.mode):
            case "txt2json":
                self.txtFilePath = self.inFilePath
                if (self.outFilePath):
                    self.jsonFilePath = self.outFilePath
                else:
                    self.inFileDir / "{0}.json".format(self.inFileName)
                    print("由于未手动指定输出文件路径，自动指定：输出文件路径为{0}".format(
                        self.jsonFilePath))

                self.txtFile = open(self.txtFilePath, "rb")
                self.jsonFile = open(self.jsonFilePath, "wt", encoding="utf-8")

                self.inFile = self.txtFile
                self.outFile = self.jsonFile

            case "json2txt":
                self.jsonFilePath = self.inFilePath
                if (self.outFilePath):
                    self.txtFilePath = self.outFilePath
                else:
                    self.inFileDir / "{0}.TXT".format(self.inFileName)
                    print("由于未手动指定输出文件路径，自动指定：输出文件路径为{0}".format(
                        self.txtFilePath))

                self.jsonFile = open(self.jsonFilePath, "rt", encoding="utf-8")
                self.txtFile = open(self.txtFilePath, "wb")

                self.inFile = self.jsonFile
                self.outFile = self.txtFile

            case _:
                raise Exception("不正确的模式名：“{0:s}”".format(self.mode))

    def clear(self):
        self.inFile.close()
        self.outFile.close()

    #######################
    # txt2json

    def read_txt(self):
        """
        读TXT文件，构建各Block、BlockSet
        """
        txtFileLen = get_file_len(self.txtFile)
        while (self.txtFile.tell() < txtFileLen):
            blockCount = int(np.fromfile(
                self.txtFile, dtype=np.uint32, count=1)[0])

            newBlockSet = deepcopy(BlockSet)
            newBlockSet["blockCount"] = blockCount

            for _ in range(blockCount):
                (_id, charCount) = np.fromfile(
                    self.txtFile, dtype=np.uint32, count=2)
                _id = int(_id)
                charCount = int(charCount)

                newBlock = deepcopy(Block)

                newBlock["id"] = _id
                newBlock["charCount"] = charCount

                line = []
                for _ in range(charCount):
                    charNum = np.fromfile(
                        self.txtFile, dtype=np.ushort, count=1)[0]

                    if (charNum != 0x0000):
                        # 先转换到python3所定字符类型，后再以utf8写入json文件
                        line.append(chr(charNum))
                    else:
                        newBlock["strList"].append("".join(line))
                        line.clear()

                newBlockSet["blockList"].append(newBlock)

            self.data.append(newBlockSet)

    def write_json(self):
        json.dump(self.data, self.jsonFile, ensure_ascii=False,
                  indent='\t', sort_keys=False)

    #####################
    # json2txt

    def __calc_charCount__(self, block: dict) -> int:
        """
        清点block中真正包含的字符数
        """
        count = 0

        for line in block["strList"]:
            count += len(line) + 1  # 各字符串末尾的'\0'，也要算进去

        return count

    def read_json(self):
        self.data = json.load(self.jsonFile)

    def write_txt(self):
        for _blockSet in self.data:
            blockCount = np.uint32(_blockSet["blockCount"])
            blockCount.tofile(self.txtFile)

            for _block in _blockSet["blockList"]:
                blockHead = np.array(
                    (_block["id"], _block["charCount"]), dtype=np.uint32)

                charCount = self.__calc_charCount__(_block)
                if (charCount != blockHead[-1]):
                    print("记载包含{0:n}个字符，实际包含{1:n}个字符。程序将以实际计得的字数为准".format(
                        blockHead[-1], charCount))
                    blockHead[-1] = charCount

                blockHead.tofile(self.txtFile)

                for lineStr in _block["strList"]:
                    lineNum = [ord(c) for c in lineStr]  # 转换回utf16le编码
                    lineNum.append(0x0000)

                    line = np.array(lineNum, dtype=np.uint16)
                    line.tofile(self.txtFile)


def main():
    cmdParser = argparse.ArgumentParser(
        description="PSP Metal Slug XX 非常规.TXT文件与.json文件互转工具")
    cmdParser.add_argument("inFilePath", help="传入文件路径")
    cmdParser.add_argument(
        "mode", help="转换模式：txt2json / json2txt", choices=("txt2json", "json2txt"))
    cmdParser.add_argument("-o", "--out-file", help="传出文件路径",
                           dest="outFilePath", required=False, default=None)

    args = cmdParser.parse_args()

    inFilePath = Path(args.inFilePath).absolute()
    outFilePath = (Path(args.outFilePath).absolute()
                   if (args.outFilePath) else None)
    mode = args.mode

    c = (Converter(inFilePath, mode, outFilePath) if (outFilePath)
         else Converter(inFilePath, mode))

    match (mode):
        case "txt2json":
            c.read_txt()
            # pp.pprint(c.data)
            c.write_json()
        case "json2txt":
            c.read_json()
            c.write_txt()

    c.clear()


if (__name__ == "__main__"):
    sys.exit(main())
