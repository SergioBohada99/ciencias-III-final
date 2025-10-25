import tkinter as tk
from tkinter import ttk


class InternasView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:  # app: RetroApp
		super().__init__(parent)

		title = ttk.Label(self, text="Búsquedas internas", style="Title.TLabel")
		title.pack(pady=(30, 10))

		panel = ttk.Frame(self, style="Panel.TFrame", padding=20)
		panel.pack(pady=10)

		btn_lineal = ttk.Button(
			panel, text="Búsqueda lineal", style="Retro.TButton", command=lambda: app.navigate("lineal")
		)
		btn_lineal.grid(row=0, column=0, padx=10, pady=10)

		btn_binaria = ttk.Button(
			panel, text="Búsqueda binaria", style="Retro.TButton", command=lambda: app.navigate("binaria")
		)
		btn_binaria.grid(row=0, column=1, padx=10, pady=10)

		btn_hash = ttk.Button(
			panel, text="Función hash", style="Retro.TButton", command=lambda: app.navigate("hash")
		)
		btn_hash.grid(row=0, column=2, padx=10, pady=10)

		btn_trie = ttk.Button(
			panel, text="Árbol digital", style="Retro.TButton", command=lambda: app.navigate("trie")
		)
		btn_trie.grid(row=0, column=3, padx=10, pady=10)

		btn_huffman = ttk.Button(
			panel, text="Árboles de Huffman", style="Retro.TButton", command=lambda: app.navigate("huffman")
		)
		btn_huffman.grid(row=1, column=0, padx=10, pady=10)

		btn_residuos = ttk.Button(
			panel, text="Árbol de residuos", style="Retro.TButton", command=lambda: app.navigate("residuos_tree")
		)
		btn_residuos.grid(row=1, column=1, padx=10, pady=10, columnspan=3, sticky="ew")

		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("busquedas"))
		back.pack(pady=10)


