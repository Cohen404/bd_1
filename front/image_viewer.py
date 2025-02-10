from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QDialog
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QImage, QPainter
import logging  # 添加日志模块导入

class ImageViewer(QDialog):
    """
    图片查看器对话框
    支持图片放大、缩小、拖拽功能
    """
    def __init__(self, parent=None):
        """
        初始化图片查看器
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """
        初始化UI界面
        """
        # 设置窗口标题和大小
        self.setWindowTitle('图片查看')
        self.resize(800, 600)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建图片显示区域
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # 添加图片显示区域到布局
        layout.addWidget(self.view)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建放大、缩小、重置按钮
        self.zoom_in_btn = QPushButton('放大')
        self.zoom_out_btn = QPushButton('缩小')
        self.reset_btn = QPushButton('重置')
        self.save_btn = QPushButton('保存')
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #5c8ac3;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #759dcd;
            }
        """
        self.zoom_in_btn.setStyleSheet(button_style)
        self.zoom_out_btn.setStyleSheet(button_style)
        self.reset_btn.setStyleSheet(button_style)
        self.save_btn.setStyleSheet(button_style)
        
        # 添加按钮到布局
        button_layout.addWidget(self.zoom_in_btn)
        button_layout.addWidget(self.zoom_out_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.save_btn)
        
        # 添加按钮布局到主布局
        layout.addLayout(button_layout)
        
        # 连接信号和槽
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.reset_btn.clicked.connect(self.reset_view)
        self.save_btn.clicked.connect(self.save_image)
        
        # 初始化缩放系数
        self.zoom_factor = 1.0
        
    def set_image(self, image):
        """
        设置要显示的图片
        
        Args:
            image: QImage或QPixmap对象
        """
        try:
            # 清除当前场景
            self.scene.clear()
            
            # 转换图片为QPixmap
            if isinstance(image, QImage):
                pixmap = QPixmap.fromImage(image)
            elif isinstance(image, QPixmap):
                pixmap = image
            else:
                raise ValueError("不支持的图片格式")
            
            # 添加图片到场景
            self.scene.addPixmap(pixmap)
            self.scene.setSceneRect(QRectF(pixmap.rect()))
            
            # 重置视图
            self.reset_view()
            
        except Exception as e:
            import traceback
            print(f"设置图片时发生错误: {str(e)}")
            print(traceback.format_exc())
            
    def zoom_in(self):
        """
        放大图片
        """
        self.zoom_factor *= 1.2
        self.view.scale(1.2, 1.2)
        
    def zoom_out(self):
        """
        缩小图片
        """
        self.zoom_factor /= 1.2
        self.view.scale(1/1.2, 1/1.2)
        
    def reset_view(self):
        """
        重置视图到原始大小
        """
        # 重置变换
        self.view.resetTransform()
        self.zoom_factor = 1.0
        
        # 调整视图以适应场景
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        
    def save_image(self):
        """
        保存图片到本地
        """
        from PyQt5.QtWidgets import QFileDialog
        try:
            # 获取场景中的第一个图片项
            items = self.scene.items()
            if not items:
                logging.warning("没有找到要保存的图片项")
                return
                
            pixmap_item = items[0]
            if not hasattr(pixmap_item, 'pixmap'):
                logging.warning("图片项不包含pixmap属性")
                return
                
            # 打开文件保存对话框
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存图片",
                "",
                "图片文件 (*.png *.jpg *.bmp);;所有文件 (*.*)"
            )
            
            if file_path:
                # 保存图片
                success = pixmap_item.pixmap().save(file_path)
                if success:
                    logging.info(f"图片已成功保存到: {file_path}")
                else:
                    logging.error(f"保存图片失败: {file_path}")
                
        except Exception as e:
            import traceback
            error_msg = f"保存图片时发生错误: {str(e)}"
            logging.error(error_msg)
            logging.error(traceback.format_exc())
            print(error_msg)
            print(traceback.format_exc()) 