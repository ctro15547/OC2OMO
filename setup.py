"""
py2app 打包配置
将 macbar-omo-tool 打包为 macOS .app
# requires: py2app>=0.28
"""
import glob
import sys
import os
from setuptools import setup


def _find_libffi():
    """
    在当前 Python 环境中查找 libffi.8.dylib。
    conda 环境下通常在 $CONDA_PREFIX/lib/ 或 Python 框架目录中。
    返回找到的路径列表，未找到返回空列表。
    """
    # 从当前 Python 可执行文件推导 conda 环境根目录
    prefix = os.path.dirname(os.path.dirname(sys.executable))
    candidates = glob.glob(os.path.join(prefix, "lib", "libffi*.dylib"))
    if candidates:
        print(f"[setup] 找到 libffi：{candidates[0]}")
        return [candidates[0]]
    print("[setup] 警告：未找到 libffi.dylib，ctypes 可能无法加载")
    return []


APP = ["src/main.py"]

# 需要打包进去的额外数据文件
DATA_FILES = []

OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "LSUIElement": True,
        "CFBundleName": "cc2omo",
        "CFBundleDisplayName": "cc2omo",
        "CFBundleIdentifier": "com.local.cc2omo",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
    },
    "packages": ["AppKit", "Foundation"],
    # 自动查找并打包 conda 环境中的 libffi，解决 ctypes 加载失败问题
    "frameworks": _find_libffi(),
}

setup(
    name="cc2omo",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
