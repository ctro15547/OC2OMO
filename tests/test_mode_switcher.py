"""
ModeSwitcher 单元测试
验证 cc/omo 模式切换逻辑的正确性
"""
import json
import os

import pytest

from src.config_reader import ConfigReader
from src.mode_switcher import ModeSwitcher
from src.plugin_detector import PluginDetector


# ──────────────────────────────────────────────
# 辅助函数
# ──────────────────────────────────────────────

def make_switcher(tmp_path, plugin_list=None):
    """
    在临时目录创建 opencode.json，返回 (ModeSwitcher, config_path)。
    plugin_list 为 None 时配置中不含 plugin 键。
    """
    config = {"model": "test-model"}
    if plugin_list is not None:
        config["plugin"] = plugin_list

    config_file = tmp_path / "opencode.json"
    config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False))

    reader = ConfigReader(str(config_file))
    detector = PluginDetector()
    switcher = ModeSwitcher(reader, detector)
    return switcher, str(config_file)


def read_plugin_list(config_path: str) -> list:
    """读取配置文件中的 plugin 列表"""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f).get("plugin", [])


# ──────────────────────────────────────────────
# switch_to_cc 测试
# ──────────────────────────────────────────────

class TestSwitchToCc:
    def test_removes_omo_from_plugin_list(self, tmp_path):
        """切换到 cc 后，plugin 列表中不应包含 oh-my-opencode"""
        switcher, config_path = make_switcher(
            tmp_path, ["oh-my-opencode@3.7.4", "other-plugin@1.0.0"]
        )
        switcher.switch_to_cc()
        plugins = read_plugin_list(config_path)
        assert all("oh-my-opencode" not in p for p in plugins)

    def test_saves_omo_entry_to_txt(self, tmp_path):
        """切换到 cc 后，omo_plugin.txt 应包含被移除的条目"""
        switcher, _ = make_switcher(
            tmp_path, ["oh-my-opencode@3.7.4"]
        )
        switcher.switch_to_cc()
        txt_path = os.path.join(str(tmp_path), "omo_plugin.txt")
        assert os.path.exists(txt_path)
        assert open(txt_path).read().strip() == "oh-my-opencode@3.7.4"

    def test_preserves_other_plugins(self, tmp_path):
        """切换到 cc 后，其他插件条目应保留"""
        switcher, config_path = make_switcher(
            tmp_path, ["oh-my-opencode@3.7.4", "other-plugin@1.0.0"]
        )
        switcher.switch_to_cc()
        plugins = read_plugin_list(config_path)
        assert "other-plugin@1.0.0" in plugins

    def test_already_cc_mode_no_error(self, tmp_path):
        """已是 cc 模式时再次切换不应报错"""
        switcher, _ = make_switcher(tmp_path, ["other-plugin@1.0.0"])
        # 不应抛出异常
        switcher.switch_to_cc()


# ──────────────────────────────────────────────
# switch_to_omo 测试
# ──────────────────────────────────────────────

class TestSwitchToOmo:
    def test_restores_omo_entry(self, tmp_path):
        """cc → omo round-trip：切换回 omo 后 plugin 列表应包含原始条目"""
        switcher, config_path = make_switcher(
            tmp_path, ["oh-my-opencode@3.7.4"]
        )
        switcher.switch_to_cc()
        switcher.switch_to_omo()
        plugins = read_plugin_list(config_path)
        assert "oh-my-opencode@3.7.4" in plugins

    def test_no_txt_file_does_not_raise(self, tmp_path):
        """omo_plugin.txt 不存在时，switch_to_omo 不应抛出异常"""
        switcher, _ = make_switcher(tmp_path, [])
        # 确保 txt 文件不存在
        txt_path = os.path.join(str(tmp_path), "omo_plugin.txt")
        assert not os.path.exists(txt_path)
        # 不应抛出异常
        switcher.switch_to_omo()

    def test_no_txt_file_mode_stays_cc(self, tmp_path):
        """omo_plugin.txt 不存在时，模式应保持 cc"""
        switcher, _ = make_switcher(tmp_path, [])
        switcher.switch_to_omo()
        assert switcher.get_current_mode() == "cc"

    def test_no_duplicate_omo_entry(self, tmp_path):
        """重复切换到 omo 不应产生重复的 oh-my-opencode 条目"""
        switcher, config_path = make_switcher(
            tmp_path, ["oh-my-opencode@3.7.4"]
        )
        switcher.switch_to_cc()
        switcher.switch_to_omo()
        switcher.switch_to_omo()  # 再次切换，应跳过
        plugins = read_plugin_list(config_path)
        omo_count = sum(1 for p in plugins if "oh-my-opencode" in p)
        assert omo_count == 1


# ──────────────────────────────────────────────
# get_current_mode 测试
# ──────────────────────────────────────────────

class TestGetCurrentMode:
    def test_returns_omo_when_omo_in_list(self, tmp_path):
        """plugin 列表含 oh-my-opencode 时返回 'omo'"""
        switcher, _ = make_switcher(tmp_path, ["oh-my-opencode@3.7.4"])
        assert switcher.get_current_mode() == "omo"

    def test_returns_cc_when_no_omo(self, tmp_path):
        """plugin 列表不含 oh-my-opencode 时返回 'cc'"""
        switcher, _ = make_switcher(tmp_path, ["other-plugin@1.0.0"])
        assert switcher.get_current_mode() == "cc"

    def test_returns_cc_when_empty_list(self, tmp_path):
        """plugin 列表为空时返回 'cc'"""
        switcher, _ = make_switcher(tmp_path, [])
        assert switcher.get_current_mode() == "cc"

    def test_only_returns_cc_or_omo(self, tmp_path):
        """返回值只能是 'cc' 或 'omo'"""
        for plugins in [[], ["oh-my-opencode@1.0"], ["other@1.0"]]:
            switcher, _ = make_switcher(tmp_path, plugins)
            assert switcher.get_current_mode() in ("cc", "omo")
