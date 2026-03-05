# oc2omo - opencode 插件模式切换工具

macOS 状态栏工具，用于快速切换 opencode 的插件配置模式（oc / omo）。

## 功能

- **状态栏图标**：在 macOS 状态栏显示黑色字母 C 图标，点击展开菜单
- **版本显示**：实时显示当前 oh-my-opencode 插件版本
- **模式切换**：一键在 oc 模式和 omo 模式之间切换
- **配置管理**：通过访达文件选择器选择 opencode.json 配置文件
- **自动检测**：启动时自动检测当前插件状态并更新菜单显示
- **快捷菜单**：提示用户在文件选择面板中可用 ⌘⇧G 快速输入路径

## 快速开始

### 环境准备

需要 macOS 系统和 conda 环境。

**1. 创建 conda 环境**

```bash
conda create -n macbar python=3.11
conda activate macbar
```

**2. 安装依赖**

```bash
pip install -r requirements.txt
pip install py2app
```

### 开发运行

直接在 conda 环境中运行：

```bash
conda activate macbar
python src/main.py
```

### 打包成 .app

**1. 清理旧的构建产物**

```bash
rm -rf build dist
```

**2. 执行打包命令**

```bash
python setup.py py2app
```

打包过程中会自动查找并打包 conda 环境中的 `libffi.8.dylib`，确保应用能正常启动。

**3. 验证打包结果**

```bash
dist/oc2omo.app/Contents/MacOS/oc2omo
```

如果看到状态栏出现 C 图标，说明打包成功。

**4. 移到应用程序文件夹（可选）**

```bash
cp -r dist/oc2omo.app /Applications/
```

之后可以从 Spotlight 搜索 `oc2omo` 或在访达中直接双击启动。

## 菜单项说明

- **omo版本**：显示当前 oh-my-opencode 版本，未检测到时显示 None
- **⚠️ 升级 omo 请先切换到 omo 模式**：oc 模式下的提示（omo 模式自动隐藏）
- **📂 选择 opencode.json…**：点击弹出文件选择面板，选择配置文件
- **⌘⇧G 可在面板中快速输入路径**：文件选择面板的快捷键提示
- **oc / omo**：单选项，切换插件模式
- **退出**：关闭应用（快捷键 ⌘Q）

## 项目结构

```
.
├── src/
│   ├── __init__.py
│   ├── config_reader.py      # 配置读写模块
│   ├── plugin_detector.py    # 插件检测模块
│   ├── mode_switcher.py      # 模式切换模块
│   ├── statusbar_app.py      # 状态栏 UI 主体
│   └── main.py               # 应用入口
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # pytest fixtures
│   └── test_mode_switcher.py # 模式切换测试
├── requirements.txt          # Python 依赖
├── setup.py                  # py2app 打包配置
└── README.md                 # 本文件
```

## 测试

运行单元测试：

```bash
pytest tests/ -v
```

## 技术栈

- **Python 3.11**
- **pyobjc-framework-Cocoa**：macOS AppKit 绑定
- **pytest**：单元测试框架
- **hypothesis**：属性测试库
- **py2app**：Python 应用打包工具

## 许可

MIT
