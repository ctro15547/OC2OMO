"""
模式切换模块
负责处理 oc / omo 单选切换逻辑，修改 plugin 列表并写回配置
"""

import os


class ModeSwitcher:
    """oc/omo 模式切换模块"""

    def __init__(self, config_reader, plugin_detector):
        """
        初始化，注入 ConfigReader 和 PluginDetector 依赖。
        :param config_reader: ConfigReader 实例
        :param plugin_detector: PluginDetector 实例（或类，因方法均为静态方法）
        """
        self.config_reader = config_reader
        self.plugin_detector = plugin_detector
        # 从配置文件路径推导出配置目录，用于读写 omo_plugin.txt
        self.config_dir = os.path.dirname(self.config_reader.config_path)

    def switch_to_oc(self) -> None:
        """
        切换到 oc 模式：
        1. 从 plugin 列表中移除 oh-my-opencode 条目
        2. 将该条目备份到 omo_plugin.txt
        3. 写回配置
        若已是 oc 模式（未找到 omo 条目），打印日志说明。
        """
        try:
            config = self.config_reader.read_config()
            plugin_list = config.get("plugin", [])

            # 查找 omo 插件条目
            omo_entry = self.plugin_detector.find_omo_plugin(plugin_list)

            if omo_entry is None:
                # 已经是 oc 模式，无需操作
                print("[ModeSwitcher] 当前已是 oc 模式，plugin 列表中未找到 oh-my-opencode 条目")
                return

            # 备份 omo 条目到 omo_plugin.txt
            self.plugin_detector.save_plugin_entry(self.config_dir, omo_entry)

            # 从 plugin 列表移除 omo 条目
            plugin_list = [p for p in plugin_list if p != omo_entry]

            # 更新配置并写回
            config["plugin"] = plugin_list
            self.config_reader.write_config(config)
            print(f"[ModeSwitcher] 已切换到 oc 模式，移除条目：{omo_entry}")

        except Exception as e:
            print(f"[ModeSwitcher] 切换到 oc 模式时发生错误：{e}")

    def switch_to_omo(self) -> None:
        """
        切换到 omo 模式：
        1. 从 omo_plugin.txt 读取备份的插件条目
        2. 将该条目添加回 plugin 列表（避免重复）
        3. 写回配置
        omo_plugin.txt 不存在时提示用户无法恢复，直接返回。
        """
        try:
            # 读取备份的 omo 插件条目
            omo_entry = self.plugin_detector.load_plugin_entry(self.config_dir)

            if omo_entry is None:
                # 备份文件不存在，无法恢复
                print("[ModeSwitcher] 无法恢复 omo 插件条目，omo_plugin.txt 不存在")
                return

            config = self.config_reader.read_config()
            plugin_list = config.get("plugin", [])

            # 确保不重复添加：若列表中已存在 omo 条目则跳过
            existing = self.plugin_detector.find_omo_plugin(plugin_list)
            if existing is not None:
                print(f"[ModeSwitcher] plugin 列表中已存在 omo 条目：{existing}，无需重复添加")
                return

            # 将备份条目添加到 plugin 列表
            plugin_list.append(omo_entry)

            # 更新配置并写回
            config["plugin"] = plugin_list
            self.config_reader.write_config(config)
            print(f"[ModeSwitcher] 已切换到 omo 模式，恢复条目：{omo_entry}")

        except Exception as e:
            print(f"[ModeSwitcher] 切换到 omo 模式时发生错误：{e}")

    def get_current_mode(self) -> str:
        """
        检测当前模式。
        plugin 列表中包含 oh-my-opencode 时返回 'omo'，否则返回 'oc'。
        """
        try:
            plugin_list = self.config_reader.get_plugin_list()
            omo_entry = self.plugin_detector.find_omo_plugin(plugin_list)
            return "omo" if omo_entry is not None else "oc"
        except Exception as e:
            print(f"[ModeSwitcher] 检测当前模式时发生错误：{e}")
            # 异常时默认返回 oc 模式
            return "oc"
