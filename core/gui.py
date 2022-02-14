#!/usr/bin/env/python3
# -*- coding:utf-8 -*-

import functools
from threading import Thread
from tkinter import Misc
from typing import List, Tuple

from ttkbootstrap import *
from ttkbootstrap.constants import *


class GUI(Window):
    @classmethod
    def multi_thread(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            thread = Thread(target=func, args=args, kwargs=kwargs)
            thread.setDaemon(True)
            thread.start()

        return wrapper

    def __init__(self,
                 title="ttkbootstrap",
                 base_size=8,
                 icon_path=None,
                 themename="litera",
                 iconphoto='',
                 size=None,
                 position=None,
                 minsize=None,
                 maxsize=None,
                 resizable=None,
                 hdpi=True,
                 scaling=None,
                 transient=None,
                 overrideredirect=False,
                 alpha=0.95):

        super().__init__(title=title,
                         themename=themename,
                         iconphoto=iconphoto,
                         size=size,
                         position=position,
                         minsize=minsize,
                         maxsize=maxsize,
                         resizable=resizable,
                         hdpi=hdpi,
                         scaling=scaling,
                         transient=transient,
                         overrideredirect=overrideredirect,
                         alpha=alpha)

        self.withdraw()

        self.base_size = base_size
        self.add_widget()
        self.center_horizontally(self)
        self.icon_path = icon_path
        if self.icon_path is not None:
            self.iconbitmap(self.icon_path)

        self.deiconify()

        self.before_work()

        # self.bind('<Return>', self._start_work)
        self.protocol('WM_DELETE_WINDOW', self.after_work)

    def add_widget(self):
        """
        "-": means columnspan
        "/": means a blank Label
        """
        widgets_list = [[None] * 9 for _ in range(9)]
        for i in range(9):
            for j in range(9):
                if i >= j:
                    widgets_list[i][j] = Label(
                        self,
                        text=f'{j+1}*{i+1}={(i+1)*(j+1)}',
                        anchor=CENTER,
                        bootstyle=(SUCCESS, INVERSE))
                else:
                    widgets_list[i][j] = '/'

        self.grid_widget(widgets_list, self, self.base_size)

    def grid_widget(self,
                    widgets_list: List[List[Tuple[Misc, str]]],
                    master: Misc,
                    padding: Tuple[int, Tuple[int, int, int, int]] = 0,
                    anchor: ANCHOR = CENTER,
                    sticky=NSEW):

        master.grid_anchor(anchor)

        max_column = len(widgets_list[0])
        assert all([len(widgets) == max_column for widgets in widgets_list
                    ]), 'the elements of each row are not equal'

        if isinstance(padding, int):
            padx = pady = ipadx = ipady = padding
        else:
            padx, pady, ipadx, ipady = padding

        for row, widgets in enumerate(widgets_list):
            for column, widget in enumerate(widgets):
                if widget == '-':
                    pass

                else:
                    columnspan = 1
                    for i in range(column + 1, max_column):
                        if widgets[i] == '-':
                            columnspan += 1
                        else:
                            break

                    if widget == '/':
                        widget = Label(master)

                    try:
                        widget.grid(row=row,
                                    column=column,
                                    columnspan=columnspan,
                                    padx=padx,
                                    pady=pady,
                                    ipadx=ipadx,
                                    ipady=ipady,
                                    sticky=sticky)
                    except AttributeError:
                        raise AttributeError(
                            f'''self.widgets_list can only contain "widget", "-" and "/", got a "{widget}".'''
                        )

    def center_horizontally(self, window: Tuple[Window, Toplevel]) -> None:
        window.update()
        w_width = window.winfo_width()
        w_height = window.winfo_height()
        s_width = self.winfo_screenwidth()
        s_height = self.winfo_screenheight()
        xpos = (s_width - w_width) // 2
        ypos = int((s_height - w_height) * 0.382)
        window.geometry(f'+{xpos}+{ypos}')

    def before_work(self):
        pass

    def start_work(self):
        pass

    def _start_work(self, event):
        return self.start_work()

    def after_work(self):
        self.destroy()


if __name__ == '__main__':
    gui = GUI()
    gui.mainloop()
