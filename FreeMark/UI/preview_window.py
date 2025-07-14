from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import os

from FreeMark.tools.watermarker import WaterMarker
from FreeMark.tools.errors import BadOptionError


class PreviewWindow(Toplevel):
    """
    预览窗口，显示带有水印的图像预览
    """
    def __init__(self, master, image_path, watermark_path, options):
        super().__init__(master)
        self.title("水印预览")
        self.geometry("800x600")
        self.minsize(400, 300)
        
        self.image_path = image_path
        self.watermark_path = watermark_path
        self.options = options
        
        self.preview_image = None
        self.photo = None
        
        self.create_widgets()
        self.generate_preview()
        
        # 使窗口居中，但等待窗口完全创建后再执行
        self.after_idle(self.center_window)
    
    def center_window(self):
        """将窗口居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def create_widgets(self):
        """创建预览窗口的GUI元素"""
        # 创建一个框架来容纳图像
        self.image_frame = Frame(self)
        self.image_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 创建一个标签来显示图像
        self.image_label = Label(self.image_frame)
        self.image_label.pack(fill=BOTH, expand=True)
        
        # 创建一个框架来容纳按钮
        self.button_frame = Frame(self)
        self.button_frame.pack(fill=X, padx=10, pady=10)
        
        # 创建关闭按钮
        self.close_button = Button(self.button_frame, text="关闭", command=self.destroy, width=10)
        self.close_button.pack(side=RIGHT, padx=5)
        
    def generate_preview(self):
        """生成预览图像"""
        try:
            # 创建一个临时的WaterMarker实例
            watermarker = WaterMarker(self.watermark_path)
            
            # 应用水印到图像，但不保存
            preview_img = watermarker.apply_watermark_preview(
                self.image_path,
                pos=self.options.get("pos"),
                padding=self.options.get("padding"),
                scale=self.options.get("scale"),
                opacity=self.options.get("opacity"),
                scale_x=self.options.get("scale_x", 1.0),
                scale_y=self.options.get("scale_y", 1.0)
            )
            
            # 调整图像大小以适应窗口
            self.display_image(preview_img)
            
        except BadOptionError as e:
            messagebox.showerror("预览错误", str(e))
            self.destroy()
        except Exception as e:
            messagebox.showerror("预览错误", f"生成预览时出错: {str(e)}")
            self.destroy()
    
    def display_image(self, img):
        """在窗口中显示图像"""
        # 获取窗口大小
        self.update_idletasks()
        window_width = self.image_frame.winfo_width()
        window_height = self.image_frame.winfo_height()
        
        # 如果窗口尚未完全初始化，使用默认大小
        if window_width <= 1 or window_height <= 1:
            window_width = 780
            window_height = 540
        
        # 计算缩放比例
        img_width, img_height = img.size
        scale_width = window_width / img_width
        scale_height = window_height / img_height
        scale = min(scale_width, scale_height)
        
        # 如果图像小于窗口，不需要缩放
        if scale >= 1:
            resized_img = img
        else:
            # 缩放图像
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # 转换为PhotoImage并显示
        self.photo = ImageTk.PhotoImage(resized_img)
        self.image_label.config(image=self.photo)
        
        # 保存对图像的引用，防止被垃圾回收
        self.preview_image = resized_img