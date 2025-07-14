from PIL import Image
import os
from FreeMark.tools.help import clamp
from FreeMark.tools.errors import BadOptionError


class WaterMarker:
    """Object for applying a free_mark to images"""
    def __init__(self, watermark_path, overwrite=False):
        self.overwrite = overwrite

        self.watermark_ratio = None
        self.watermark = None
        self.watermark_copy = None
        self.previous_size = None
        self.needs_opacity = None

        self.landscape_scale_factor = 0.15
        self.portrait_scale_factor = 0.30
        self.equal_scale_factor = 0.20
        self.min_scale = 0.5
        self.max_scale = 3

        # Prepare the watermarker
        try:
            self.watermark = Image.open(watermark_path)
        except FileNotFoundError:
            raise FileNotFoundError("Watermark not found, please click the "
                                    "\"Choose watermark\" button")
        except OSError:
            raise OSError("Watermark image is of incompatible type.")
        self.watermark_ratio = self.watermark.size[0] / self.watermark.size[1]

    def clean(self):
        """
        Forget the currently loaded free_mark
        """
        self.watermark_ratio = None
        self.watermark = None

    def apply_watermark(self, input_path, output_path, scale=True,
                        pos="SE", padding=((20, "px"), (5, "px")),
                        opacity=0.5):
        """
        Apply a free_mark to an image
        :param input_path: path to image on disk as a string
        :param output_path: save destination (path) as a string
        :param scale: Bool, scale free_mark
        :param opacity: free_mark opacity (a value between 0 and 1)
        :param pos: Assumes first char is y (N/S) and second is x (E/W)
        :param padding: padding in format ((x_pad, unit), (y_pad, unit))
        """
        # Don't overwrite existing files unless asked to
        if os.path.isfile(output_path) and not self.overwrite:
            return

        image = Image.open(input_path)

        if scale and \
                (not self.previous_size or self.previous_size != image.size):
            self.watermark_copy = self.scale_watermark(image)
            if opacity < 1:
                self.needs_opacity = True
            else:
                self.needs_opacity = False
        elif not self.watermark_copy:
            self.watermark_copy = self.watermark.copy()
            if opacity < 1:
                self.needs_opacity = True
            else:
                self.needs_opacity = False

        self.previous_size = image.size

        # Change free_mark opacity
        if self.needs_opacity:
            self.watermark_copy = self.change_opacity(self.watermark_copy,
                                                      opacity)
            self.needs_opacity = False

        position = self.get_watermark_position(image, self.watermark_copy,
                                               pos=pos, padding=padding)

        try:
            image.paste(self.watermark_copy, box=position,
                        mask=self.watermark_copy)
        except ValueError:
            image.paste(self.watermark_copy, box=position)
        image.save(output_path)

    def apply_watermark_preview(self, input_path, pos="SE", padding=((20, "px"), (5, "px")),
                               scale=True, opacity=0.5):
        """
        应用水印到图像并返回预览图像，但不保存
        :param input_path: 输入图像路径
        :param pos: 水印位置，第一个字符是y轴(N/S)，第二个是x轴(E/W)
        :param padding: 填充格式 ((x_pad, unit), (y_pad, unit))
        :param scale: 是否缩放水印
        :param opacity: 水印不透明度(0到1之间的值)
        :return: 带有水印的PIL图像对象
        """
        try:
            image = Image.open(input_path)
        except FileNotFoundError:
            raise BadOptionError("找不到输入图像文件")
        except OSError:
            raise BadOptionError("输入图像格式不兼容")

        watermark_copy = None
        if scale:
            watermark_copy = self.scale_watermark(image)
        else:
            watermark_copy = self.watermark.copy()

        # 改变水印不透明度
        if opacity < 1:
            watermark_copy = self.change_opacity(watermark_copy, opacity)

        position = self.get_watermark_position(image, watermark_copy,
                                              pos=pos, padding=padding)

        try:
            # 创建一个新的图像副本，以免修改原始图像
            preview_image = image.copy()
            preview_image.paste(watermark_copy, box=position,
                              mask=watermark_copy)
        except ValueError:
            preview_image = image.copy()
            preview_image.paste(watermark_copy, box=position)
        
        return preview_image

    @staticmethod
    def change_opacity(image, opacity):
        """
        Change opacity of an image.
        :param image: PIL image object.
        :param opacity: Opacity as a factor (number between 0.0 and 1.0)
        :return: Image with new opacity
        """
        assert 0.0 <= opacity <= 1.0, "opacity must be between 0 and 1"
        image = image.convert("RGBA")
        img_data = image.load()
        new_data = []

        width, height = image.size
        for y in range(height):
            for x in range(width):
                if img_data[x, y][3] > 5:
                    new_data.append((img_data[x, y][0],
                                     img_data[x, y][1],
                                     img_data[x, y][2],
                                     int(img_data[x, y][3]*opacity)))
                else:
                    new_data.append(img_data[x, y])

        image.putdata(new_data)
        return image

    def scale_watermark(self, image):
        """
        Get a scaled copy of the currently loaded free_mark,
        tries to scale it to from input image's size and orientation
        :param image: PIL image object that free_mark will be applied to
        :return: scaled copy of currently loaded free_mark as PIL image object
        """
        image_width, image_height = image.size

        # Calculate new free_mark size
        if image_width > image_height:
            # Scales the width of the free_mark based on the width of the image
            # while keeping within min/max values
            new_width = int(clamp(image_width * self.landscape_scale_factor,
                                  self.watermark.size[0] * self.min_scale,
                                  self.watermark.size[0] * self.max_scale))
        # Image is in the portrait position
        elif image_width < image_height:
            new_width = int(clamp(image_width * self.portrait_scale_factor,
                                  self.watermark.size[0] * self.min_scale,
                                  self.watermark.size[0] * self.max_scale))
        # Image is equal sided
        else:
            new_width = int(clamp(image_width * self.equal_scale_factor,
                                  self.watermark.size[0] * self.min_scale,
                                  self.watermark.size[0] * self.max_scale))

        # Determine height from new width and old height/width ratio
        new_height = int(new_width / self.watermark_ratio)

        # Apply it
        return self.watermark.copy().resize((new_width, new_height))

    @staticmethod
    def get_watermark_position(image, watermark, pos="SE",
                               padding=((20, "px"), (5, "px"))):
        """
        Calculate position to place the free_mark
        :param image: image object of image
        :param watermark: image object of free_mark
        :param pos: Assumes first char is y (N/S) and second is x (E/W)
        :param padding: padding in format ((x_pad, unit), (y_pad, unit))
        :return: (x, y) coordinates to place the upper left coordinates
        """
        # Change pos and make sure the right values were provided
        assert padding[0][1] and padding[1][1] in ["px", "%"], "unit must be px or %"
        pos = pos.upper().strip()
        assert pos[0] in ['N', 'S'], "first char of pos must be N or S"
        assert pos[1] in ['E', 'W'], "second char of pos must be E or W"

        # Get padding size
        if padding[0][1] == "%":
            padx = int(image.size[0] * (padding[0][0] / 100))
        else:
            padx = padding[0][0]

        if padding[1][1] == "%":
            pady = int(image.size[1] * (padding[1][0] / 100))
        else:
            pady = padding[1][0]

        if pos[0] == "S":
            y = image.size[1] - watermark.size[1] - pady
        else:
            y = pady
        if pos[1] == "E":
            x = image.size[0] - watermark.size[0] - padx
        else:
            x = padx
        return x, y