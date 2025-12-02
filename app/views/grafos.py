import tkinter as tk
from tkinter import ttk


class GrafosView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:  # app: RetroApp
		super().__init__(parent)

		title = ttk.Label(self, text="Operaciones con Grafos", style="Title.TLabel")
		title.pack(pady=(30, 10))

		desc = ttk.Label(self, text="Selecciona el tipo de operaciones que deseas realizar")
		desc.pack(pady=5)

		panel = ttk.Frame(self, style="Panel.TFrame", padding=20)
		panel.pack(pady=10)

		# Botón para operaciones con un solo grafo
		btn_unario = ttk.Button(
			panel, 
			text="Operaciones con Un Grafo", 
			style="Retro.TButton", 
			command=lambda: app.navigate("grafo_unario")
		)
		btn_unario.grid(row=0, column=0, padx=10, pady=10)

		# Botón para operaciones con dos grafos
		btn_binario = ttk.Button(
			panel, 
			text="Operaciones con Varios Grafos", 
			style="Retro.TButton", 
			command=lambda: app.navigate("grafo_binario")
		)
		btn_binario.grid(row=0, column=1, padx=10, pady=10)

		# Botón para Algoritmo de Floyd
		btn_floyd = ttk.Button(
			panel, 
			text="Algoritmo de Floyd", 
			style="Retro.TButton", 
			command=lambda: app.navigate("floyd")
		)
		btn_floyd.grid(row=1, column=0, padx=10, pady=10)

		# Botón para Árboles (submódulos)
		btn_arboles = ttk.Button(
			panel, 
			text="Árboles", 
			style="Retro.TButton", 
			command=lambda: app.navigate("arboles_menu")
		)
		btn_arboles.grid(row=1, column=1, padx=10, pady=10)

		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("home"))
		back.pack(pady=10)


