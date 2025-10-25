import tkinter as tk
from tkinter import ttk


class BusquedasView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:  # app: RetroApp
		super().__init__(parent)

		title = ttk.Label(self, text="Búsquedas", style="Title.TLabel")
		title.pack(pady=(40, 20))

		buttons = ttk.Frame(self, style="Panel.TFrame", padding=20)
		buttons.pack(pady=20)

		btn_internas = ttk.Button(
			buttons,
			text="Internas",
			style="Retro.TButton",
			command=lambda: app.navigate("internas"),
		)
		btn_internas.grid(row=0, column=0, padx=10, pady=10)

		btn_externas = ttk.Button(
			buttons,
			text="Externas",
			style="Retro.TButton",
			command=lambda: app.navigate("externas"),
		)
		btn_externas.grid(row=0, column=1, padx=10, pady=10)

		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("home"))
		back.pack(pady=10)


