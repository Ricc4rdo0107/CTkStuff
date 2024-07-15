import PIL
import base64
from io import BytesIO
from typing import Any, Callable, Tuple
import customtkinter as ctk
from customtkinter import CTkImage

RIGHT_ARROW_64_ICON = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAL1JREFUWEfV1+EKgCAMBOB88715IVRImNtud0H9TbyPOc3a5jxmtl9DzKx547PvlxOO4SrEK2AWrkBAgA5hLQcMYCHSPfBssmol3K5e9QKjJ1zAWep7K75tM7QSIYASEQaoECmAApEGsBEQgImAASxECcBAlAFVxP8B1aO6VIFqeF8+GMAIhwGscAjADE8D2OEpgCI8DFCFhwDKcBegDl8CvggvAdBL6PNSC/0XsMLdHph9apnhIcCIYIf3uQ9w54AhxEd3ZwAAAABJRU5ErkJggg=='


def base64_to_pil_image(base64_str: bytes, resize:tuple =None, to_ctk_image: bool=False) -> CTkImage|PIL.Image.Image:
    image_data = base64.b64decode(base64_str)
    image = PIL.Image.open(BytesIO(image_data))
    if resize:
        image.resize(resize, PIL.Image.LANCZOS)
    if to_ctk_image:
        image = CTkImage(image)
    return image

RIGHT_ARROW_IMAGE = base64_to_pil_image(RIGHT_ARROW_64_ICON)
UP_ARROW_ICON     = ctk.CTkImage(RIGHT_ARROW_IMAGE.rotate(90, PIL.Image.NEAREST, expand=1))
DOWN_ARROW_ICON   = ctk.CTkImage(RIGHT_ARROW_IMAGE.rotate(270,PIL.Image.NEAREST, expand=1))

class CTkInputPopup(ctk.CTkToplevel):
    def __init__(self, title: str, text: str, centered: bool=False, titlebar: bool = True, *args,  fg_color: str | Tuple[str] | None = None, **kwargs):
        super().__init__(*args, fg_color=fg_color, **kwargs)
        self._text = text
        self._title = title
        
        self.title(self._title)

        self._font = ("Roboto", 15)

        self.lift()
        self.attributes("-topmost", True)
        self._winsize = (300, 127.5)

        if not titlebar:
            self.overrideredirect(1)

        if centered:
            screen_size = self.winfo_screenwidth(), self.winfo_screenheight()
            x, y = screen_size[0]//2, screen_size[1]//2
            self.geometry(f"{x}+{y}")
        self.geometry(f"{self._winsize[0]}x{self._winsize[1]}")


        self.after(10, self._create_widgets)
        self.resizable(False, False)
        self.grab_set()

    def _on_exit(self, event):
        self._input = self._entry.get().strip()
        self.destroy()


    def _create_widgets(self):
        self._label = ctk.CTkLabel(self, text=self._text, font=self._font)
        self._entry = ctk.CTkEntry(self, font=self._font)

        self._label.pack(fill="x", expand=1, padx=12, pady=12)
        self._entry.pack(fill="x", expand=1, padx=12, pady=12)
        self._entry.bind("<Return>", self._on_exit)

    def get_input(self):
        self.wait_window()
        return self._input
        

class CTkArrowOpeningMenu(ctk.CTkFrame):
    def __init__(self, master: Any, width: int = 200, height: int = 200, corner_radius: int | str | None = None, border_width: int | str | None = None, bg_color: str | Tuple[str] = "transparent", fg_color: str | Tuple[str] | None = None, border_color: str | Tuple[str] | None = None, background_corner_colors: Tuple[str | Tuple[str]] | None = None, overwrite_preferred_drawing_method: str | None = None, **kwargs):
        """
        use CTkArrowOpeningMenu.widgetsFrame as master
        """
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        
        self.UP_ARROW_ICON   = UP_ARROW_ICON
        self.DOWN_ARROW_ICON = DOWN_ARROW_ICON

        self.rowconfigure((0, 1), weight=1)
        self.columnconfigure(0, weight=1)

        self.widgetsFrame = ctk.CTkFrame(self, bg_color="transparent")
        self.widgets = []

        self.arrow = ctk.CTkLabel(self, text="", image=DOWN_ARROW_ICON)
        self.arrow.bind("<Button-1>", self.toggle_menu)
        self.arrow.grid(row=1, column=0)

        global menuOpen
        menuOpen = False

    def toggle_menu(self, event):
        global menuOpen
        menuOpen = not(menuOpen)
        if menuOpen:
            children = self.widgetsFrame.winfo_children()
            num_widgets = len(children)
            if num_widgets:
                self.widgetsFrame.grid(row=0, column=0)
            self.arrow.configure(image=self.UP_ARROW_ICON)
        else:
            self.widgetsFrame.grid_forget()
            self.arrow.configure(image=self.DOWN_ARROW_ICON)


class CTkFloatingMenu(ctk.CTkToplevel):
    def __init__(self, master, winsize: tuple=(100,140), on_death:Callable=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        """
        If you want to set this as master you should call it 
        """
        self.master = master
        self.winsize = winsize
        self.overrideredirect(1)

        self.screensize: tuple[int, int] = (self.master.winfo_screenwidth(), self.master.winfo_screenheight())

        self.on_death = on_death
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.BigFrame = ctk.CTkFrame(self)
        self.BigFrame.rowconfigure(0, weight=1)
        self.BigFrame.columnconfigure(0, weight=1)
        self.BigFrame.grid(row=0, column=0, sticky="nsew")
        self.buttons = []
        self.bind("<FocusOut>", self.on_focus_out)

    def destroy_custom(self):
        if self.on_death:
            self.on_death()
        return super().destroy()

    def on_focus_out(self, event):
        self.destroy_custom()

    def quit_and_execute(self, function: Callable):
        self.destroy()
        function()

    def add_option(self, text, command) -> None:
        button = ctk.CTkButton(self.BigFrame, text=text, fg_color="#2b2b2b", hover_color="#3d3d3d",  border_color="black")
        button.pack(fill="x")
        button.bind("<Button-1>", command=lambda x=None: self.quit_and_execute(command))
        self.buttons.append(button)
        return text
        
    def popup(self, x, y):
        self.winsize = (150, 32*len(self.buttons))

        if y > self.screensize[1]-self.winsize[1]:
            y-=self.winsize[1]

        elif y <= self.winsize[1]:
            y += self.winsize[1]/2

        elif x <= self.winsize[0]:
            x += self.winsize[0]/2

        elif x > self.screensize[0]-self.winsize[0]:
            x-=self.winsize[0]

        self.geometry(f"{self.winsize[0]}x{self.winsize[1]-20}+{x}+{y}")
        self.mainloop()

