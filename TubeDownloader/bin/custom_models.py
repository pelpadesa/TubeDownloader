from customtkinter import CTkComboBox
from customtkinter.windows.widgets.core_widget_classes.dropdown_menu import DropdownMenu
from customtkinter.windows.widgets.font import CTkFont
from customtkinter.windows.widgets.core_rendering import CTkCanvas, DrawEngine
from customtkinter.windows.widgets.theme import ThemeManager
from customtkinter.windows.widgets.scaling import CTkScalingBaseClass
from customtkinter.windows.widgets.appearance_mode import CTkAppearanceModeBaseClass
from typing import Union, Tuple, Callable, List, Optional
import tkinter
import sys


# Fixing readonly hover
class custom_CTkComboBox(CTkComboBox):
    def __init__(self,
                 master: any,
                 width: int = 140,
                 height: int = 28,
                 corner_radius: Optional[int] = None,
                 border_width: Optional[int] = None,

                 bg_color: Union[str, Tuple[str, str]] = "transparent",
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 border_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 dropdown_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 dropdown_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 dropdown_text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color_disabled: Optional[Union[str, Tuple[str, str]]] = None,

                 font: Optional[Union[tuple, CTkFont]] = None,
                 dropdown_font: Optional[Union[tuple, CTkFont]] = None,
                 values: Optional[List[str]] = None,
                 state: str = tkinter.NORMAL,
                 hover: bool = True,
                 variable: Union[tkinter.Variable, None] = None,
                 command: Union[Callable[[str], None], None] = None,
                 justify: str = "left",
                 **kwargs
            ):

        # transfer basic functionality (_bg_color, size, __appearance_mode, scaling) to CTkBaseClass
        super().__init__(master=master, bg_color=bg_color, width=width, height=height, **kwargs)

        # shape
        self._corner_radius = ThemeManager.theme["CTkComboBox"]["corner_radius"] if corner_radius is None else corner_radius
        self._border_width = ThemeManager.theme["CTkComboBox"]["border_width"] if border_width is None else border_width

        # color
        self._fg_color = ThemeManager.theme["CTkComboBox"]["fg_color"] if fg_color is None else self._check_color_type(fg_color)
        self._border_color = ThemeManager.theme["CTkComboBox"]["border_color"] if border_color is None else self._check_color_type(border_color)
        self._button_color = ThemeManager.theme["CTkComboBox"]["button_color"] if button_color is None else self._check_color_type(button_color)
        self._button_hover_color = ThemeManager.theme["CTkComboBox"]["button_hover_color"] if button_hover_color is None else self._check_color_type(button_hover_color)
        self._text_color = ThemeManager.theme["CTkComboBox"]["text_color"] if text_color is None else self._check_color_type(text_color)
        self._text_color_disabled = ThemeManager.theme["CTkComboBox"]["text_color_disabled"] if text_color_disabled is None else self._check_color_type(text_color_disabled)

        # font
        self._font = CTkFont() if font is None else self._check_font_type(font)
        if isinstance(self._font, CTkFont):
            self._font.add_size_configure_callback(self._update_font)

        # callback and hover functionality
        self._command = command
        self._variable = variable
        self._state = state
        self._hover = hover

        if values is None:
            self._values = ["CTkComboBox"]
        else:
            self._values = values

        self.dropdown_fg_color = dropdown_fg_color
        self.dropdown_hover_color = dropdown_hover_color
        self.dropdown_text_color = dropdown_text_color
        self.dropdown_font = dropdown_font
        
        self.regenDropdown()

        # configure grid system (1x1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._canvas = CTkCanvas(master=self,
                                 highlightthickness=0,
                                 width=self._apply_widget_scaling(self._desired_width),
                                 height=self._apply_widget_scaling(self._desired_height))
        self.draw_engine = DrawEngine(self._canvas)

        self._entry = tkinter.Entry(master=self,
                                    state=self._state,
                                    width=1,
                                    bd=0,
                                    justify=justify,
                                    highlightthickness=0,
                                    font=self._apply_font_scaling(self._font),
                                    cursor="hand2")
        self._entry.bind("<1>", self._clicked)

        self._create_grid()
        self._create_bindings()
        self._draw()  # initial draw

        if self._variable is not None:
            self._entry.configure(textvariable=self._variable)

        # insert default value
        if len(self._values) > 0:
            self._entry.insert(0, self._values[0])
        else:
            self._entry.insert(0, "CTkComboBox")

    def _on_enter(self, event=0):
        if self._hover is True and len(self._values) > 0:
            if sys.platform == "darwin" and len(self._values) > 0 and self._cursor_manipulation_enabled:
                self._canvas.configure(cursor="pointinghand")
            elif sys.platform.startswith("win") and len(self._values) > 0 and self._cursor_manipulation_enabled:
                self._canvas.configure(cursor="hand2")

            # set color of inner button parts to hover color
            self._canvas.itemconfig("inner_parts_right",
                                    outline=self._apply_appearance_mode(self._button_hover_color),
                                    fill=self._apply_appearance_mode(self._button_hover_color))
            self._canvas.itemconfig("border_parts_right",
                                    outline=self._apply_appearance_mode(self._button_hover_color),
                                    fill=self._apply_appearance_mode(self._button_hover_color))
    def _clicked(self, event=None):
        if self._state is not tkinter.DISABLED and len(self._values) > 0:
            if self._dropdown_menu.isopen == False:
                self._dropdown_menu.isopen = True
                self._open_dropdown_menu()
            else:
                self._dropdown_menu.isopen = False
                self._dropdown_menu.destroy()
                self.regenDropdown()
    def _on_leave(self, event=0):
        if sys.platform == "darwin" and len(self._values) > 0 and self._cursor_manipulation_enabled:
            self._canvas.configure(cursor="arrow")
        elif sys.platform.startswith("win") and len(self._values) > 0 and self._cursor_manipulation_enabled:
            self._canvas.configure(cursor="arrow")

        # set color of inner button parts
        self._canvas.itemconfig("inner_parts_right",
                                outline=self._apply_appearance_mode(self._button_color),
                                fill=self._apply_appearance_mode(self._button_color))
        self._canvas.itemconfig("border_parts_right",
                                outline=self._apply_appearance_mode(self._button_color),
                                fill=self._apply_appearance_mode(self._button_color))
    def regenDropdown(self):
        self._dropdown_menu = custom_DropdownMenu(master=self,
            values=self._values,
            command=self._dropdown_callback,
            fg_color=self.dropdown_fg_color,
            hover_color=self.dropdown_hover_color,
            text_color=self.dropdown_text_color,
            font=self.dropdown_font)

class custom_DropdownMenu(DropdownMenu):
    def __init__(self, *args,
                 min_character_width: int = 18,

                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color: Optional[Union[str, Tuple[str, str]]] = None,

                 font: Optional[Union[tuple, CTkFont]] = None,
                 command: Union[Callable, None] = None,
                 values: Optional[List[str]] = None,
                 **kwargs):

        # call init methods of super classes
        tkinter.Menu.__init__(self, *args, **kwargs)
        CTkAppearanceModeBaseClass.__init__(self)
        CTkScalingBaseClass.__init__(self, scaling_type="widget")

        self.isopen = False
        self._min_character_width = min_character_width
        self._fg_color = ThemeManager.theme["DropdownMenu"]["fg_color"] if fg_color is None else self._check_color_type(fg_color)
        self._hover_color = ThemeManager.theme["DropdownMenu"]["hover_color"] if hover_color is None else self._check_color_type(hover_color)
        self._text_color = ThemeManager.theme["DropdownMenu"]["text_color"] if text_color is None else self._check_color_type(text_color)

        # font
        self._font = CTkFont() if font is None else self._check_font_type(font)
        if isinstance(self._font, CTkFont):
            self._font.add_size_configure_callback(self._update_font)

        self._configure_menu_for_platforms()

        self._values = values
        self._command = command

        self._add_menu_commands()