from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os


class FileSelector(Frame):
    """
    GUI element for selecting images to apply free_mark to
    """
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master

        self.base_dir = StringVar()
        self.files = []

        self.button_frame = Frame(self)
        self.folder_frame = Frame(self)

        self.files_view = Listbox(self, width=35, height=20)
        self.folder_entry = Entry(self.folder_frame, width=27,
                                  textvariable=self.base_dir)

        self.create_widgets()

    def create_widgets(self):
        """Create GUI elements"""
        pad_y = 1
        pad_x = 3
        button_width = 7
        Label(self, text="Images", font=14).pack()
        # List for files
        self.files_view.pack(pady=pad_y, padx=pad_x)

        # Folder entry field
        Label(self.folder_frame, text="Folder:").pack(side=LEFT)
        self.folder_entry.pack(side=RIGHT, pady=pad_y)

        # Button panel and error message
        Button(self.button_frame, text="Choose folder", width=button_width,
               command=self.fill_list).pack(side=LEFT, padx=pad_x)

        Button(self.button_frame, text="Choose file(s)", width=button_width,
               command=self.select_files).pack(side=LEFT)

        Button(self.button_frame, text="Clear files", width=button_width,
               command=self.clear_files).pack(side=RIGHT)

        Button(self.button_frame, text="Remove file", width=button_width,
               command=self.remove_item).pack(side=RIGHT, padx=pad_x)

        # Pack frames
        self.folder_frame.pack()
        self.button_frame.pack(pady=pad_y)

    def remove_item(self):
        """
        Delete selected item from the list view
        and copy files list from view
        """
        self.files_view.delete(ANCHOR)
        self.files = self.files_view.get(0, END)

    def prompt_directory(self):
        """Prompt the user for a base dir"""
        self.base_dir.set(filedialog.askdirectory())

    def select_files(self):
        file_types = [('Images', '*.JPEG;*.JPG;*.jpg;*.jpeg;*.png;*.bmp;*.tiff')]

        files = filedialog.askopenfilenames(title="Select images",
                                            filetypes=file_types)

        for _file in files:
            if _file not in self.files:
                self.files.append(_file)
        self.refresh_list()

    def refresh_list(self):
        self.files_view.delete(0, END)
        for _file in self.files:
            self.files_view.insert(END, _file)

    def clear_files(self):
        self.files = []
        self.refresh_list()
        self.base_dir.set('')

    def refresh_files(self):
        """Update files list"""
        self.files = []
        types = ['.PNG', '.JPG', 'JPEG', '.BMP', '.TIFF', '.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        try:
            for _file in os.listdir(self.base_dir.get()):
                if os.path.isfile(os.path.join(self.base_dir.get(), _file)):
                    for _type in types:
                        if _file.endswith(_type) and _file not in self.files:
                            self.files.append(_file)
                            # Stop when correct format is found.
                            break
        except FileNotFoundError:
            messagebox.showerror("Error", "Directory not found")
            return
        self.refresh_list()

    def fill_list(self):
        """Fill the list, by first asking the user to choose a directory
        and then loading all the files from the directory"""
        self.prompt_directory()
        self.refresh_files()

    def get_files(self):
        """Might as well go full java now that we're at it"""
        return self.files

    def get_file_paths(self):
        """Return path to files"""
        return [os.path.join(self.base_dir.get(), file) for file
                in self.get_files()]
                
    def get_current_file_path(self):
        """Return the path of the currently selected file, or empty string if none selected"""
        selected = self.files_view.curselection()
        if selected:
            selected_item = self.files_view.get(selected[0])
            # Check if the selected item is already a full path
            if os.path.isabs(selected_item) or '/' in selected_item or '\\' in selected_item:
                return selected_item
            else:
                # If it's just a filename, join it with the base directory
                return os.path.join(self.base_dir.get(), selected_item)
        return ""