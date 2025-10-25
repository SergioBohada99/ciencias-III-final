import tkinter as tk
from tkinter import ttk


class HomeView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:  # app: RetroApp
		super().__init__(parent)

		title = ttk.Label(self, text="CIENCIAS DE LA COMPUTACIÓN II", style="Title.TLabel")
		title.pack(pady=(40, 20))

		buttons = ttk.Frame(self, style="Panel.TFrame", padding=20)
		buttons.pack(pady=20)

		btn_busquedas = ttk.Button(
			buttons,
			text="Búsquedas",
			style="Retro.TButton",
			command=lambda: app.navigate("busquedas"),
		)
		btn_busquedas.grid(row=0, column=0, padx=10, pady=10)

		btn_grafos = ttk.Button(
			buttons,
			text="Grafos",
			style="Retro.TButton",
			command=lambda: app.navigate("grafos"),
		)
		btn_grafos.grid(row=0, column=1, padx=10, pady=10)


