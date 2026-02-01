# msxx\_txt

PSP Metal Slug XX 非常规.TXT文件与.json文件互转工具。

## 用法

详见程序的`--help`提示。

### 示例

`Linux`下：

```
$ ./msxx_txt.py ./TEXT_JP.TXT txt2json -o /tmp/TEXT_JP.json
```

## 依赖

* `python3 >= 3.10`：3.10后才支持match-case语句。
* `numpy`：作用跟林檎一般大小的破程序居然还要numpy，实在是太屑了。

## 附件

* `FUN_08881630.c`：从[Ghidra](https://github.com/NationalSecurityAgency/ghidra/)中得到的，读取TXT文件元数据的函数。通过它才真正确定了TXT文件的结构。带有些许注释。
* `example.tar.xz`：内含`MSXX-Europe`中的`TEXT_JP.TXT`文件及其成功转换后的文件`TEXT_JP-2.json`，作示例文件用。

## LICENCE

LGPL-3

----
wyz\_2015
