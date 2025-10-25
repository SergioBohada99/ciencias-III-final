import tkinter as tk
from tkinter import ttk


class ExternasView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:  # app: RetroApp
		super().__init__(parent)

		title = ttk.Label(self, text="Búsquedas externas", style="Title.TLabel")
		title.pack(pady=(30, 10))

		panel = ttk.Frame(self, style="Panel.TFrame", padding=20)
		panel.pack(pady=10)


		# Externas: Lineal (bloques), Binario (bloques binaria), Transformación de claves
		btn_lineal = ttk.Button(
			panel, text="Lineal", style="Retro.TButton", command=lambda: app.navigate("bloques")
		)
		btn_lineal.grid(row=0, column=0, padx=10, pady=10)

		btn_binario = ttk.Button(
			panel, text="Binario", style="Retro.TButton", command=lambda: app.navigate("binario_ext")
		)
		btn_binario.grid(row=0, column=1, padx=10, pady=10)

		btn_transform = ttk.Button(
			panel, text="Transformación de claves", style="Retro.TButton", command=lambda: app.navigate("transformacion")
		)
		btn_transform.grid(row=0, column=2, padx=10, pady=10)

		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("busquedas"))
		back.pack(pady=10)