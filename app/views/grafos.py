import tkinter as tk
from tkinter import ttk


class GrafosView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:  # app: RetroApp
		super().__init__(parent)

		title = ttk.Label(self, text="Grafos", style="Title.TLabel")
		title.pack(pady=(30, 10))

		panel = ttk.Frame(self, style="Panel.TFrame", padding=20)
		panel.pack(pady=10)

		lbl = ttk.Label(panel, text="Panel de grafos (placeholder)")
		lbl.grid(row=0, column=0, padx=8, pady=8)

		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("home"))
		back.pack(pady=10)


