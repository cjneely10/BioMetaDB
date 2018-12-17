import os
import tkinter as tk
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from tkinter import messagebox


# Begin script stuff

class Grapher:
    def __init__(self, size=()):
        """
		Usage:
		grapher = Grapher(size=(x,y))
		grapher.init()
		grapher.plt.[insert function]()
		...
		...
		grapher.show()
		"""
        self.size = size
        self.root = tk.Tk()
        self.root.wm_title("{0}".format(os.path.basename(__file__.split(".")[0])))
        self.plt = plt
        self.ax = None
        self.fig = None

    def on_key_event(self, event):
        key_press_handler(event, self.canvas, self.toolbar)

    def _quit(self):
        self.root.destroy()
        self.root.quit()
        quit()

    def set_3D(self):
        self.ax = Axes3D(self.ax)

    def on_closing(self):
        if messagebox.askyesno("Exit", "Do you want to quit?"):
            self.root.destroy()
            self.root.quit()
            quit()

    def init(self, threeD=False):
        if threeD:
            self.fig = plt.figure(figsize=self.size, dpi=100)
            self.ax = self.fig.add_subplot(111, projection="3d")
        else:
            self.fig = plt.figure(figsize=self.size, dpi=100)
            self.ax = self.fig.add_subplot(111)

    def show(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.root)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.button = tk.Button(master=self.root, text="Quit", command=self._quit)
        self.button.pack(side=tk.BOTTOM)
        self.canvas.mpl_connect('key_press_event', self.on_key_event)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        self.plt.show()
