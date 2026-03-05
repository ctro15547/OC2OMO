"""
配置读取模块
负责读取、解析和写入 opencode.json 配置文件
"""
# requires: pyobjc-framework-Cocoa>=9.0

import json
import os


class ConfigReader:
    """配置文件读写模块，操作 opencode.json"""

    def __init__(self, config_path: str = "~/.config/opencode/opencode.json"):
        """
        初始化，设置配置文件路径。
        :param config_path: opencode.json 的路径，支持 ~ 展开
        """
        # 展开 ~ 为实际用户目录
        self.config_path = os.path.expanduser(config_path)

    def read_config(self) -> dict:
        """
        读取并解析 opencode.json。
        文件不存在或格式无效时返回空 dict。
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # 文件不存在，视为空配置
            return {}
        except json.JSONDecodeError:
            # JSON 格式无效，视为空配置
            print(f"[警告] 配置文件格式无效，无法解析 JSON：{self.config_path}")
            return {}
        except Exception as e:
            # 其他异常，打印警告并返回空配置
            print(f"[警告] 读取配置文件时发生未知错误：{e}")
            return {}

    def get_plugin_list(self) -> list:
        """
        从配置中提取 plugin 列表。
        "plugin" 键不存在或值不是数组时返回空列表。
        """
        config = self.read_config()
        plugin = config.get("plugin")
        # 确保返回值是列表类型
        if not isinstance(plugin, list):
            return []
        return plugin

    def write_config(self, config: dict) -> None:
        """
        将修改后的配置写回 opencode.json，保持格式化缩进。
        :param config: 要写入的配置 dict
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                # 保持格式化缩进，ensure_ascii=False 支持中文等非 ASCII 字符
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[错误] 写入配置文件失败：{e}")

    def set_config_path(self, new_path: str) -> None:
        """
        更新配置文件路径，支持 ~ 展开。
        :param new_path: 新的配置文件路径
        """
        # 展开 ~ 为实际用户目录
        self.config_path = os.path.expanduser(new_path)
