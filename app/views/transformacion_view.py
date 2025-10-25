import tkinter as tk
from tkinter import ttk


class TransformacionClavesView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)

		title = ttk.Label(self, text="Transformación de claves", style="Title.TLabel")
		title.pack(pady=(20, 5))

		desc = ttk.Label(self, text="Próximamente: búsqueda externa por transformación de claves", style="TLabel")
		desc.pack(pady=10)

		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("externas"))
		back.pack(pady=6)
