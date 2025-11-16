import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Set, Tuple
import math


class GrafoBinarioView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)
		
		title = ttk.Label(self, text="Operaciones con Dos Grafos", style="Title.TLabel")
		title.pack(pady=(20, 5))
		
		desc = ttk.Label(self, text="Próximamente: Producto cruz, producto tensorial, unión, etc.")
		desc.pack(pady=10)
		
		# Botón volver
		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("grafos"))
		back.pack(pady=6)
		
		self.app = app

