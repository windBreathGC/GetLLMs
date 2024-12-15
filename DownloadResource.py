# coding=utf-8
from http import HTTPStatus
from pathlib import Path
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

LOCAL_PATH = Path(r"D:\Projects\Resource")
HUGGING_FACE = "https://huggingface.co/"
MODEL_NAME = "spacy/en_core_web_lg"
BLOCK_SIZE = 4096


def download():
    """下载资源"""
    # 如果本地目录不存在，就先创建好
    if not LOCAL_PATH.exists():
        LOCAL_PATH.mkdir()
    resources = get_resources()
    if not resources:
        return

    # 遍历所有资源
    for url in resources:
        response = requests.get(url, verify=False, stream=True)
        # 计算待下载资源的总大小
        total = int(response.headers.get("content-length", 0))
        # 提取文件名
        file_name = url[url.rfind("/") + 1:]
        # 计算进度，将文件写入到本地
        with tqdm(total=total, unit="B", unit_scale=True) as progress_bar:
            with open(Path(LOCAL_PATH, file_name).as_posix(), "wb") as file:
                for data in response.iter_content(BLOCK_SIZE):
                    progress_bar.update(len(data))
                    file.write(data)


def get_resources() -> List:
    """获取Hugging Face指定连接下的所有可下载链接"""
    url = urljoin(HUGGING_FACE, f"{MODEL_NAME}/tree/main")
    response = requests.get(url, verify=False)
    status = response.status_code
    if status != HTTPStatus.OK:
        print("\033[1;31;40m访问抱抱脸网站失败！\033[0m")
        return []

    soup = BeautifulSoup(response.content, features="lxml")
    links = soup.find_all('a', title="Download file")
    items = []
    for link in links:
        # 如果未找到合法的attrs属性或者href字段，就退出
        if not isinstance(link.attrs, dict) or not link.attrs.get("href"):
            continue
        href = link.attrs.get("href")
        # 如果找到?，就只截取前面部分
        separator = href.rfind("?")
        if separator > 0:
            href = href[:separator]
        items.append(urljoin(HUGGING_FACE, href))
    return items


if __name__ == '__main__':
    download()
