from tkinter import *
from tkinter import messagebox

from FreeMark.UI.output_selector import OutputSelector
from FreeMark.UI.watermark_selector import WatermarkSelector
from FreeMark.UI.watermark_options import WatermarkOptions
from FreeMark.UI.preview_window import PreviewWindow


class OptionsPane(Frame):
    """
    Frame for holding all the options elements, is also used as an interface
    to supply the worker with settings and services
    """
    def __init__(self, master=None):
        super().__init__(master)

        self.file_selector = None
        self.output_selector = OutputSelector(self)
        self.watermark_selector = WatermarkSelector(self)
        self.watermark_options = WatermarkOptions(self)
        self.create_widgets()
        
    def set_file_selector(self, file_selector):
        """
        Set the file selector instance to access selected files
        :param file_selector: FileSelector instance
        """
        self.file_selector = file_selector

    def create_widgets(self):
        """Create the graphical element"""
        pady = 5
        Label(self, text="Settings", font=14).pack(anchor=N)
        self.watermark_selector.pack(fill=X, pady=pady, anchor=N)
        self.watermark_options.pack(fill=X, pady=pady, anchor=N)
        self.output_selector.pack(fill=X, anchor=N)

    def get_watermark_path(self):
        """
        Get path to the currently selected free_mark
        :return: path to free_mark as string
        """
        return self.watermark_selector.get_path()

    def get_output_path(self):
        return self.output_selector.get_dir()

    def create_output_path(self, input_path, output_path):
        return self.output_selector.get_output_path(input_path, output_path)

    def get_watermark_pos(self):
        return self.watermark_options.position.get()

    def get_padding(self):
        return (int(self.watermark_options.padx.get()), self.watermark_options.unit_x.get()), \
               (int(self.watermark_options.pady.get()), self.watermark_options.unit_y.get())

    def get_opacity(self):
        return self.watermark_options.opacity.get()/100
        
    def preview_watermark(self):
        """
        Preview the watermark on the selected image
        """
        if self.file_selector is None:
            messagebox.showerror("错误", "无法访问文件选择器")
            return
            
        selected_files = self.file_selector.get_current_file_path()
        if not selected_files:
            messagebox.showinfo("提示", "请先选择一个图像文件")
            return
            
        # Use the first selected file for preview
        image_path = selected_files
        
        watermark_path = self.get_watermark_path()
        if not watermark_path:
            messagebox.showinfo("提示", "请先选择一个水印图像")
            return
            
        # Get watermark options
        options = {
            "pos": self.get_watermark_pos(),
            "padding": self.get_padding(),
            "opacity": self.get_opacity(),
            "scale_x": self.watermark_options.scale_x.get(),
            "scale_y": self.watermark_options.scale_y.get()
        }
        
        # Create preview window
        preview = PreviewWindow(self, image_path, watermark_path, options)