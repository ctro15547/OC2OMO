"""
插件检测模块
负责在 plugin 列表中查找 oh-my-opencode，提取版本号，管理 omo_plugin.txt
"""

import os


class PluginDetector:
    """oh-my-opencode 插件检测模块"""

    @staticmethod
    def find_omo_plugin(plugin_list: list) -> "str | None":
        """
        在 plugin 列表中查找包含 'oh-my-opencode' 的条目。
        找到返回完整字符串（如 'oh-my-opencode@3.7.4'），否则返回 None。
        plugin_list 为空或非列表时安全返回 None。
        :param plugin_list: plugin 字符串列表
        """
        # 非列表或空列表直接返回 None
        if not isinstance(plugin_list, list) or not plugin_list:
            return None

        for entry in plugin_list:
            # 只处理字符串类型的条目
            if isinstance(entry, str) and "oh-my-opencode" in entry:
                return entry

        return None

    @staticmethod
    def extract_version(plugin_entry: str) -> "str | None":
        """
        从插件条目中提取 '@' 后的版本号。
        如 'oh-my-opencode@3.7.4' → '3.7.4'，'oh-my-opencode@latest' → 'latest'。
        无 '@' 或格式异常返回 None，'@' 后为空字符串也返回 None。
        :param plugin_entry: 插件条目字符串
        """
        try:
            if not isinstance(plugin_entry, str) or "@" not in plugin_entry:
                return None

            # 取 '@' 后的部分
            version = plugin_entry.split("@", 1)[1]

            # '@' 后为空字符串时返回 None
            if not version:
                return None

            return version
        except Exception as e:
            print(f"[PluginDetector] 提取版本号异常: {e}")
            return None

    @staticmethod
    def save_plugin_entry(config_dir: str, plugin_entry: str) -> None:
        """
        将插件条目写入 config_dir/omo_plugin.txt。
        捕获写入异常并打印错误日志。
        :param config_dir: 配置文件所在目录
        :param plugin_entry: 要保存的插件条目字符串
        """
        file_path = os.path.join(config_dir, "omo_plugin.txt")
        try:
            with open(file_path, "w") as f:
                f.write(plugin_entry)
            print(f"[PluginDetector] 插件条目已保存到: {file_path}")
        except Exception as e:
            print(f"[PluginDetector] 保存插件条目失败 ({file_path}): {e}")

    @staticmethod
    def load_plugin_entry(config_dir: str) -> "str | None":
        """
        从 config_dir/omo_plugin.txt 读取插件条目。
        文件不存在时返回 None，其他异常捕获并打印警告，返回 None。
        :param config_dir: 配置文件所在目录
        """
        file_path = os.path.join(config_dir, "omo_plugin.txt")
        try:
            with open(file_path, "r") as f:
                content = f.read().strip()
            return content if content else None
        except FileNotFoundError:
            # 文件不存在属于正常情况，不打印警告
            return None
        except Exception as e:
            print(f"[PluginDetector] 读取插件条目失败 ({file_path}): {e}")
            return None
