import tkinter as tk
from tkinter import ttk


class ArbolesMenuView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:  # app: RetroApp
		super().__init__(parent)

		title = ttk.Label(self, text="Árboles", style="Title.TLabel")
		title.pack(pady=(30, 10))

		desc = ttk.Label(self, text="Selecciona el submódulo que deseas explorar")
		desc.pack(pady=5)

		panel = ttk.Frame(self, style="Panel.TFrame", padding=20)
		panel.pack(pady=10)

		# Botón para Matrices
		btn_matrices = ttk.Button(
			panel, 
			text="Matrices", 
			style="Retro.TButton", 
			command=lambda: app.navigate("grafo_matrices")
		)
		btn_matrices.grid(row=0, column=0, padx=10, pady=10)

		# Botón para Árbol Generador
		btn_arbol_generador = ttk.Button(
			panel, 
			text="Árbol Generador", 
			style="Retro.TButton", 
			command=lambda: app.navigate("arboles")
		)
		btn_arbol_generador.grid(row=0, column=1, padx=10, pady=10)

		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("grafos"))
		back.pack(pady=10)

