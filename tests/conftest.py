"""
pytest 基础 fixtures
为各模块测试提供公共测试夹具
"""
import json
import os
import tempfile

import pytest


@pytest.fixture
def tmp_config_dir(tmp_path):
    """提供一个临时目录，用于存放测试用的配置文件"""
    return str(tmp_path)


@pytest.fixture
def valid_config_file(tmp_path):
    """
    创建一个包含有效 plugin 列表的 opencode.json 临时文件。
    返回文件路径字符串。
    """
    config = {
        "$schema": "https://opencode.ai/config.json",
        "model": "test-model",
        "plugin": ["oh-my-opencode@3.7.4", "other-plugin@1.0.0"],
    }
    config_file = tmp_path / "opencode.json"
    config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False))
    return str(config_file)


@pytest.fixture
def empty_config_file(tmp_path):
    """
    创建一个不含 plugin 键的 opencode.json 临时文件。
    返回文件路径字符串。
    """
    config = {"$schema": "https://opencode.ai/config.json", "model": "test-model"}
    config_file = tmp_path / "opencode.json"
    config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False))
    return str(config_file)


@pytest.fixture
def invalid_json_file(tmp_path):
    """
    创建一个内容为非法 JSON 的临时文件。
    返回文件路径字符串。
    """
    config_file = tmp_path / "opencode.json"
    config_file.write_text("这不是合法的 JSON 内容 {{{")
    return str(config_file)


@pytest.fixture
def nonexistent_path(tmp_path):
    """返回一个不存在的文件路径字符串"""
    return str(tmp_path / "does_not_exist.json")
