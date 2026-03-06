"""
状态栏应用主体
负责创建 macOS 状态栏图标、构建菜单、协调各模块
"""
# requires: pyobjc-framework-Cocoa>=9.0

import os
import subprocess

from AppKit import (
    NSApplication,
    NSStatusBar,
    NSMenu,
    NSMenuItem,
    NSOpenPanel,
    NSOnState,
    NSOffState,
    NSImage,
    NSBezierPath,
    NSColor,
    NSFont,
    NSString,
    NSAttributedString,
    NSMakeRect,
    NSMakeSize,
    NSForegroundColorAttributeName,
    NSFontAttributeName,
)
from Foundation import NSMutableDictionary

from config_reader import ConfigReader
from plugin_detector import PluginDetector
from mode_switcher import ModeSwitcher


class StatusBarApp:
    """macOS 状态栏应用主体"""

    def __init__(self):
        """
        初始化应用：
        - 创建 NSApplication 和状态栏图标
        - 初始化各功能模块
        - 执行启动自动检测
        - 构建菜单
        """
        try:
            # 创建 macOS 应用实例
            self.app = NSApplication.sharedApplication()

            # 创建状态栏图标，-1 表示自动宽度
            self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(-1)
            # 用代码绘制"实心方块镂空C"图标
            icon = self._make_icon()
            if icon:
                self.status_item.button().setImage_(icon)
            else:
                self.status_item.setTitle_("C")

            # 初始化各功能模块
            self.config_reader = ConfigReader()
            self.plugin_detector = PluginDetector()
            self.mode_switcher = ModeSwitcher(self.config_reader, self.plugin_detector)

            # 启动时自动检测插件状态（菜单项尚未创建，_auto_detect 内部用 hasattr 保护）
            self._auto_detect()

            # 构建菜单
            self.build_menu()

        except Exception as e:
            print(f"[StatusBarApp] 初始化失败：{e}")

    def build_menu(self) -> None:
        """
        构建下拉菜单，顺序：
        1. 版本标签（不可点击）
        2. 分隔线
        3. 路径输入框（NSTextField 嵌入 NSMenuItem）
        4. 分隔线
        5. oc 单选项
        6. omo 单选项
        """
        try:
            menu = NSMenu.alloc().init()
            # 设置菜单 delegate 为 self，以便在 menuWillOpen_ 中让输入框获得焦点
            menu.setDelegate_(self)

            # --- 1. 版本标签（不可点击）---
            version_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "omo版本：None", None, ""
            )
            menu.addItem_(version_item)
            self.menu_item_version = version_item

            # --- 1b. oc 模式提示（oc 时显示，omo 时隐藏）---
            hint_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "⚠️ 升级 omo 请先切换到 omo 模式", None, ""
            )
            hint_item.setEnabled_(False)   # 灰色不可点击，仅作提示
            menu.addItem_(hint_item)
            self.menu_item_hint = hint_item

            # --- 2. 分隔线 ---
            menu.addItem_(NSMenuItem.separatorItem())

            # --- 3. 选择配置文件路径（点击弹出访达文件选择面板）---
            path_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "📂 选择 opencode.json…", "onSelectPath:", ""
            )
            path_item.setTarget_(self)
            menu.addItem_(path_item)
            self.menu_item_path = path_item

            # --- 3b. 快捷键提示（灰色不可点击）---
            tip_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "  ⌘⇧G 可在面板中快速输入路径", None, ""
            )
            tip_item.setEnabled_(False)
            menu.addItem_(tip_item)

            # --- 4. 分隔线 ---
            menu.addItem_(NSMenuItem.separatorItem())

            # --- 5. oc 单选项 ---
            oc_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "oc", "onModeSwitch:", ""
            )
            oc_item.setTarget_(self)
            menu.addItem_(oc_item)
            self.menu_item_oc = oc_item

            # --- 6. omo 单选项 ---
            omo_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "omo", "onModeSwitch:", ""
            )
            omo_item.setTarget_(self)
            menu.addItem_(omo_item)
            self.menu_item_omo = omo_item

            # --- 7. 分隔线 ---
            menu.addItem_(NSMenuItem.separatorItem())

            # --- 8. 开机启动勾选项 ---
            is_enabled = self._is_launch_at_startup_enabled()
            startup_title = f"开机启动 {'✅' if is_enabled else '❌'}"
            startup_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                startup_title, "onToggleStartup:", ""
            )
            startup_item.setTarget_(self)
            # 已启用时显示勾选状态
            startup_item.setState_(NSOnState if is_enabled else NSOffState)
            menu.addItem_(startup_item)
            self.menu_item_startup = startup_item

            # --- 9. 分隔线 ---
            menu.addItem_(NSMenuItem.separatorItem())

            # --- 10. 退出按钮 ---
            quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "退出", "onQuit:", "q"
            )
            quit_item.setTarget_(self)
            menu.addItem_(quit_item)

            # 将菜单绑定到状态栏图标
            self.status_item.setMenu_(menu)

            # 菜单构建完成后，根据已检测的状态更新菜单显示
            self._auto_detect()

        except Exception as e:
            print(f"[StatusBarApp] 构建菜单失败：{e}")

    def update_version_label(self, version: "str | None") -> None:
        """
        更新版本标签显示。
        格式：'omo版本：{version}'，version 为 None 时显示 'omo版本：None'。
        :param version: 版本号字符串或 None
        """
        try:
            label = f"omo版本：{version}"
            self.menu_item_version.setTitle_(label)
        except Exception as e:
            print(f"[StatusBarApp] 更新版本标签失败：{e}")

    def onModeSwitch_(self, sender) -> None:
        """
        单选项点击回调（ObjC selector 格式）。
        根据点击的菜单项标题调用对应的模式切换方法，
        并更新单选状态和版本标签。
        :param sender: 触发事件的 NSMenuItem
        """
        try:
            title = sender.title()
            # 标题可能带有警告后缀，只取前缀判断模式
            if title.startswith("oc"):
                mode = "oc"
            elif title.startswith("omo"):
                mode = "omo"
            else:
                return

            if mode == "oc":
                self.mode_switcher.switch_to_oc()
            elif mode == "omo":
                # 每次都尝试切换，支持用户补上备份后重试
                self.mode_switcher.switch_to_omo()
                new_mode = self.mode_switcher.get_current_mode()

                if new_mode == "oc":
                    # 切换失败，保持 oc 选中状态并在 omo 右侧持续显示警告
                    self._show_notification(
                        "无法切换到 omo 模式",
                        "未找到 omo 插件版本备份或没安装 omo"
                    )
                    self.menu_item_oc.setState_(NSOnState)
                    self.menu_item_omo.setState_(NSOffState)
                    return
                else:
                    # 切换成功，清除之前可能存在的警告提示
                    self._clear_menu_alert()

            # 更新单选状态：被点击项选中，另一项取消选中
            if mode == "oc":
                self.menu_item_oc.setState_(NSOnState)
                self.menu_item_omo.setState_(NSOffState)
            elif mode == "omo":
                self.menu_item_omo.setState_(NSOnState)
                self.menu_item_oc.setState_(NSOffState)

            # 切换后重新检测版本并更新标签和提示行
            plugin_list = self.config_reader.get_plugin_list()
            omo_entry = PluginDetector.find_omo_plugin(plugin_list)
            if omo_entry:
                version = PluginDetector.extract_version(omo_entry)
                self.update_version_label(version)
                self.menu_item_hint.setHidden_(True)
            else:
                self.update_version_label(None)
                self.menu_item_hint.setHidden_(False)

        except Exception as e:
            print(f"[StatusBarApp] 模式切换回调失败：{e}")

    def controlTextDidEndEditing_(self, notification) -> None:
        """
        路径输入框编辑完成回调（NSTextField delegate）。
        获取新路径，更新 ConfigReader，并重新执行自动检测。
        :param notification: NSNotification 对象
        """
        try:
            new_path = notification.object().stringValue()
            print(f"[StatusBarApp] 配置路径已更新：{new_path}")
            self.config_reader.set_config_path(new_path)
            # 重新检测并更新菜单状态
            self._auto_detect()
        except Exception as e:
            print(f"[StatusBarApp] 路径变更回调失败：{e}")

    def _make_icon(self) -> "NSImage | None":
        """
        绘制状态栏图标：透明背景，黑色实心字母 C 居中。
        使用 template 模式让 macOS 自动适配深色/浅色主题。
        """
        try:
            size = 18.0
            image = NSImage.alloc().initWithSize_(NSMakeSize(size, size))
            image.lockFocus()

            # 清空为透明背景
            NSColor.clearColor().setFill()
            NSBezierPath.fillRect_(NSMakeRect(0, 0, size, size))

            # 绘制黑色加粗字母 C，居中
            attrs = NSMutableDictionary.dictionary()
            attrs[NSFontAttributeName] = NSFont.boldSystemFontOfSize_(14.0)
            attrs[NSForegroundColorAttributeName] = NSColor.blackColor()

            letter = NSString.stringWithString_("C")
            attr_str = NSAttributedString.alloc().initWithString_attributes_(letter, attrs)

            letter_size = attr_str.size()
            x = (size - letter_size.width) / 2.0
            y = (size - letter_size.height) / 2.0
            attr_str.drawAtPoint_((x, y))

            image.unlockFocus()

            # template 模式：macOS 自动将黑色像素在深色模式下反转为白色
            image.setTemplate_(True)
            return image

        except Exception as e:
            print(f"[StatusBarApp] 绘制图标失败：{e}")
            return None

    def _auto_detect(self) -> None:
        """
        启动时自动检测流程：
        1. 读取 plugin 列表
        2. 检测 oh-my-opencode 插件
        3. 根据检测结果更新版本标签和单选状态
        注意：菜单项可能尚未创建，使用 hasattr 保护
        """
        try:
            plugin_list = self.config_reader.get_plugin_list()
            omo_entry = PluginDetector.find_omo_plugin(plugin_list)

            if omo_entry is not None:
                # 检测到 omo 插件：写入备份文件，更新版本标签，选中 omo
                config_dir = self.mode_switcher.config_dir
                PluginDetector.save_plugin_entry(config_dir, omo_entry)

                version = PluginDetector.extract_version(omo_entry)

                # 菜单项存在时才更新 UI
                if hasattr(self, "menu_item_version"):
                    self.update_version_label(version)
                if hasattr(self, "menu_item_hint"):
                    # omo 模式下隐藏提示行
                    self.menu_item_hint.setHidden_(True)
                if hasattr(self, "menu_item_omo"):
                    self.menu_item_omo.setState_(NSOnState)
                if hasattr(self, "menu_item_cc"):
                    self.menu_item_cc.setState_(NSOffState)
            else:
                # 未检测到 omo 插件：版本显示 None，选中 oc，显示提示行
                if hasattr(self, "menu_item_version"):
                    self.update_version_label(None)
                if hasattr(self, "menu_item_hint"):
                    # oc 模式下显示升级提示
                    self.menu_item_hint.setHidden_(False)
                if hasattr(self, "menu_item_oc"):
                    self.menu_item_oc.setState_(NSOnState)
                if hasattr(self, "menu_item_omo"):
                    self.menu_item_omo.setState_(NSOffState)

        except Exception as e:
            print(f"[StatusBarApp] 自动检测失败：{e}")

    def _show_notification(self, title: str, message: str) -> None:
        """
        显示 macOS 系统通知。
        优先使用新版 UNUserNotificationCenter（macOS 10.14+），
        旧版 API 已废弃且在新系统上返回 None。
        :param title: 通知标题
        :param message: 通知内容
        """
        try:
            # 使用新版 UserNotifications framework
            import UserNotifications
            center = UserNotifications.UNUserNotificationCenter.currentNotificationCenter()

            # 请求通知权限
            def request_handler(granted, error):
                if not granted:
                    print(f"[StatusBarApp] 通知权限未授予，改用菜单提示")
                    return

            center.requestAuthorizationWithOptions_completionHandler_(
                UserNotifications.UNAuthorizationOptionAlert,
                request_handler
            )

            # 构建通知内容
            content = UserNotifications.UNMutableNotificationContent.alloc().init()
            content.setTitle_(title)
            content.setBody_(message)

            # 立即触发
            trigger = None
            import uuid
            request = UserNotifications.UNNotificationRequest.requestWithIdentifier_content_trigger_(
                str(uuid.uuid4()), content, trigger
            )
            center.addNotificationRequest_withCompletionHandler_(request, None)

        except Exception as e:
            # 通知失败时降级为菜单项临时提示
            print(f"[StatusBarApp] 显示通知失败：{e}，改用菜单标题提示")
            self._show_menu_alert(message)

    def _show_menu_alert(self, message: str) -> None:
        """
        在 omo 菜单项右侧持续显示警告提示，直到切换成功才清除。
        :param message: 要显示的提示文字
        """
        try:
            self.menu_item_omo.setTitle_(f"omo  ⚠️ {message}")
            print(f"[StatusBarApp] omo 菜单项显示警告：{message}")
        except Exception as e:
            print(f"[StatusBarApp] 菜单提示失败：{e}")

    def _clear_menu_alert(self) -> None:
        """切换成功后清除 omo 菜单项的警告提示，恢复原始标题。"""
        try:
            self.menu_item_omo.setTitle_("omo")
            print("[StatusBarApp] omo 菜单项警告已清除")
        except Exception as e:
            print(f"[StatusBarApp] 清除菜单提示失败：{e}")

    def menuWillOpen_(self, menu) -> None:
        """
        菜单即将显示时的回调（NSMenu delegate）。
        手动让路径输入框获得焦点，解决菜单内 NSTextField 无法输入的问题。
        """
        try:
            if hasattr(self, "path_field"):
                # 让窗口将第一响应者设为输入框
                self.app.mainWindow()
                self.path_field.window()
                # 通过 NSApp 的 keyWindow 让输入框成为第一响应者
                from AppKit import NSApp
                key_win = NSApp.keyWindow()
                if key_win:
                    key_win.makeFirstResponder_(self.path_field)
        except Exception as e:
            print(f"[StatusBarApp] menuWillOpen_ 回调失败：{e}")

    def onSelectPath_(self, sender) -> None:
        """
        点击"选择 opencode.json"菜单项时弹出访达文件选择面板。
        用户选择文件后更新 ConfigReader 路径并重新检测。
        """
        try:
            panel = NSOpenPanel.openPanel()
            panel.setTitle_("选择 opencode.json")
            panel.setMessage_("请选择 opencode 配置文件")
            panel.setAllowedFileTypes_(["json"])
            panel.setAllowsMultipleSelection_(False)
            panel.setCanChooseDirectories_(False)
            panel.setCanChooseFiles_(True)

            # 以模态方式运行面板（1 = NSModalResponseOK）
            result = panel.runModal()
            if result == 1:
                selected_path = panel.URL().path()
                print(f"[StatusBarApp] 用户选择配置文件：{selected_path}")
                self.config_reader.set_config_path(selected_path)
                # 更新菜单项标题，显示当前选中的文件名
                filename = os.path.basename(selected_path)
                self.menu_item_path.setTitle_(f"📂 {filename}")
                # 重新检测插件状态
                self._auto_detect()
        except Exception as e:
            print(f"[StatusBarApp] 选择配置文件失败：{e}")

    def onQuit_(self, sender) -> None:
        """退出按钮回调，终止应用"""
        NSApplication.sharedApplication().terminate_(None)

    def _get_launchagent_path(self) -> str:
        """返回 LaunchAgent plist 文件路径"""
        return os.path.expanduser("~/Library/LaunchAgents/com.local.oc2omo.plist")

    def _get_app_executable(self) -> str:
        """
        获取当前应用的可执行文件路径。
        打包后为 .app 内的二进制，直接运行时为 python 解释器路径。
        """
        import sys
        executable = sys.executable
        # 打包成 .app 后，executable 指向 .app 内的二进制
        # 尝试找到 .app bundle 的实际可执行文件
        bundle_exec = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(executable))),
            "MacOS", "oc2omo"
        )
        if os.path.exists(bundle_exec):
            return bundle_exec
        return executable

    def _is_launch_at_startup_enabled(self) -> bool:
        """检查开机启动是否已启用（plist 文件是否存在）"""
        return os.path.exists(self._get_launchagent_path())

    def _enable_launch_at_startup(self) -> bool:
        """
        启用开机启动：生成 LaunchAgent plist 并注册到 launchctl。
        返回是否成功。
        """
        try:
            import subprocess
            plist_path = self._get_launchagent_path()
            exec_path = self._get_app_executable()

            # 生成 plist 内容
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.local.oc2omo</string>
    <key>ProgramArguments</key>
    <array>
        <string>{exec_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>"""
            # 确保目录存在
            os.makedirs(os.path.dirname(plist_path), exist_ok=True)

            with open(plist_path, "w", encoding="utf-8") as f:
                f.write(plist_content)

            # 注册到 launchctl
            subprocess.run(["launchctl", "load", plist_path], check=True)
            print(f"[StatusBarApp] 开机启动已启用：{plist_path}")
            return True

        except Exception as e:
            print(f"[StatusBarApp] 启用开机启动失败：{e}")
            return False

    def _disable_launch_at_startup(self) -> bool:
        """
        禁用开机启动：从 launchctl 卸载并删除 plist 文件。
        返回是否成功。
        """
        try:
            import subprocess
            plist_path = self._get_launchagent_path()

            if os.path.exists(plist_path):
                subprocess.run(["launchctl", "unload", plist_path], check=True)
                os.remove(plist_path)

            print("[StatusBarApp] 开机启动已禁用")
            return True

        except Exception as e:
            print(f"[StatusBarApp] 禁用开机启动失败：{e}")
            return False

    def onToggleStartup_(self, sender) -> None:
        """
        开机启动勾选项点击回调。
        当前已启用则禁用，未启用则启用，并更新菜单项状态。
        """
        try:
            is_enabled = self._is_launch_at_startup_enabled()

            if is_enabled:
                success = self._disable_launch_at_startup()
                new_state = False
            else:
                success = self._enable_launch_at_startup()
                new_state = True

            if success:
                # 更新菜单项标题和勾选状态
                self.menu_item_startup.setTitle_(f"开机启动 {'✅' if new_state else '❌'}")
                self.menu_item_startup.setState_(NSOnState if new_state else NSOffState)
            else:
                print("[StatusBarApp] 开机启动切换失败，状态未变更")

        except Exception as e:
            print(f"[StatusBarApp] 开机启动切换回调失败：{e}")

    def run(self) -> None:
        """启动应用主循环"""
        try:
            NSApplication.sharedApplication().run()
        except Exception as e:
            print(f"[StatusBarApp] 应用运行失败：{e}")
