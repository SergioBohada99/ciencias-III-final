import tkinter as tk
from tkinter import ttk
from typing import Dict, Type

from app.theme.retro import apply_retro_style


class RetroApp:
	def __init__(self) -> None:
		self.root = tk.Tk()
		self.root.title("Ciencias de la Computación II - Búsquedas")
		self.root.geometry("1000x700")
		self.root.resizable(True, True)

		apply_retro_style(self.root)

		self.container = ttk.Frame(self.root, padding=10)
		self.container.pack(fill=tk.BOTH, expand=True)

		self.views: Dict[str, tk.Frame] = {}
		self._init_views()

	def _init_views(self) -> None:
		from app.views.home import HomeView
		from app.views.busquedas import BusquedasView
		from app.views.internas import InternasView
		from app.views.externas import ExternasView
		from app.views.busqueda_lineal import BusquedaLinealView
		from app.views.busqueda_binaria import BusquedaBinariaView
		from app.views.hash_view import HashView
		from app.views.trie_view import TrieView
		from app.views.huffman_view import HuffmanView
		from app.views.residuos_multiples_view import ResiduosMultiplesView
		from app.views.grafos import GrafosView
		from app.views.bloques_view import BloquesView
		from app.views.dinamicas_view import DinamicasView
		from app.views.indices_view import IndicesView
		from app.views.residuos_tree_view import ResiduosTreeView
		from app.views.bloques_binaria_view import BloquesBinariaView
		from app.views.transformacion_view import TransformacionClavesView
		from app.views.dinamicas_parciales_view import DinamicasParcialesView
		from app.views.dinamicas_totales_view import DinamicasTotalesView
		from app.views.grafo_unario_view import GrafoUnarioView
		from app.views.grafo_binario_view import GrafoBinarioView


		available_views: Dict[str, Type[tk.Frame]] = {
			"home": HomeView,
			"busquedas": BusquedasView,
			"internas": InternasView,
			"externas": ExternasView,
			"lineal": BusquedaLinealView,
			"binaria": BusquedaBinariaView,
			"hash": HashView,
			"trie": TrieView,
			"huffman": HuffmanView,
			"residuos_multiples": ResiduosMultiplesView,
			"grafos": GrafosView,
			"grafo_unario": GrafoUnarioView,
			"grafo_binario": GrafoBinarioView,
			"bloques": BloquesView,
			"binario_ext": BloquesBinariaView,
			"transformacion": TransformacionClavesView,
			"dinamicas": DinamicasView,
			"indices": IndicesView,
			"residuos_tree": ResiduosTreeView,
			"dinamicas_totales": DinamicasTotalesView,
			"dinamicas_parciales": DinamicasParcialesView
		}

		self.views.clear()
		for name, ViewCls in available_views.items():
			frame = ViewCls(parent=self.container, app=self)
			self.views[name] = frame
			frame.grid(row=0, column=0, sticky="nsew")

		self.container.rowconfigure(0, weight=1)
		self.container.columnconfigure(0, weight=1)

		self.navigate("home")

	def navigate(self, view_name: str) -> None:
		for name, frame in self.views.items():
			if name == view_name:
				frame.tkraise()
				break

	def run(self) -> None:
		self.root.mainloop()


