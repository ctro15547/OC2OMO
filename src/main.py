"""
应用入口文件
初始化 StatusBarApp 并启动主循环
"""
# requires: pyobjc-framework-Cocoa>=9.0

import os
import sys

# 确保 src/ 目录在模块搜索路径中，兼容直接运行和 py2app 打包两种方式
_src_dir = os.path.dirname(os.path.abspath(__file__))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from statusbar_app import StatusBarApp


def main():
    """程序入口：创建状态栏应用并运行"""
    app = StatusBarApp()
    app.run()


if __name__ == "__main__":
    main()
