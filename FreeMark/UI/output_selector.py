from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os
import re

from ..tools.errors import BadOptionError

NONE = 0
PRE = 1
SUFFIX = 2


class OutputSelector(Frame):
    """
    Class for selecting output destination and generating paths
    """
    def __init__(self, master=None):
        super().__init__(master)

        self.fix = StringVar()
        self.fix_position = IntVar()
        self.output_dir = StringVar()
        self.output_dir.set("Choose output folder")

        self.validate_pattern = re.compile(r'[<|>*:?"/\\]')

        self.entry_frame = Frame(self)
        self.fix_frame = Frame(self)
        self.radio_frame = Frame(self.fix_frame)
        self.create_widgets()

    def create_widgets(self):
        """
        Create and pack the TK widgets
        """
        Label(self, text="Output options", font=14).pack(anchor=W)

        Entry(self.entry_frame, width=50,
              textvariable=self.output_dir).pack(side=LEFT)
        Button(self.entry_frame, text="Choose folder",
               command=self.choose_dir).pack(side=LEFT, padx=10)
        self.entry_frame.pack(fill=X, pady=5)

        Label(self, text="Rename files").pack(anchor=W)

        Label(self.fix_frame, text="Fix: ").pack(side=LEFT)

        validate = (self.register(self.validate_fix), '%P')
        Entry(self.fix_frame, width=30, validate="key", validatecommand=validate,
              textvariable=self.fix).pack(side=LEFT, padx=5)
        # Me? I know who I am
        # I'm a frame playing a frame, disguised as another frame!
        Radiobutton(self.radio_frame, text="Postfix",
                    variable=self.fix_position, value=SUFFIX).pack(side=RIGHT)
        Radiobutton(self.radio_frame, text="Prefix",
                    variable=self.fix_position, value=PRE).pack(side=RIGHT)
        Radiobutton(self.radio_frame, text="None", variable=self.fix_position,
                    value=NONE).pack(side=RIGHT)
        self.radio_frame.pack(anchor=CENTER)
        self.fix_frame.pack(fill=X)

    def lock(self):
        """
        Lock down the output selector so the user doesn't mess with it
        while it's running
        """
        for child in (self.fix_frame.winfo_children()
                      + self.radio_frame.winfo_children()
                      + self.entry_frame.winfo_children()):
            try:
                child.config(state=DISABLED)
            except TclError:
                pass

    def unlock(self):
        """
        Opposite of lock
        """
        for child in (self.fix_frame.winfo_children()
                      + self.radio_frame.winfo_children()
                      + self.entry_frame.winfo_children()):
            try:
                child.config(state=NORMAL)
            except TclError:
                pass

    def validate_fix(self, fix_change):
        assert type(fix_change) == str, "Path must be a string"

        if re.search(self.validate_pattern, fix_change):
            return False

        return True

    def choose_dir(self):
        """
        Prompts the user to choose a folder.
        Bound to button next to folder entry
        """
        self.output_dir.set(filedialog.askdirectory())

    def get_dir(self):
        """
        Returns the currently selected dir
        """
        out_path = self.output_dir.get().rstrip().lstrip()

        if out_path.strip() == "":
            raise BadOptionError("Missing output location, please click the "
                                 "\"Choose Folder\" button")

        if not os.path.isabs(out_path):
            raise BadOptionError("Invalid output location, please click the "
                                 "\"Choose Folder\" button")

        if os.path.isdir(out_path):
            return out_path

        if messagebox.askyesno("Create folder",
                               "Folder doesn't exist, create it?"):
            try:
                os.makedirs(out_path)
            except OSError:
                raise BadOptionError("Invalid character in folder name.")
            return out_path
        else:
            raise BadOptionError("Output location doesn't exist.")

    def rename_file(self, filename, abs_path=False):
        """
        extract file name and apply suffix or prefix
        :param filename: file name or path
        :param abs_path: kwarg, true if filename isn't a filename but a path
        :return: 
        """
        if abs_path:
            filename = os.path.split(filename)[-1]

        if self.fix_position.get() == NONE:
            return filename
        elif self.fix_position.get() == PRE:
            return "{}_{}".format(self.fix.get(), filename)
        elif self.fix_position.get() == SUFFIX:
            filename = filename.rsplit('.', maxsplit=1)
            return "{}_{}.{}".format(filename[0], self.fix.get(), filename[1])

    def get_output_path(self, input_path, output_path):
        """
        Get output path from an input path
        :param input_path: path to original image
        :return: path to image destination
        """
        filename = self.rename_file(input_path, abs_path=True)
        return os.path.join(output_path, filename)
