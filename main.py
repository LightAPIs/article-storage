# -*- coding: utf-8 -*-
import os
import io
import json
import chardet
import codecs
import argparse
from log import Logger


def handler(path, is_new, is_convert, xlog):
    if os.path.exists(path):
        xlog.info("正在遍历目录: " + path)
        dir_ignore_file = os.path.join(path, "dir_ignore.json")
        dir_ignore_list = read_json_file(dir_ignore_file, [])
        history_dict = {"dir": [], "txt": []}
        if not is_new:
            # 读取历史索引
            history_file = os.path.join(path, "list.json")
            history_dict = read_json_file(history_file, {"dir": [], "txt": []})
        res_dict = {"dir": [], "txt": []}
        for each_name in os.listdir(path):
            each_full_name = os.path.join(path, each_name)
            if os.path.isdir(each_full_name):
                # 目录
                if not is_empty_dir(each_full_name) and not (each_name in dir_ignore_list):
                    res_dict["dir"].append(each_name)
                    handler(each_full_name, is_new, is_convert, xlog)
            else:
                # 文件
                if is_txt_ext(each_full_name):
                    had = False
                    for item in history_dict["txt"]:
                        if item["name"] == each_name:
                            res_dict["txt"].append(item)
                            had = True
                            break

                    if not had:
                        if is_convert:
                            with io.open(each_full_name, mode="rb") as f:
                                data = f.read()
                                source_encoding = chardet.detect(data)
                                if source_encoding["encoding"] != "utf-8":
                                    xlog.info("转换文件编码格式: " + each_full_name)
                                    if (source_encoding["encoding"] == "GB2312"):
                                        content = data.decode("GBK")
                                        content = content.encode(
                                            "utf-8").strip()
                                        codecs.open(each_full_name,
                                                    'wb').write(content)
                                    else:
                                        content = data.decode(
                                            source_encoding["encoding"]
                                        ).encode('utf-8').strip()
                                        codecs.open(each_full_name,
                                                    'wb').write(content)

                        with io.open(each_full_name, mode="r",
                                     encoding="utf-8") as file_load:
                            file_size = os.path.getsize(each_full_name)
                            content = file_load.read()
                            word_num = len(content.strip())
                            item_dict = {
                                "name": each_name,
                                "size": size_convert(file_size),
                                "count": word_num
                            }
                            res_dict["txt"].append(item_dict)

        res_file = os.path.join(path, "list.json")
        with io.open(res_file, mode="w", encoding="utf-8") as load_f:
            json.dump(res_dict, load_f)
            xlog.info("写入数据至文件: " + res_file)


def size_convert(size):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    base = 1024.0
    for i in range(len(units)):
        if (size / base) < 1:
            return "%.2f%s" % (size, units[i])
        size /= base


def is_txt_ext(file_path):
    file_ext = os.path.splitext(file_path)[1]
    if file_ext in [".txt"]:
        return True
    else:
        return False


def is_empty_dir(dir_path):
    """判断目录是否为空

    Args:
        dir_path (string): 目录路径

    Returns:
        bool: 为空时返回 True
    """
    for name in os.listdir(dir_path):
        if is_txt_ext(name):
            return False
    return True


def read_json_file(path, default={}):
    if os.path.exists(path):
        with io.open(path, mode="r", encoding="utf-8") as load_f:
            return json.load(load_f)
    else:
        return default


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="水文仓库文章索引器")
    ap.add_argument("-n",
                    "--new",
                    action="store_true",
                    required=False,
                    help="重建索引文件(会覆盖已存在的索引文件)")
    ap.add_argument("-c",
                    "--convert",
                    action="store_true",
                    required=False,
                    help="索引过程中同时将文本文件编码转为 utf-8")

    args = vars(ap.parse_args())
    xlog = Logger("DEBUG", "log")

    xlog.info("************************************************")
    xlog.info(">>>>>>>>>>>>>水文仓库文章索引器运行日志<<<<<<<<<<<<<")
    if args["new"]:
        xlog.info("++++++++++++++++++++++++++++++++++++++++++++++++")
        xlog.info("本次工作将重建索引文件！")
        xlog.info("++++++++++++++++++++++++++++++++++++++++++++++++")
    if args["convert"]:
        xlog.info("++++++++++++++++++++++++++++++++++++++++++++++++")
        xlog.info("本次工作将自动转换文本文件编码格式！")
        xlog.info("++++++++++++++++++++++++++++++++++++++++++++++++")
    xlog.info("************************************************")

    xlog.info("开始索引工作...")
    handler(os.path.join(os.getcwd(), "src"), args["new"], args["convert"], xlog)
    xlog.info("索引工作完成。")
