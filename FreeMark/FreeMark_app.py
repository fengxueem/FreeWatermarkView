from tkinter import *
from time import time
from tkinter import messagebox

from FreeMark.UI.file_selector import FileSelector
from FreeMark.UI.options_pane import OptionsPane
from FreeMark.UI.preview_window import PreviewWindow
from FreeMark.UI.worker import Worker


class FreeMarkApp(Frame):
    """
    Top most frame of the application, represents the 'app'
    brings together all the other major pieces, which in turn brings together 
    the smaller pieces
    """
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.preview_window = None
        self.last_update = 0
        
        self.create_widgets()
        
        # 创建预览窗口
        self.create_preview_window()
        
        # Bind window close event
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_preview_window(self):
        """创建预览窗口"""
        try:
            # 直接创建预览窗口实例，让PreviewWindow类自己创建Toplevel窗口
            self.preview_window = PreviewWindow(self.master, "", "", {})
            
            # 设置预览窗口的位置
            self.master.update_idletasks()
            main_x = self.master.winfo_x()
            main_y = self.master.winfo_y()
            main_width = self.master.winfo_width()
            
            # 将预览窗口放在主窗口的右侧
            self.preview_window.window.geometry(f"+{main_x + main_width + 10}+{main_y}")
            
            # 绑定关闭事件
            self.preview_window.window.protocol("WM_DELETE_WINDOW", self.on_preview_close)
        except Exception as e:
            print(f"创建预览窗口时出错: {e}")
    
    def on_preview_close(self):
        """处理预览窗口关闭事件"""
        if self.preview_window:
            self.preview_window.window.withdraw()  # 隐藏而不是销毁
    
    def on_close(self):
        """Handle window closing"""
        if self.preview_window:
            self.preview_window.window.destroy()
        self.master.destroy()

    def update_preview(self, *args):
        """更新预览窗口"""
        # 限制更新频率，避免过于频繁的更新
        current_time = time() * 1000  # 转换为毫秒
        if hasattr(self, 'last_update') and current_time - self.last_update < 300:
            return
            
        self.last_update = current_time
        
        # 检查预览窗口是否存在
        if not self.preview_window or not self.preview_window.window.winfo_exists():
            self.create_preview_window()
            
        try:
            # 获取当前选择的文件
            selected_file = self.file_selector.get_current_file_path()
            if not selected_file:
                return
                
            # 获取水印设置
            watermark_path = self.options_pane.get_watermark_path()
            if not watermark_path:
                return
                
            # 获取水印选项
            options = {
                "pos": self.options_pane.get_watermark_pos(),
                "padding": self.options_pane.get_padding(),
                "opacity": self.options_pane.get_opacity(),
                "scale_x": self.options_pane.watermark_options.scale_x.get(),
                "scale_y": self.options_pane.watermark_options.scale_y.get()
            }
            
            # 更新预览
            self.preview_window.update_preview(selected_file, watermark_path, options)
            
            # 确保预览窗口可见
            self.preview_window.window.deiconify()
            
        except Exception as e:
            print(f"更新预览时出错: {e}")

    def create_widgets(self):
        """Create the GUI elements"""
        # Label(self.master, text='FreeMark', font=16).pack(pady=pad_y)

        # Create listbox for files
        options_frame = Frame(self.master)
        self.file_selector = FileSelector(options_frame)
        self.options_pane = OptionsPane(options_frame)

        # Set file_selector to options_pane
        self.options_pane.set_file_selector(self.file_selector)
        
        # 绑定所有选项变化到预览更新
        self.options_pane.bind_all_options(self.update_preview)
        
        # 绑定文件选择变化到预览更新
        self.file_selector.files_view.bind('<<ListboxSelect>>', self.update_preview)
        
        self.file_selector.pack(side=LEFT, padx=(2, 5))
        self.options_pane.pack(side=RIGHT, fill=Y, pady=10)

        options_frame.pack()

        worker = Worker(self.file_selector, self.options_pane)
        worker.pack()