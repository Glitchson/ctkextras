from tkinter import END
from customtkinter import (
    CTkFrame,
    CTkLabel,
    CTkFont
)
from .algoz import close_matches,List
from typing import Callable

class Option(CTkLabel):
    """Option widgets for the suggestion frames"""
    def __init__(
            self,
            master,
            fg_color,
            hover_color,
            focus_color,
            text_color,
            width,
            corner_radius,
            font,
            padding,
        ):
        super().__init__(
            master=master,
            fg_color=fg_color ,
            corner_radius=corner_radius,
            anchor="w",
            font=font,
            text_color=text_color,
            text="",
            height=25,
            width=width
        )
        self.master=master
        self.padding=padding
        self._color={
            "fg":fg_color,
            "fo":focus_color,
            "hc":hover_color
        }
        self._selected=False
        self.bind("<Enter>",self._enter)
        self.bind("<Leave>",self._leave)
        self.bind("<Button-1>",self._click)
    def focus(self):
        if self.master.current:
            self.master.current.defocus()
            self._selected=True
        self.insert()
        self.configure(fg_color=self._color["fo"])
        self.master.current=self
    def defocus(self):
        self._selected=False
        self.configure(fg_color=self._color["fg"])
    def insert(self):
        text=self.cget("text")
        self.master.entry.delete(0,END)
        self.master.entry.insert(0,text)
    def _enter(self,event):
        if self._selected:
            return
        self.configure(fg_color=self._color["hc"])
    def _leave(self,event):
        if self._selected:
            self.configure(fg_color=self._color["fo"])
            return
        self.configure(fg_color=self._color["fg"])
    def _click(self,event):
        self.insert()
        self.master.submit()
    def add(self,text):
        x,y=self.padding
        self.configure(text=text)
        self.pack(padx=x,pady=y,fill="x",expand=True)
class CTkSearchConfig(CTkFrame):
    """This is a frame widget that turns a normal entry box into a search bar widget.
    ARGS:
        `entry`
    The enrty box thats meant to be used as a searchbar
        `max_results`
    The maximum results to be shown
        `search_engine`
    This is a function that generates suggestions.
    It takes in the following arguments
        - The string to be matched
        - A list of available results
        - The threshhold,,,
        `threshhold`
    By default, the search engine is implimented from the levenshtien distance algorithm.
    The threshhold is the minimum similarity (0-100) between the text and the suggestions.
        `colors`
    The following apply to the main frame container
        - fg_color
        - bg_color
        - corner_radius
        - border_width
        - border_color
    The following apply to the suggestion option widgets
        - option_fg_color
        - option_hover_color
        - option_focus_color
        - option_width
        - option_text_color
        - option_padding
        - option_corner_radius
    The focus color is the color of the option widget when selected using the arrow keys.
    The option padding is the a tupple: (`padx`,`pady`) for the options.
        `command`
    This is the function that gets executed when a widget is clicked, or the return key is pressed.
    METHODS:
        `set_suggestions`
    Takes in a list of strings and sets them as matchable options for the searchbar
    NOTE You can override some of the methods for more custom widgets
    The following method used for drawing an individual suggestion option is `_draw_option`
    It takes in:
        - text 
        - master
    NOTE 
        - The function set must return an option
        - The option must have methods `focus`,`defocus`
    >>> app=CTk()
        ent=CTkEntry(app,width=500,placeholder_text="Search Bar")
        ent.pack()
        sf=CTkSearchConfig(ent,command=lambda s: print(s))
        files=[
            'main.py',
            'index.html',
            'index.js',
            'project.rs',
            'readme.md',
            'main.cpp',
            'init.lua'
        ]
        sf.set_suggestions(files)
        app.mainloop()
        """
    def __init__(
            self,
            entry,
            max_results:int | None = None,
            search_engine:int | None = None,
            threshhold:int | None = None,
            fg_color:str | tuple[str,str] | None = None,
            bg_color:str | tuple[str,str] | None = None,
            option_fg_color:str | tuple[str,str] | None = None,
            option_hover_color:str | tuple[str,str] | None = None,
            option_focus_color:str | tuple[str,str] | None = None,
            option_width:int | None = None,
            font: CTkFont | None = None,
            option_text_color: CTkFont | None = None,
            corner_radius: int | None = None,
            border_width: int | None = None,
            border_color: str | tuple[str,str] | None = None,
            option_corner_radius: int | None = None,
            option_padding: tuple[int,int] | None = None,
            command: Callable[[str],None] | None = None
        ):
        super().__init__(
            master=entry.winfo_toplevel(),
            width=0,
            height=0,
            fg_color=fg_color or "#151515",
            bg_color= bg_color or "transparent",
            corner_radius=corner_radius or 10,
            border_color=border_color,
            border_width=border_width or 0
        )
        self._command=command or (lambda _ : _)
        self.current=None
        self.entry=entry
        self.threshhold=threshhold or 20
        self.searh_engine=search_engine or close_matches
        self.max_results=max_results or 5
        self._place=False
        self._optwid=List([])
        self._suggestions=[]
        self._opt_config=(
            option_fg_color or "transparent",
            option_hover_color or "#404040",
            option_focus_color or "#404040",
            option_text_color,
            option_width or entry.cget("width"),
            option_corner_radius or 5,
            font,
            option_padding or ((3,3),(3,3))
        )
        self.entry.bind("<KeyRelease>",self._ontype)
        self.entry.bind("<FocusOut>",self._focus_out)
    def set_suggestions(self,_s:list[str]):
        self._suggestions=list({i for i in _s})
    def _draw_option(self,text,master):
        o=Option(
            master,
            *self._opt_config
        )
        o.add(text)
        return o
    def _gen_options(self):
        a=self.searh_engine(
            " ".join(filter(None,self.entry.get())),
            self._suggestions,
            self.threshhold
        )[:self.max_results]
        self._optwid=List([])
        for i in a:
            self._optwid.append(self._draw_option(i,self))
        if len(self._optwid)==0:
            self._place=False
            return
        self.current=self._optwid[0]
        self.current.configure(fg_color=self.current._color["fo"])
        self._place=True
    def _rem_options(self):
        for i in self._optwid:
            i.destroy()
        self.current=None
        self._place=False
        self._optwid=List([])
    def _place_self(self):
        x=self.entry.winfo_rootx()-self.winfo_toplevel().winfo_rootx()
        y=self.entry.winfo_rooty()-self.winfo_toplevel().winfo_rooty()+self.entry.cget("height")+5
        self.place(x=x,y=y)
    def submit(self):
        t=self.entry.get()
        self.place_forget()
        self._rem_options()
        self._command(t)
        self.entry.delete(0,END)
        self.master.focus_set()
    def _ontype(self,event):
        keysym=event.keysym
        if keysym=="BackSpace":return self._setup_()
        if keysym=="Up":return self._up() 
        if keysym=="Down":return self._down()
        if keysym=="Return":return self.submit()
        self._setup_()
    def _focus_out(self,event):
        self.place_forget()
    def _up(self):
        if self._place:
            self._optwid.prev().focus()
            return "break"
    def _down(self):
        if self._place:
            self._optwid.nxt().focus()
            return "break"
    def _setup_(self):
        self.place_forget()
        self._rem_options()
        self._gen_options()
        if self._place:
            self._place_self()