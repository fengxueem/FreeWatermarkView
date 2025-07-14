from tkinter import *
# tkinter OptionMenu is hella ugly so use ttk
from tkinter.ttk import OptionMenu


class WatermarkOptions(Frame):

    def __init__(self, master=None):
        super().__init__(master)

        self.position = StringVar()
        self.position.set("SE")

        self.padx = StringVar()
        self.pady = StringVar()
        self.unit_x = StringVar()
        self.unit_y = StringVar()
        self.padx.set(20)
        self.pady.set(5)
        # ttk is super weird and demands that the first option is left blank
        self.unit_options = ["", "px", "%"]
        self.unit_x.set(self.unit_options[1])
        self.unit_y.set(self.unit_options[1])

        # 水印缩放相关变量
        # 新增：横向和纵向缩放比例
        self.scale_x = DoubleVar()
        self.scale_y = DoubleVar()
        self.scale_x.set(1.0)
        self.scale_y.set(1.0)
        
        # 新增：是否保持横纵比例一致
        self.keep_aspect_ratio = BooleanVar()
        self.keep_aspect_ratio.set(True)

        self.opacity = IntVar()
        self.opacity.set(100)

        self.create_widgets()

    def create_widgets(self):
        padx = 5
        pady = 5
        Label(self, text="Watermark options", font=14).pack(anchor=W)

        # --------- Position options ---------
        pos_options = Frame(self)
        Label(pos_options, text="Position").pack(anchor=W)

        # -- Padding --
        validate = (self.register(self.validate_int), '%P')
        padding_frame = Frame(pos_options)
        # Horizontal padding
        Label(padding_frame, text="Pad x").grid(column=0, row=0)
        Entry(padding_frame, textvariable=self.padx, validate="key", width=5,
              validatecommand=validate).grid(column=1, row=0, padx=padx)
        OptionMenu(padding_frame, self.unit_x,
                   *self.unit_options).grid(column=3, row=0)

        # Vertical padding
        Label(padding_frame, text="Pad y").grid(column=0, row=1)
        Entry(padding_frame, textvariable=self.pady, validate="key", width=5,
              validatecommand=validate).grid(column=1, row=1,
                                             padx=padx, pady=pady)
        OptionMenu(padding_frame, self.unit_y,
                   *self.unit_options).grid(column=3, row=1)

        padding_frame.pack(side=LEFT)

        pos_frame = Frame(pos_options)
        radio_pad = 5
        # -- Position --
        Radiobutton(pos_frame, text="Top left", variable=self.position,
                    value="NW").grid(column=0, row=0, sticky=W,
                                     padx=radio_pad, pady=radio_pad)

        Radiobutton(pos_frame, text="Top right", variable=self.position,
                    value="NE").grid(column=1, row=0, sticky=W,
                                     padx=radio_pad, pady=radio_pad)

        Radiobutton(pos_frame, text="Bottom left", variable=self.position,
                    value="SW").grid(column=0, row=1,
                                     padx=radio_pad, pady=radio_pad)

        Radiobutton(pos_frame, text="Bottom right", variable=self.position,
                    value="SE").grid(column=1, row=1,
                                     padx=radio_pad, pady=radio_pad)
        pos_frame.pack(side=LEFT, padx=30)

        pos_options.pack(anchor=W)

        # ---------- Opacity options ---------
        Label(self, text="Opacity and size").pack(anchor=W)

        opacity_frame = Frame(self)
        Label(opacity_frame, text="Opacity").pack(side=LEFT, anchor=S)

        self.opacity_slider = Scale(opacity_frame, from_=0, to=100, orient=HORIZONTAL,
              variable=self.opacity)
        self.opacity_slider.pack(side=LEFT, anchor=N, padx=5, fill=X, expand=True)

        Entry(opacity_frame, textvariable=self.opacity, width=4,
              validate="key", validatecommand=validate).pack(side=LEFT,
                                                             anchor=S, pady=3)

        Label(opacity_frame, text="%").pack(side=LEFT, anchor=S, pady=3)
        opacity_frame.pack(anchor=W, fill=X)

        # ----------- Size options -----------
        # 保持横纵比例一致的复选框和预览按钮
        aspect_ratio_frame = Frame(self)
        Checkbutton(aspect_ratio_frame, text="Keep aspect ratio",
                    variable=self.keep_aspect_ratio,
                    command=self.update_aspect_ratio,
                    onvalue=True, offvalue=False).pack(side=LEFT)
        
        # 添加预览按钮到Keep aspect ratio的右边
        self.preview_button = Button(aspect_ratio_frame, text="Preview", 
                                    command=self.master.preview_watermark)
        self.preview_button.pack(side=LEFT, padx=10)
        
        aspect_ratio_frame.pack(anchor=W, pady=(5, 0), fill=X)
        
        # 横向缩放比例滑块
        scale_x_frame = Frame(self)
        Label(scale_x_frame, text="Scale x:").pack(side=LEFT)
        self.scale_x_slider = Scale(scale_x_frame, from_=0.1, to=3.0, 
                                   orient=HORIZONTAL, resolution=0.01,
                                   variable=self.scale_x, 
                                   command=self.on_scale_x_change)
        self.scale_x_slider.pack(side=LEFT, fill=X, expand=True)
        self.scale_x_label = Label(scale_x_frame, text="1.00x")
        self.scale_x_label.pack(side=LEFT, padx=5)
        scale_x_frame.pack(anchor=W, pady=(5, 0), fill=X)
        
        # 纵向缩放比例滑块
        scale_y_frame = Frame(self)
        Label(scale_y_frame, text="Scale y:").pack(side=LEFT)
        self.scale_y_slider = Scale(scale_y_frame, from_=0.1, to=3.0, 
                                   orient=HORIZONTAL, resolution=0.01,
                                   variable=self.scale_y, 
                                   command=self.on_scale_y_change)
        self.scale_y_slider.pack(side=LEFT, fill=X, expand=True)
        self.scale_y_label = Label(scale_y_frame, text="1.00x")
        self.scale_y_label.pack(side=LEFT, padx=5)
        scale_y_frame.pack(anchor=W, pady=(5, 0), fill=X)

    @staticmethod
    def validate_int(number):
        try:
            int(number)
        except ValueError:
            if len(number.strip()) == 0:
                # Allow the field to be empty
                return True
            return False
        else:
            return True
            
    def toggle_scale_options(self):
        """启用或禁用缩放选项"""
        state = "normal" if self.scale_watermark.get() else "disabled"
        self.scale_x_slider.config(state=state)
        self.scale_y_slider.config(state=state)
        
    def update_aspect_ratio(self):
        """更新横纵比例"""
        if self.keep_aspect_ratio.get():
            # 如果启用了保持横纵比例，则将纵向缩放设置为与横向缩放相同
            self.scale_y.set(self.scale_x.get())
            self.scale_y_label.config(text=f"{self.scale_y.get():.2f}x")
            
    def on_scale_x_change(self, value):
        """处理横向缩放滑块的变化"""
        # 更新标签显示
        self.scale_x_label.config(text=f"{float(value):.2f}x")
        
        # 如果启用了保持横纵比例，则同步纵向缩放
        if self.keep_aspect_ratio.get():
            self.scale_y.set(float(value))
            self.scale_y_label.config(text=f"{float(value):.2f}x")
            
    def on_scale_y_change(self, value):
        """处理纵向缩放滑块的变化"""
        # 更新标签显示
        self.scale_y_label.config(text=f"{float(value):.2f}x")
        
        # 如果启用了保持横纵比例，则同步横向缩放
        if self.keep_aspect_ratio.get():
            self.scale_x.set(float(value))
            self.scale_x_label.config(text=f"{float(value):.2f}x")