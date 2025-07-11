# -*- coding: utf-8 -*-
# dk call mcp 用户界面
import os
import sys
import json
# 移除了psutil导入
import argparse
# 移除了subprocess和threading导入
import hashlib
import base64
import io
from typing import Optional, TypedDict, List

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QGroupBox,
    QFileDialog, QScrollArea, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QSettings, QThread, Signal
from PySide6.QtGui import QIcon, QKeyEvent, QPalette, QColor, QPixmap

# 提示词优化模块将异步加载
OPTIMIZER_AVAILABLE = False
_optimizer_module = None

try:
    from PIL import Image, ImageQt
    PIL_AVAILABLE = True
    print("PIL导入成功: PIL版本可用")
except ImportError as e:
    PIL_AVAILABLE = False
    print(f"PIL导入失败: {e}")
    print("注意: 图片功能将被禁用，但其他功能仍可正常使用")
except Exception as e:
    PIL_AVAILABLE = False
    print(f"PIL导入时发生未知错误: {e}")
    print("注意: 图片功能将被禁用，但其他功能仍可正常使用")

class ImageData(TypedDict):
    filename: str
    data: str  # Base64编码的图片数据
    mime_type: str  # 图片MIME类型

class CalldkResult(TypedDict):
    interactive_calldk: str
    images: List[ImageData]

# 移除了命令相关的配置

def set_dark_title_bar(widget: QWidget, dark_title_bar: bool) -> None:
    # 确保我们在Windows系统上
    if sys.platform != "win32":
        return

    from ctypes import windll, c_uint32, byref

    # 获取Windows版本号
    build_number = sys.getwindowsversion().build
    if build_number < 17763:  # Windows 10 1809 最低版本
        return

    # 检查控件的属性是否已经匹配设置
    dark_prop = widget.property("DarkTitleBar")
    if dark_prop is not None and dark_prop == dark_title_bar:
        return

    # 设置属性（如果 dark_title_bar != 0 则为 True，否则为 False）
    widget.setProperty("DarkTitleBar", dark_title_bar)

    # 加载 dwmapi.dll 并调用 DwmSetWindowAttribute
    dwmapi = windll.dwmapi
    hwnd = widget.winId()  # 获取窗口句柄
    attribute = 20 if build_number >= 18985 else 19  # 对于较新的版本使用较新的属性
    c_dark_title_bar = c_uint32(dark_title_bar)  # 转换为C兼容的uint32
    dwmapi.DwmSetWindowAttribute(hwnd, attribute, byref(c_dark_title_bar), 4)

    # 技巧：创建一个1x1像素的无框窗口来强制重绘
    temp_widget = QWidget(None, Qt.FramelessWindowHint)
    temp_widget.resize(1, 1)
    temp_widget.move(widget.pos())
    temp_widget.show()
    temp_widget.deleteLater()  # 在Qt事件循环中安全删除

def get_dark_mode_palette(app: QApplication):
    darkPalette = app.palette()
    darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.WindowText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    darkPalette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ToolTipText, Qt.white)
    darkPalette.setColor(QPalette.Text, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
    darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ButtonText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.BrightText, Qt.red)
    darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    darkPalette.setColor(QPalette.HighlightedText, Qt.white)
    darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.PlaceholderText, QColor(127, 127, 127))
    return darkPalette

# 移除了kill_tree和get_user_environment函数

class OptimizerLoaderThread(QThread):
    """异步加载提示词优化模块的线程"""
    loaded = Signal(bool, str)  # 加载成功/失败, 状态消息

    def run(self):
        global OPTIMIZER_AVAILABLE, _optimizer_module
        try:
            # 动态导入提示词优化模块
            import prompt_optimizer
            _optimizer_module = prompt_optimizer

            # 检查是否可用
            if _optimizer_module.is_optimizer_available():
                OPTIMIZER_AVAILABLE = True
                self.loaded.emit(True, "提示词优化功能已就绪")
            else:
                status = _optimizer_module.get_optimizer_status()
                self.loaded.emit(False, status)
        except ImportError as e:
            self.loaded.emit(False, f"提示词优化模块导入失败: {e}")
        except Exception as e:
            self.loaded.emit(False, f"提示词优化模块加载失败: {e}")

def get_optimizer():
    """获取优化器实例"""
    if _optimizer_module is None:
        raise RuntimeError("提示词优化模块尚未加载")
    return _optimizer_module.get_optimizer()

def is_optimizer_available():
    """检查优化器是否可用"""
    if _optimizer_module is None:
        return False
    return _optimizer_module.is_optimizer_available()

def get_optimizer_status():
    """获取优化器状态"""
    if _optimizer_module is None:
        return "提示词优化模块尚未加载"
    return _optimizer_module.get_optimizer_status()

class OptimizeThread(QThread):
    """提示词优化线程"""
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, input_text):
        super().__init__()
        self.input_text = input_text

    def run(self):
        try:
            if not OPTIMIZER_AVAILABLE:
                self.error.emit("提示词优化模块不可用")
                return

            optimizer = get_optimizer()
            if not optimizer.is_available():
                self.error.emit(optimizer.get_status_message())
                return

            result = optimizer.optimize_prompt(self.input_text)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class CalldkTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event: QKeyEvent):
        # 查找父级 CalldkUI 实例
        parent = self.parent()
        while parent and not isinstance(parent, CalldkUI):
            parent = parent.parent()

        if parent:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                # Ctrl+Enter: 提交
                parent._submit_calldk()
                return
            elif event.key() == Qt.Key_Q and event.modifiers() == Qt.ControlModifier:
                # Ctrl+Q: 提示词优化
                parent._optimize_prompt()
                return
            elif event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
                # Ctrl+Z: 撤销优化
                parent._undo_optimize()
                return

        super().keyPressEvent(event)

# 移除了LogSignals类

class CalldkUI(QMainWindow):
    def __init__(self, project_directory: str, prompt: str):
        super().__init__()
        self.project_directory = project_directory
        self.prompt = prompt

        self.calldk_result = None

        # 图片相关变量
        self.selected_images: List[ImageData] = []
        self.image_preview_widgets: List[QLabel] = []

        # 提示词优化相关变量
        self.optimize_thread = None
        self.original_text_before_optimize = ""  # 用于撤销功能
        self.optimizer_loader_thread = None  # 异步加载线程

        self.setWindowTitle("call dk")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "images", "feedback.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        self.settings = QSettings("CallDK", "CallDK")

        # 为主窗口加载通用UI设置（几何形状、状态）
        self.settings.beginGroup("MainWindow_General")
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(800, 600)
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - 800) // 2
            y = (screen.height() - 600) // 2
            self.move(x, y)
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
        self.settings.endGroup() # 结束 "MainWindow_General" 组
        
        self._create_ui()
        set_dark_title_bar(self, True)

        # 启动异步加载提示词优化模块
        self._start_optimizer_loading()

    def _format_windows_path(self, path: str) -> str:
        if sys.platform == "win32":
            # 将正斜杠转换为反斜杠
            path = path.replace("/", "\\")
            # 如果路径以 x:\ 开头，则将驱动器字母大写
            if len(path) >= 2 and path[1] == ":" and path[0].isalpha():
                path = path[0].upper() + path[1:]
        return path

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 移除了命令区域相关的所有组件

        # 调整高度的call dk部分
        self.calldk_group = QGroupBox("call dk")
        calldk_layout = QVBoxLayout(self.calldk_group)

        self.calldk_text = CalldkTextEdit()
        font_metrics = self.calldk_text.fontMetrics()
        row_height = font_metrics.height()
        # 计算5行的高度 + 边距的一些填充
        padding = self.calldk_text.contentsMargins().top() + self.calldk_text.contentsMargins().bottom() + 5 # 5是额外的垂直填充
        self.calldk_text.setMinimumHeight(5 * row_height + padding)

        self.calldk_text.setPlaceholderText("请在此输入您的call dk (Ctrl+Enter 提交, Ctrl+Q 优化, Ctrl+Z 撤销)")
        
        # 图片上传区域
        image_group = QGroupBox("图片附件")
        image_layout = QVBoxLayout(image_group)
        
        # 图片操作按钮行
        image_buttons_layout = QHBoxLayout()
        self.add_image_button = QPushButton("添加图片")
        self.add_image_button.clicked.connect(self._add_image)
        self.clear_images_button = QPushButton("清除所有图片")
        self.clear_images_button.clicked.connect(self._clear_images)
        
        # 如果PIL不可用，禁用图片功能
        if not PIL_AVAILABLE:
            self.add_image_button.setEnabled(False)
            self.add_image_button.setToolTip("图片功能需要安装Pillow库")
            self.clear_images_button.setEnabled(False)
        
        image_buttons_layout.addWidget(self.add_image_button)
        image_buttons_layout.addWidget(self.clear_images_button)
        image_buttons_layout.addStretch()
        image_layout.addLayout(image_buttons_layout)
        
        # 图片预览区域
        self.image_scroll_area = QScrollArea()
        self.image_scroll_area.setWidgetResizable(True)
        self.image_scroll_area.setMaximumHeight(150)
        self.image_scroll_area.setMinimumHeight(50)
        
        self.image_preview_widget = QWidget()
        self.image_preview_layout = QHBoxLayout(self.image_preview_widget)
        self.image_preview_layout.setAlignment(Qt.AlignLeft)
        self.image_scroll_area.setWidget(self.image_preview_widget)
        
        image_layout.addWidget(self.image_scroll_area)
        
        # 图片状态标签
        self.image_status_label = QLabel("未选择图片")
        self.image_status_label.setStyleSheet("color: #888888; font-size: 9pt;")
        image_layout.addWidget(self.image_status_label)
        
        calldk_layout.addWidget(self.calldk_text)
        calldk_layout.addWidget(image_group)

        # 按钮区域
        button_layout = QHBoxLayout()

        # 提示词优化按钮
        self.optimize_button = QPushButton("⏳ 加载优化模块中... (Ctrl+Q)")
        self.optimize_button.clicked.connect(self._optimize_prompt)
        self.optimize_button.setEnabled(False)  # 初始状态禁用
        self.optimize_button.setToolTip("正在加载提示词优化模块，请稍候...")

        button_layout.addWidget(self.optimize_button)

        # 发送按钮
        submit_button = QPushButton("发送 (Ctrl+Enter)")
        submit_button.clicked.connect(self._submit_calldk)
        button_layout.addWidget(submit_button)

        button_layout.addStretch()  # 添加弹性空间
        calldk_layout.addLayout(button_layout)

        # 设置 calldk_group 的最小高度以容纳其内容
        # 这将基于5行的 calldk_text
        self.calldk_group.setMinimumHeight(self.calldk_text.minimumHeight() + submit_button.sizeHint().height() + calldk_layout.spacing() * 2 + calldk_layout.contentsMargins().top() + calldk_layout.contentsMargins().bottom() + 10) # 10为额外填充

        # 按特定顺序添加控件
        layout.addWidget(self.calldk_group)

        # 制作者/联系标签
        contact_label = QLabel('DK-Arthas')
        contact_label.setOpenExternalLinks(True)
        contact_label.setAlignment(Qt.AlignCenter)
        # 可选地，使字体稍小一些，不那么突出
        # contact_label_font = contact_label.font()
        # contact_label_font.setPointSize(contact_label_font.pointSize() - 1)
        # contact_label.setFont(contact_label_font)
        contact_label.setStyleSheet("font-size: 9pt; color: #cccccc;") # 深色主题的浅灰色
        layout.addWidget(contact_label)

    def _start_optimizer_loading(self):
        """启动异步加载提示词优化模块"""
        self.optimizer_loader_thread = OptimizerLoaderThread()
        self.optimizer_loader_thread.loaded.connect(self._on_optimizer_loaded)
        self.optimizer_loader_thread.start()

    def _on_optimizer_loaded(self, success: bool, message: str):
        """处理优化器加载完成事件"""
        if success:
            self.optimize_button.setText("🚀 提示词优化 (Ctrl+Q)")
            self.optimize_button.setEnabled(True)
            self.optimize_button.setToolTip("使用AI优化当前输入的提示词 (Ctrl+Q)")
        else:
            self.optimize_button.setText("❌ 优化不可用 (Ctrl+Q)")
            self.optimize_button.setEnabled(False)
            self.optimize_button.setToolTip(message)

        # 清理线程
        if self.optimizer_loader_thread:
            self.optimizer_loader_thread.deleteLater()
            self.optimizer_loader_thread = None

    # 移除了命令切换相关的方法

    # 移除了所有命令相关的方法

    def _add_image(self):
        """添加图片文件"""
        if not PIL_AVAILABLE:
            QMessageBox.warning(self, "错误", 
                              "图片功能需要Pillow库，但导入失败。\n\n"
                              "请检查控制台输出获取详细错误信息。\n\n"
                              "如果Pillow未安装，请运行: pip install pillow\n"
                              "如果已安装但仍有问题，请尝试: pip install --upgrade pillow")
            return
            
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("图片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.tiff)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            for file_path in file_paths:
                self._process_image_file(file_path)
    
    def _process_image_file(self, file_path: str):
        """处理单个图片文件"""
        try:
            # 检查文件大小（限制为10MB）
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                QMessageBox.warning(self, "文件过大", f"图片文件 {os.path.basename(file_path)} 超过10MB限制。")
                return

            # 获取文件格式
            file_format = os.path.splitext(file_path)[1].lower().replace('.', '')
            if not file_format:
                file_format = 'jpeg'  # 默认格式

            # 使用PIL打开图片
            with Image.open(file_path) as img:
                # 保持原始格式，只转换不支持的格式
                output_format = file_format
                mime_type = f'image/{file_format}'

                # 如果不是常见格式，转为PNG
                if file_format not in ('jpeg', 'jpg', 'png', 'gif', 'bmp', 'webp'):
                    output_format = 'png'
                    mime_type = 'image/png'

                # 保留原始尺寸，不压缩
                
                # 根据格式保存图片
                buffer = io.BytesIO()
                if output_format.lower() in ('jpg', 'jpeg'):
                    # JPEG不支持透明度，需要特殊处理
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(buffer, format='JPEG', quality=100)  # 使用最高质量
                else:
                    # 对于PNG等支持透明度的格式，保留原始模式
                    img.save(buffer, format=output_format.upper())

                img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

                # 创建图片数据对象
                image_data = ImageData(
                    filename=os.path.basename(file_path),
                    data=img_data,
                    mime_type=mime_type
                )
                
                self.selected_images.append(image_data)
                self._update_image_preview()
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理图片时出错: {str(e)}")
    
    def _clear_images(self):
        """清除所有图片"""
        self.selected_images.clear()
        self._update_image_preview()
    
    def _update_image_preview(self):
        """更新图片预览区域"""
        # 清除现有预览
        for widget in self.image_preview_widgets:
            widget.deleteLater()
        self.image_preview_widgets.clear()

        # 添加新的预览
        for i, image_data in enumerate(self.selected_images):
            preview_frame = QFrame()
            preview_frame.setFrameStyle(QFrame.Box)
            preview_frame.setMaximumSize(120, 100)
            preview_frame.setMinimumSize(120, 100)

            frame_layout = QVBoxLayout(preview_frame)
            frame_layout.setContentsMargins(5, 5, 5, 5)

            # 创建缩略图
            try:
                img_bytes = base64.b64decode(image_data['data'])
                img = Image.open(io.BytesIO(img_bytes))
                img.thumbnail((100, 70), Image.Resampling.LANCZOS)

                # 转换为QPixmap
                qt_img = ImageQt.ImageQt(img)
                pixmap = QPixmap.fromImage(qt_img)

                img_label = QLabel()
                img_label.setPixmap(pixmap)
                img_label.setAlignment(Qt.AlignCenter)
                img_label.setScaledContents(True)

                frame_layout.addWidget(img_label)
                
            except Exception:
                error_label = QLabel("预览失败")
                error_label.setAlignment(Qt.AlignCenter)
                frame_layout.addWidget(error_label)
            
            # 文件名标签
            name_label = QLabel(image_data['filename'])
            name_label.setWordWrap(True)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("font-size: 8pt;")
            frame_layout.addWidget(name_label)

            # 删除按钮
            remove_button = QPushButton("×")
            remove_button.setMaximumSize(20, 20)
            remove_button.clicked.connect(lambda _, idx=i: self._remove_image(idx))
            frame_layout.addWidget(remove_button)

            self.image_preview_layout.addWidget(preview_frame)
            self.image_preview_widgets.append(preview_frame)

        # 更新状态标签
        count = len(self.selected_images)
        if count == 0:
            self.image_status_label.setText("未选择图片")
        else:
            self.image_status_label.setText(f"已选择 {count} 张图片")
    
    def _remove_image(self, index: int):
        """删除指定索引的图片"""
        if 0 <= index < len(self.selected_images):
            self.selected_images.pop(index)
            self._update_image_preview()

    def _optimize_prompt(self):
        """优化提示词"""
        input_text = self.calldk_text.toPlainText().strip()

        if not input_text:
            QMessageBox.warning(self, "提示", "请先输入要优化的提示词")
            return

        if not OPTIMIZER_AVAILABLE:
            QMessageBox.warning(self, "错误", "提示词优化功能不可用，请检查相关依赖是否已安装")
            return

        # 禁用按钮，显示处理状态
        self.optimize_button.setEnabled(False)
        self.optimize_button.setText("🧠 优化中...")

        # 创建并启动优化线程
        self.optimize_thread = OptimizeThread(input_text)
        self.optimize_thread.finished.connect(self._on_optimize_finished)
        self.optimize_thread.error.connect(self._on_optimize_error)
        self.optimize_thread.start()

    def _on_optimize_finished(self, result: str):
        """优化完成回调"""
        # 保存原始文本用于撤销
        self.original_text_before_optimize = self.calldk_text.toPlainText()

        # 将优化结果替换到输入框
        self.calldk_text.setPlainText(result)

        # 恢复按钮状态
        self.optimize_button.setEnabled(True)
        self.optimize_button.setText("🚀 提示词优化 (Ctrl+Q)")

        # 显示状态提示（不弹窗）
        self.optimize_button.setToolTip("✅ 优化完成！按Ctrl+Z可撤销")

    def _on_optimize_error(self, error: str):
        """优化错误回调"""
        # 恢复按钮状态
        self.optimize_button.setEnabled(True)
        self.optimize_button.setText("🚀 提示词优化 (Ctrl+Q)")

        # 显示错误消息
        QMessageBox.critical(self, "优化失败", f"提示词优化失败：\n{error}")

    def _undo_optimize(self):
        """撤销提示词优化"""
        if hasattr(self, 'original_text_before_optimize') and self.original_text_before_optimize:
            # 恢复原始文本
            self.calldk_text.setPlainText(self.original_text_before_optimize)
            # 清空保存的原始文本
            self.original_text_before_optimize = ""
            # 更新按钮提示
            self.optimize_button.setToolTip("使用AI优化当前输入的提示词 (Ctrl+Q)")
        else:
            # 如果没有可撤销的内容，显示提示
            self.optimize_button.setToolTip("没有可撤销的优化操作")

    def _submit_calldk(self):
        self.calldk_result = CalldkResult(
            interactive_calldk=self.calldk_text.toPlainText().strip(),
            images=self.selected_images.copy()
        )
        self.close()

    # 移除了日志清除和配置保存方法

    def closeEvent(self, event):
        # 清理异步加载线程
        if self.optimizer_loader_thread and self.optimizer_loader_thread.isRunning():
            self.optimizer_loader_thread.quit()
            self.optimizer_loader_thread.wait(1000)  # 等待最多1秒

        # 为主窗口保存通用UI设置（几何形状、状态）
        self.settings.beginGroup("MainWindow_General")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.endGroup()
        super().closeEvent(event)

    def run(self) -> CalldkResult:
        self.show()
        QApplication.instance().exec()

        if not self.calldk_result:
            return CalldkResult(
                interactive_calldk="",
                images=[]
            )

        return self.calldk_result

def get_project_settings_group(project_dir: str) -> str:
    # 从项目目录路径创建安全、唯一的组名
    # 仅使用最后一个组件 + 完整路径的哈希值，以保持一定的可读性但唯一
    basename = os.path.basename(os.path.normpath(project_dir))
    full_hash = hashlib.md5(project_dir.encode('utf-8')).hexdigest()[:8]
    return f"{basename}_{full_hash}"

def calldk_ui(project_directory: str, prompt: str, output_file: Optional[str] = None) -> Optional[CalldkResult]:
    app = QApplication.instance() or QApplication()
    app.setPalette(get_dark_mode_palette(app))
    app.setStyle("Fusion")
    ui = CalldkUI(project_directory, prompt)
    result = ui.run()

    if output_file and result:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        # 将结果保存到输出文件
        with open(output_file, "w") as f:
            json.dump(result, f)
        return None

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the call dk UI")
    parser.add_argument("--project-directory", default=os.getcwd(), help="运行命令的项目目录")
    parser.add_argument("--prompt", default="我已实现您请求的更改。", help="显示给用户的提示信息")
    parser.add_argument("--output-file", help="保存call dk结果为JSON的路径")
    args = parser.parse_args()

    result = calldk_ui(args.project_directory, args.prompt, args.output_file)
    if result:
        print(f"\n收到的call dk:\n{result['interactive_calldk']}")
        if result['images']:
            print(f"\n附加图片: {len(result['images'])} 张")
            for i, img in enumerate(result['images']):
                print(f"  {i+1}. {img['filename']} ({img['mime_type']})")
    sys.exit(0)
