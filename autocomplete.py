from tkinter import INSERT,CURRENT
from customtkinter import CTkFrame,CTkLabel,CTkFont
from .algoz import close_matches,List
from typing import Callable,Any
def preload_options(_o):
    pr={}
    for i in _o:
        key=i[0].lower()
        if key in pr:
            pr[key].append(i)
            continue
        pr[key]=[i]
    return pr
def matcher(_str,opt,threshhold):
    if _str=="":
        return []
    key=_str[0].lower()
    if key not in opt:
        return []
    return close_matches(_str.lower(),opt[key],threshhold=threshhold)
class Option(CTkLabel):
    """The suggestion options"""
    def __init__(
            self,
            master,
            fg_color,
            focus_color,
            hover_color,
            font,
            text_color,
            padding,
            corner_radius,
            width,
            height,
            text_padx
        ):
        self.padding=padding
        super().__init__(
            master=master,
            fg_color=fg_color,
            bg_color="transparent",
            font=font,
            text="",
            text_color=text_color,
            corner_radius=corner_radius,
            height=height ,
            anchor="w",
            width=width,
            padx=text_padx,
        )
        self.master=master
        self.textbox=master.textbox
        self._color={
            "fg":fg_color,
            "hc":hover_color,
            "fc":focus_color
        }
        self.selected=False
        self.bind("<Enter>",self._enter)
        self.bind("<Leave>",self._leave)
        self.bind("<Button-1>",self._click)
    def _enter(self,event):
        return self.configure(fg_color=self._color["hc"])
    def _leave(self,event):
        if self.selected:return self.configure(fg_color=self._color["fc"])
        return self.configure(fg_color=self._color["fg"])
    def _click(self,event):
        self.focus()
        self.insert()
        self.master.remove()
    def focus(self):
        if self.master.current:
            self.master.current.defocus()
        self.selected=True
        self.master.current=self
        self.configure(fg_color=self._color["fc"])
    def defocus(self):
        self.selected=False
        self.configure(fg_color=self._color["fg"])
        self.master.current=None
    def insert(self):
        ct:str=self.textbox.get("1.0",INSERT)
        self.textbox.delete("1.0",INSERT)
        suggestion=self.cget("text")
        ct=ct.removesuffix(self.master.buffer)+suggestion
        self.textbox.insert("1.0",ct)
        self.master.remove()
        self.textbox.mark_set(CURRENT,self.textbox.index(INSERT))
        self.textbox.see(INSERT)
    def add(self,text):
        self.defocus()
        self.configure(text=text)
        padx,pady=self.padding
        self.pack(padx=padx,pady=pady,fill="x",expand=True)
class CTkAutoComplete(CTkFrame):
    """This is a simple autocomplete that configures snippetes for a textbox
    ARGUMENTS:
        `textbox`
    This is the textbox in which the autocomplete is set up
        `font`
    This is the font of the text in the suggestion widgets
        `preloader`
    This is a functions that preorganises the snippets before they can be used in the autocomplete for more precise snippetes.
    By default, the snippets are split into a dictionary of letter keys and a list of words that start with those letters.
        `match_engine`
    This is the function that takes in:
        - string to match
        - preloaded snippets
        - threshhold
        `maximum_results`
    The maximum amount of suggestions that can be shown
        `threshhold`
    The precision of the strings matched for them to be considered valid. 
    If using a custom `match_engine`, this should be implimented in the function.
    """
    def __init__(
            self,
            textbox,
            fg_color: str | tuple[str,str] | None = None,
            font: CTkFont | None = None,
            text_color: str | tuple[str,str] | None = None,
            border_width: int | None = None,
            border_color: str | tuple[str,str] | None = None,
            option_fg_color: str | None = None,
            option_focus_color: str | None = None,
            option_hover_color: str | None = None,
            option_padding: tuple[int,int] | tuple[tuple[int,int],tuple[int,int]] | None = None,
            option_corner_radius: int | None = None,
            option_width: int | None = None,
            option_height: int | None = None,
            optional_text_padx: int | tuple[int,int] | None = None,
            match_engine: Callable[[str,list[str],int | float],list[str]] | None = None,
            preloader: Callable[[list[str]],Any] | None = None,
            maximum_results: int | None = None,
            threshhold: int | None = None,

        ):
        super().__init__(
            master=textbox.winfo_toplevel(),
            fg_color=fg_color or "#151515",
            corner_radius=0,
            border_width=border_width or 1,
            border_color=border_color or "#999999",
        )
        if not font:
            font=textbox.cget("font")
        else:
            font.configure(size=textbox.cget("font").cget("size"))
        self.threshhold=threshhold or 60
        self.maximum_results=maximum_results or 5
        self.match_engine=match_engine or matcher
        self.preloader=preloader or preload_options
        self.textbox=textbox
        self.reverse=False
        self.buffer=""
        self._suggestions=[]
        self._preloaded_widgets=[]
        self._optwidgs=List([])
        self._placed=False
        self.fonty=font.cget("size")
        self.current=None
        self._opt_config=[
            self,
            option_fg_color or "transparent",
            option_focus_color or "#404040",
            option_hover_color or "#404040",
            font,
            text_color or "#909090",
            option_padding or (2,1),
            option_corner_radius or 0,
            option_width or 250,
            option_height or 22,
            optional_text_padx or 3
        ]
        self.textbox.bind("<Up>",self._up)
        self.textbox.bind("<Down>",self._down)
        self.textbox.bind("<Tab>",self._tab)
        self.textbox.bind("<Return>", self._return)
        self.textbox.bind("<space>",  self._space)
        self.textbox.bind("<BackSpace>",  self._backspace)
        self.textbox.bind("<FocusOut>",self._focus_out)
        self.textbox.bind("<Configure>",self._on_configure)
        self.textbox.bind("<KeyPress>",self._ontype)
        self._preload_opts()
    def set_snippets(self,_s:list[str],):
        self._suggestions=self.preloader(list({i for i in _s}))
    def _get_to_place(self):
        tb=self.textbox
        n=tb.bbox(tb.index(INSERT))
        if not n:
            return n
        x,y,*_=n
        tx,ty=tb.winfo_rootx()-tb.winfo_toplevel().winfo_rootx(),tb.winfo_rooty()-tb.winfo_toplevel().winfo_rooty()
        width,height=self.winfo_width(),self.winfo_height()
        twidth,theight=tb.winfo_width(),tb.winfo_height()
        dy=int(self.fonty*5/3)
        x+=5
        y+=dy
        if x+width>tx+twidth:
            x-=width
        if y+height>ty+theight:
            y-=height
            self.reverse=True
        return x,y
    def _draw_option(self,master):
        o=Option(
            *self._opt_config
        )
        return o
    def _get_option_text(self):
        if self.buffer=="" or self._suggestions==[]:return []
        sg=self.match_engine(self.buffer,self._suggestions,self.threshhold)
        if self.reverse:
            return sg[::-1][:self.maximum_results+1]
        return sg[:self.maximum_results+1]
    def _preload_opts(self):
        for _ in range(self.maximum_results+1):
            self._preloaded_widgets.append(self._draw_option(self))
    def _gen_options(self):
        self._optwidgs=List([])
        sg=self._get_option_text()
        if sg==[]:
            self._placed=False
            return
        if self.reverse:
            sg=sg[::-1]
        for text,w in zip(sg,self._preloaded_widgets):
            w.add(text)
            self._optwidgs.append(w)
        self._placed=True
        if self.reverse:
            self._optwidgs._i=-1
            self.current=self._optwidgs[-1]
            return
        self._optwidgs._i=0
        self.current=self._optwidgs[0]
    def _rem_prev(self):
        for i in self._optwidgs:
            i.pack_forget()
    def _setup_(self):
        pos=self._get_to_place()
        self._gen_options()
        if not self._placed or not pos:
            return
        self.current.focus()
        x,y=pos
        self.place(x=x,y=y)
    def remove(self):
        self.place_forget()
        self._rem_prev()
        self.current=None
        self._placed=False
        self.reverse=False
    def _tab(self,event):
        if self._placed and self.current:
            self.current.insert()
            self.buffer=""
            return "break"
    def _return(self,event):
        if self._placed and self.current:
            self.current.insert()
            self.buffer=""
            return "break"
    def _up(self,event):
        if self._placed:
            self._optwidgs.prev().focus()
            return "break"
    def _down(self,event):
        if self._placed:
            self._optwidgs.nxt().focus()
            return "break"
        return 
    def _space(self,event):
        if self._placed:
            self.remove()
        self.buffer=""
    def _backspace(self,event):
        if self._placed:
            self.remove()
        self.buffer=self.buffer[:-1]
    def _focus_out(self,event):
        if self._placed:
            self.remove()
    def _on_configure(self,event):
        if self._placed:
            self.remove()
    def _ontype(self,event):
        keysym=event.keysym
        char=event.char
        if keysym in ("Tab","Return","Up","Down","space","BackSpace","Left","Right"):return
        if self._placed:
            self.remove()
        self.buffer+=char
        self._setup_()