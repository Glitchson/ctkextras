from tkinter import Frame
from importlib.util import spec_from_file_location,module_from_spec
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
class AppWatcher(FileSystemEventHandler):
    """
    Listens for changes in the directory and updates the ui"""
    def __init__(self, app_instance, script_path):
        super().__init__()
        self._ui = app_instance
        self.script_path = script_path
        self.on_modified=self._on_dir_change
        self._reload()
    def _reload(self):
        spec = spec_from_file_location("mod", self.script_path)
        self.mod= module_from_spec(spec)
        spec.loader.exec_module(self.mod)
    def _on_dir_change(self, event):
        if event.is_directory:
            return
        self._reload()
        try:
            self._ui._update()
        except Exception as e:
            print(e)
class CTkReload(Frame):
    """Reloads the ui when changes are made in the app file
    Arguments:
        `root`
    The main app class
        `script_path`
    The name and path to where the contents of the file will be cotained
    
    The script file must contain a function called `reload` which takes in the container frame as an argument.
    This is the widget parent for all the ui elements.
    NOTE This should be primarily used for configuring the structure and the style of the widgets.
    Functionality to be implimented if complex may lead to unforseable behaviour when reloading
    >>> #reload.py :file running in the background
        root = CTk()
        CTkReload(root,'main.py')
        root.mainloop()
        #NOTE ,you can use the tkinter toplevel or any toplevels that inherit from tkinter
        #main.py :file containing the widgets
        class Ui:
            def __init__(self,container):
                self._button=CTkButton(container)
                self._button.pack()
                ...
                self.pack(expand=True,fille="both")
        def reload(container):
            Ui(container)
        """
    def __init__(self, root:str, script_path):
        super().__init__(root)
        self._draw_container()
        self.script_path = script_path
        self.file_watcher = AppWatcher(self, script_path)
        self.observer = Observer()
        self.observer.schedule(self.file_watcher, path=".", recursive=False)
        self.file_watcher._reload()
    def _draw_container(self):
        self.cframe = Frame(self,bg="#333333")
        self.cframe.pack(fill="both",expand=True)
    def _update(self): 
        try:
            self.cframe.destroy()
        except Exception as e:
            pass
        self._draw_container()
        if hasattr(self.file_watcher.mod, "reload"):self.file_watcher.mod.reload(self.cframe)
    def start(self):self.observer.start()