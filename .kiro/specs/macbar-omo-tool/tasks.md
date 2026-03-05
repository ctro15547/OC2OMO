# 实现计划：macbar-omo-tool

## 概述

基于多模块架构，按 ConfigReader → PluginDetector → ModeSwitcher → StatusBarApp 的顺序逐步实现，每个模块实现后紧跟测试，最后组装为完整的状态栏应用。使用 Python + pyobjc (AppKit)，运行在 conda macbar 环境下。

## 任务列表

- [x] 1. 创建项目结构和基础模块文件
  - 创建 `src/` 目录，包含 `__init__.py`、`config_reader.py`、`plugin_detector.py`、`mode_switcher.py`、`statusbar_app.py`、`main.py`
  - 创建 `tests/` 目录，包含 `__init__.py`、`conftest.py`
  - 创建 `requirements.txt`，包含 pyobjc、pytest、hypothesis 依赖
  - _需求：1.1, 5.1_

- [x] 2. 实现 ConfigReader 配置读取模块
  - [x] 2.1 实现 ConfigReader 类
    - 实现 `__init__`：接收 config_path 参数，默认值 `~/.config/opencode/opencode.json`，展开 `~` 路径
    - 实现 `read_config`：读取并解析 JSON，文件不存在或格式无效时返回空 dict
    - 实现 `get_plugin_list`：从配置中提取 "plugin" 键对应的列表，不存在或非数组时返回空列表
    - 实现 `write_config`：将配置 dict 写回 JSON 文件，保持格式化缩进
    - 实现 `set_config_path`：更新配置文件路径
    - _需求：3.2, 3.3, 5.1, 5.2, 5.3_

  - [ ]* 2.2 编写 ConfigReader 单元测试
    - 测试正常读取有效 JSON 配置
    - 测试读取不存在的文件返回空 dict
    - 测试读取非法 JSON 返回空 dict
    - 测试缺少 "plugin" 键返回空列表
    - 测试 "plugin" 值不是数组时返回空列表
    - _需求：5.2, 5.3_

  - [ ]* 2.3 编写 ConfigReader 属性测试：plugin 列表解析正确性
    - **属性 5：plugin 列表解析正确性**
    - 使用 hypothesis 生成包含 "plugin" 键的随机 JSON，验证 `get_plugin_list()` 返回值与原始列表一致
    - **验证需求：5.2**

  - [ ]* 2.4 编写 ConfigReader 属性测试：无效配置容错
    - **属性 6：无效配置容错**
    - 使用 hypothesis 生成随机非 JSON 字符串和不存在的路径，验证 `read_config()` 返回空 dict 且不抛异常
    - **验证需求：5.3**

  - [ ]* 2.5 编写 ConfigReader 属性测试：配置路径更新生效
    - **属性 4：配置路径更新生效**
    - 使用 hypothesis 生成随机文件路径，验证 `set_config_path` 后读取操作使用新路径
    - **验证需求：3.3**

- [x] 3. 实现 PluginDetector 插件检测模块
  - [x] 3.1 实现 PluginDetector 类
    - 实现 `find_omo_plugin`：遍历 plugin 列表，查找包含 "oh-my-opencode" 的条目
    - 实现 `extract_version`：从插件条目中提取 "@" 后的版本号，支持 "latest" 等非语义化版本
    - 实现 `save_plugin_entry`：将插件条目写入 omo_plugin.txt
    - 实现 `load_plugin_entry`：从 omo_plugin.txt 读取插件条目
    - _需求：2.3, 6.1, 6.2, 6.3_

  - [ ]* 3.2 编写 PluginDetector 单元测试
    - 测试从包含 omo 的列表中找到插件条目
    - 测试从不包含 omo 的列表中返回 None
    - 测试提取 "oh-my-opencode@3.7.4" 版本号为 "3.7.4"
    - 测试提取 "oh-my-opencode@latest" 版本号为 "latest"
    - 测试无 "@" 的条目返回 None
    - 测试 save/load omo_plugin.txt 的读写
    - _需求：2.3, 6.1, 6.2_

  - [ ]* 3.3 编写 PluginDetector 属性测试：版本号提取正确性
    - **属性 1：版本号提取正确性**
    - 使用 hypothesis 生成随机 `name@version` 字符串，验证提取结果等于 "@" 后的子串
    - **验证需求：2.3**

  - [ ]* 3.4 编写 PluginDetector 属性测试：oh-my-opencode 检测正确性
    - **属性 7：oh-my-opencode 检测正确性**
    - 使用 hypothesis 生成随机字符串列表（含/不含 omo），验证检测结果的正确性
    - **验证需求：6.1**

  - [ ]* 3.5 编写 PluginDetector 属性测试：插件条目备份 round-trip
    - **属性 8：插件条目备份 round-trip**
    - 使用 hypothesis 生成随机插件条目字符串，验证 save 后 load 返回相同内容
    - **验证需求：6.2**

- [x] 4. 检查点 - 确保基础模块测试通过
  - 确保所有测试通过，如有问题请向用户确认。

- [x] 5. 实现 ModeSwitcher 模式切换模块
  - [x] 5.1 实现 ModeSwitcher 类
    - 实现 `__init__`：注入 ConfigReader 和 PluginDetector 依赖
    - 实现 `switch_to_cc`：从 plugin 列表移除 omo 条目，备份到 omo_plugin.txt，写回配置
    - 实现 `switch_to_omo`：从 omo_plugin.txt 恢复插件条目，添加到 plugin 列表，写回配置
    - 实现 `get_current_mode`：检测 plugin 列表中是否包含 omo，返回 "cc" 或 "omo"
    - 处理 omo_plugin.txt 不存在时的错误提示
    - _需求：4.2, 4.3, 4.4, 7.1, 7.2_

  - [ ]* 5.2 编写 ModeSwitcher 单元测试
    - 测试切换到 cc 模式后 plugin 列表不含 omo
    - 测试切换到 omo 模式后 plugin 列表包含 omo
    - 测试 cc → omo round-trip 恢复原始条目
    - 测试 omo_plugin.txt 不存在时切换到 omo 的错误处理
    - _需求：4.2, 4.3, 7.1, 7.2_

  - [ ]* 5.3 编写 ModeSwitcher 属性测试：单选互斥性
    - **属性 3：单选互斥性**
    - 使用 hypothesis 生成随机初始状态和切换序列，验证 `get_current_mode()` 始终返回 "cc" 或 "omo"
    - **验证需求：4.2, 4.3**

  - [ ]* 5.4 编写 ModeSwitcher 属性测试：自动模式检测一致性
    - **属性 9：自动模式检测一致性**
    - 使用 hypothesis 生成随机 plugin 列表，验证 `get_current_mode()` 返回值与列表中是否包含 omo 一致
    - **验证需求：7.1, 7.2**

- [x] 6. 检查点 - 确保模式切换逻辑测试通过
  - 确保所有测试通过，如有问题请向用户确认。

- [x] 7. 实现 StatusBarApp 状态栏应用
  - [x] 7.1 实现 StatusBarApp 类核心框架
    - 使用 AppKit 创建 NSStatusBar 状态栏图标（参考 test_menubar.py）
    - 实现 `build_menu`：按顺序构建菜单项（版本标签 → 路径输入框 → cc 单选 → omo 单选）
    - 使用 `NSMenuItem` 的 `state` 属性（`NSOnState` / `NSOffState`）实现单选效果
    - 使用 `NSTextField` 嵌入 `NSMenuItem.view` 实现路径输入框，默认值 `~/.config/opencode/opencode.json`
    - _需求：1.1, 1.2, 1.3, 3.1, 3.2_

  - [x] 7.2 实现版本标签显示逻辑
    - 实现 `update_version_label`：格式化为 "omo版本：{version}"，未检测到时显示 "omo版本：None"
    - _需求：2.1, 2.2, 2.3_

  - [ ]* 7.3 编写版本标签属性测试：版本标签格式化
    - **属性 2：版本标签格式化**
    - 使用 hypothesis 生成随机版本号字符串和 None，验证格式化结果匹配 "omo版本：{version}" 模式
    - **验证需求：2.1, 2.2**

  - [x] 7.4 实现单选项点击回调和模式切换联动
    - 实现 `on_mode_switch`：点击 cc/omo 单选项时调用 ModeSwitcher 执行切换，更新菜单状态和版本标签
    - 实现路径输入框变更回调：用户修改路径后调用 `ConfigReader.set_config_path` 并重新加载配置
    - _需求：3.3, 4.1, 4.2, 4.3, 4.4_

  - [x] 7.5 实现启动时自动检测流程
    - 启动时调用 ConfigReader 读取配置 → PluginDetector 检测插件 → 自动设置模式和版本标签
    - 检测到 omo 时写入 omo_plugin.txt 并选中 omo 单选项
    - 未检测到时选中 cc 单选项，版本标签显示 "None"
    - _需求：5.1, 5.2, 5.3, 6.1, 6.2, 6.3, 7.1, 7.2_

- [x] 8. 实现 main.py 入口文件
  - 创建应用入口，初始化 StatusBarApp 并调用 `run()`
  - _需求：1.1_

- [x] 9. 最终检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请向用户确认。

## 备注

- 标记 `*` 的任务为可选，可跳过以加速 MVP 开发
- 每个任务引用了对应的需求编号，确保可追溯性
- 属性测试使用 hypothesis 库，每个属性对应设计文档中的正确性属性
- 检查点用于阶段性验证，确保增量开发的正确性
