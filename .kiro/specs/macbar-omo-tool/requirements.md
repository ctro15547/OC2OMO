# 需求文档

## 简介

macbar-omo-tool 是一个 macOS 状态栏工具，使用 Python + pyobjc (AppKit) 开发，运行在 conda macbar 环境下。该工具在状态栏提供一个菜单，用于管理 opencode 的插件配置（oh-my-opencode），支持查看版本、切换插件模式（cc / omo），并在启动时自动检测当前配置状态。

## 术语表

- **StatusBar_App**：macOS 状态栏应用主体，负责创建状态栏图标和菜单
- **Config_Reader**：配置读取模块，负责读取和解析 opencode.json 文件
- **Plugin_Detector**：插件检测模块，负责在 plugin 列表中查找 oh-my-opencode 相关条目
- **Mode_Switcher**：模式切换模块，负责处理 cc / omo 单选切换逻辑
- **opencode.json**：opencode 的配置文件，默认路径为 ~/.config/opencode/opencode.json
- **plugin 列表**：opencode.json 中 "plugin" 键对应的字符串数组，元素格式如 "oh-my-opencode@3.7.4"
- **omo_plugin.txt**：存储 oh-my-opencode 插件条目的文本文件，位于 opencode.json 同目录下
- **omo 模式**：表示 plugin 列表中包含 oh-my-opencode 的状态
- **cc 模式**：表示 plugin 列表中不包含 oh-my-opencode 的状态

## 需求

### 需求 1：状态栏图标与菜单创建

**用户故事：** 作为用户，我希望在 macOS 状态栏看到一个图标，点击后展开菜单，以便快速管理 opencode 插件配置。

#### 验收标准

1. WHEN StatusBar_App 启动完成, THE StatusBar_App SHALL 在 macOS 状态栏创建一个可点击的图标
2. WHEN 用户点击状态栏图标, THE StatusBar_App SHALL 展开一个下拉菜单
3. THE StatusBar_App SHALL 在菜单中按从上到下的顺序显示以下元素：版本标签、配置路径输入框、cc 单选项、omo 单选项

### 需求 2：版本标签显示

**用户故事：** 作为用户，我希望在菜单顶部看到当前 omo 插件的版本号，以便了解当前使用的版本。

#### 验收标准

1. THE StatusBar_App SHALL 在菜单顶部显示格式为 "omo版本：{版本号}" 的文本标签
2. WHEN Plugin_Detector 未检测到 oh-my-opencode 插件, THE StatusBar_App SHALL 将版本标签显示为 "omo版本：None"
3. WHEN Plugin_Detector 检测到 oh-my-opencode 插件条目（如 "oh-my-opencode@3.7.4" 或 "oh-my-opencode@latest"）, THE StatusBar_App SHALL 从该条目中提取 "@" 后的内容并显示为 "omo版本：3.7.4" 或 "omo版本：latest"

### 需求 3：配置路径输入框

**用户故事：** 作为用户，我希望能看到并修改 opencode.json 的路径，以便支持自定义配置文件位置。

#### 验收标准

1. THE StatusBar_App SHALL 在版本标签下方显示一个文本输入框
2. THE StatusBar_App SHALL 将输入框的默认值设置为 "~/.config/opencode/opencode.json"
3. WHEN 用户修改输入框中的路径, THE Config_Reader SHALL 使用新路径作为配置文件读取路径

### 需求 4：模式单选切换

**用户故事：** 作为用户，我希望通过单选框在 cc 模式和 omo 模式之间切换，以便控制 opencode 的插件配置。

#### 验收标准

1. THE StatusBar_App SHALL 在输入框下方显示 "cc" 和 "omo" 两个互斥的单选项
2. WHEN 用户点击 "cc" 单选项, THE Mode_Switcher SHALL 将 "cc" 设为选中状态并取消 "omo" 的选中状态
3. WHEN 用户点击 "omo" 单选项, THE Mode_Switcher SHALL 将 "omo" 设为选中状态并取消 "cc" 的选中状态
4. WHEN 用户点击某个单选项, THE Mode_Switcher SHALL 执行一次对应的切换动作（动作内容后续定义）

### 需求 5：启动时配置读取

**用户故事：** 作为用户，我希望工具启动时自动读取 opencode.json 配置，以便自动检测当前插件状态。

#### 验收标准

1. WHEN StatusBar_App 启动, THE Config_Reader SHALL 读取输入框中指定路径的 opencode.json 文件
2. WHEN Config_Reader 成功读取 opencode.json, THE Config_Reader SHALL 解析其中 "plugin" 键对应的字符串列表
3. IF opencode.json 文件不存在或格式无效, THEN THE Config_Reader SHALL 将 plugin 列表视为空列表并继续运行

### 需求 6：oh-my-opencode 插件检测

**用户故事：** 作为用户，我希望工具自动检测 plugin 列表中是否包含 oh-my-opencode，以便自动设置正确的模式。

#### 验收标准

1. WHEN Config_Reader 解析完 plugin 列表, THE Plugin_Detector SHALL 遍历列表检查是否存在包含 "oh-my-opencode" 字样的元素
2. WHEN Plugin_Detector 检测到包含 "oh-my-opencode" 的元素, THE Plugin_Detector SHALL 将该元素的完整字符串写入 opencode.json 同目录下的 omo_plugin.txt 文件
3. WHEN Plugin_Detector 未检测到包含 "oh-my-opencode" 的元素, THE Plugin_Detector SHALL 不创建 omo_plugin.txt 文件

### 需求 7：启动时自动选择模式

**用户故事：** 作为用户，我希望工具启动时根据检测结果自动选中对应的单选项，以便准确反映当前配置状态。

#### 验收标准

1. WHEN Plugin_Detector 检测到 plugin 列表中包含 oh-my-opencode, THE Mode_Switcher SHALL 自动将 "omo" 单选项设为选中状态
2. WHEN Plugin_Detector 未检测到 plugin 列表中包含 oh-my-opencode, THE Mode_Switcher SHALL 自动将 "cc" 单选项设为选中状态
