import random
import string
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional


class BusquedaLinealView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:  # app: RetroApp
		super().__init__(parent)

		title = ttk.Label(self, text="Búsqueda lineal", style="Title.TLabel")
		title.pack(pady=(20, 5))

		# Section 1: Parámetros (igual a Binaria)
		params = ttk.Frame(self, style="Panel.TFrame", padding=10)
		params.pack(fill=tk.X, padx=4, pady=6)

		lbl_n = ttk.Label(params, text="Rango (n):")
		lbl_n.grid(row=0, column=0, sticky="w", padx=(0, 6))
		self.entry_n = ttk.Entry(params, width=10)
		self.entry_n.insert(0, "10")
		self.entry_n.grid(row=0, column=1, padx=(0, 16))

		lbl_len = ttk.Label(params, text="Dígitos de la clave (solo números):")
		lbl_len.grid(row=0, column=2, sticky="w", padx=(0, 6))
		self.entry_len = ttk.Entry(params, width=10)
		self.entry_len.insert(0, "5")
		self.entry_len.grid(row=0, column=3, padx=(0, 16))

		btn_generate_params = ttk.Button(params, text="Generar datos", command=self._on_generate)
		btn_generate_params.grid(row=0, column=4, padx=(0, 6))

		# Visualización fija (lista)

		# Section 2: Panel paralelo (operaciones izquierda, visualización derecha)
		panel = ttk.Frame(self, padding=6)
		panel.pack(fill=tk.BOTH, expand=True)

		ops = ttk.Frame(panel, style="Panel.TFrame", padding=10)
		ops.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

		# Eliminadas pestañas; UI simplificada

		lbl_target = ttk.Label(ops, text="Número:")
		lbl_target.grid(row=0, column=0, sticky="w")
		self.entry_target = ttk.Entry(ops, width=16)
		self.entry_target.grid(row=1, column=0, pady=(0, 10))

		btn_insert = ttk.Button(ops, text="Insertar", style="Retro.TButton", command=self._on_insert)
		btn_insert.grid(row=2, column=0, pady=4, sticky="ew")

		btn_delete = ttk.Button(ops, text="Eliminar", style="Retro.TButton", command=self._on_delete)
		btn_delete.grid(row=3, column=0, pady=4, sticky="ew")

		btn_search = ttk.Button(ops, text="Buscar", style="Retro.TButton", command=self._on_search)
		btn_search.grid(row=4, column=0, pady=4, sticky="ew")


		btn_reset = ttk.Button(ops, text="Reiniciar", command=self._on_reset)
		btn_reset.grid(row=5, column=0, pady=4, sticky="ew")

		self.status = ttk.Label(ops, text="Estado: listo")
		self.status.grid(row=6, column=0, pady=(8, 0), sticky="w")

		viz_panel = ttk.Frame(panel, style="Panel.TFrame", padding=12)
		viz_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.canvas = tk.Canvas(viz_panel, background="#ffffff", height=420)

		# Treeview (lista)
		self.tree = ttk.Treeview(viz_panel, columns=("idx", "val"), show="headings", height=18)
		self.tree.heading("idx", text="Dirección")
		self.tree.heading("val", text="Clave")
		self.tree.column("idx", width=100, anchor="center")
		self.tree.column("val", width=200, anchor="center")
		self.tree.tag_configure("normal", background="#ffffff")
		self.tree.tag_configure("current", background="#cfe8ff")
		self.tree.tag_configure("delete", background="#ffd6d6")
		self.tree.pack(fill=tk.BOTH, expand=True)

		# Bottom save/load panel
		file_panel = ttk.Frame(self, style="Panel.TFrame", padding=8)
		file_panel.pack(fill=tk.X, padx=4, pady=6)

		btn_save_close = ttk.Button(file_panel, text="Guardar y cerrar", command=self._on_save_and_close)
		btn_save_close.grid(row=0, column=0, padx=4, pady=2)

		btn_save = ttk.Button(file_panel, text="Guardar", command=self._on_save)
		btn_save.grid(row=0, column=1, padx=4, pady=2)

		btn_load = ttk.Button(file_panel, text="Cargar", command=self._on_load)
		btn_load.grid(row=0, column=2, padx=4, pady=2)

		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("internas"))
		back.pack(pady=8)

		self.app = app

		self._data: List[str] = []
		self._selected_index: Optional[int] = None
		self._delete_index: Optional[int] = None
		self._draw()

	def _read_params(self) -> (int, int):
		try:
			n = int(self.entry_n.get())
		except ValueError:
			n = 10
		try:
			max_len = int(self.entry_len.get())
		except ValueError:
			max_len = 5
		return max(0, n), max(1, max_len)

	def _random_key(self, max_len: int) -> str:
		length = random.randint(1, max_len)
		alphabet = "0123456789"
		# Avoid leading zeros only if length > 1 to keep numbers visually meaningful
		first = random.choice("123456789") if length > 1 else random.choice(alphabet)
		if length == 1:
			return first
		return first + "".join(random.choice(alphabet) for _ in range(length - 1))

	def _validate_numeric(self, key_str: str, max_len: int) -> Optional[str]:
		if not key_str.isdigit():
			messagebox.showerror("Error", "La clave debe ser numérica.")
			return None
		if len(key_str) > max_len:
			messagebox.showerror("Error", "Clave supera el máximo de dígitos.")
			return None
		return key_str

	def _sort_data(self) -> None:
		# Mantener la estructura siempre ordenada numéricamente
		try:
			self._data.sort(key=int)
		except Exception:
			self._data.sort()

	def _on_generate(self) -> None:
		n, max_len = self._read_params()
		self._data = [self._random_key(max_len) for _ in range(n)]
		self._selected_index = None
		self._delete_index = None
		self._sort_data()
		self._draw()

	def _on_reset(self) -> None:
		self._data = []
		self._selected_index = None
		self._delete_index = None
		self._draw()

	def _on_insert(self) -> None:
		_, max_len = self._read_params()
		try:
			capacity = int(self.entry_n.get())
		except Exception:
			capacity = len(self._data)
		if len(self._data) >= max(0, capacity):
			messagebox.showerror("Error", "Capacidad alcanzada (n)")
			return
		inp = self.entry_target.get().strip()
		if inp:
			key = self._validate_numeric(inp, max_len)
			if key is None:
				return
		else:
			key = self._random_key(max_len)
		self._data.append(key)
		self._sort_data()
		self._draw()

	def _on_delete(self) -> None:
		inp = self.entry_target.get().strip()
		if not inp or not self._data:
			return
		_, max_len = self._read_params()
		target = self._validate_numeric(inp, max_len)
		if target is None:
			return
		self._selected_index = None
		self._delete_index = None
		for idx, value in enumerate(self._data):
			self._selected_index = idx
			self._draw()
			self.after(700)
			self.update_idletasks()
			if value == target:
				self._delete_index = idx
				self._draw()
				self.after(1400)
				self.update_idletasks()
				del self._data[idx]
				self._selected_index = None
				self._delete_index = None
				self._sort_data()
				self._draw()
				return
		# Not found
		self._selected_index = None
		self._delete_index = None
		self._draw()
		messagebox.showinfo("Búsqueda", "Valor no encontrado")

	def _on_search(self) -> None:
		inp = self.entry_target.get().strip()
		_, max_len = self._read_params()
		target = self._validate_numeric(inp, max_len)
		if target is None:
			return
		self._selected_index = None
		self._delete_index = None
		for idx, value in enumerate(self._data):
			self._selected_index = idx
			self._draw()
			self.after(700)
			self.update_idletasks()
			if value == target:
				return
		self._selected_index = None
		self._draw()
		messagebox.showinfo("Búsqueda", "Valor no encontrado")

	def _serialize(self) -> str:
		_, max_len = self._read_params()
		joined = ",".join(self._data)
		return f"max_len:{max_len}\narray:{joined}\n"

	def _parse(self, content: str) -> Optional[tuple[int, List[str]]]:
		lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
		max_len: Optional[int] = None
		arr: List[str] = []
		for ln in lines:
			if ln.lower().startswith("max_len:"):
				try:
					max_len = int(ln.split(":", 1)[1].strip())
				except Exception:
					return None
			elif ln.lower().startswith("array:"):
				arr_str = ln.split(":", 1)[1]
				arr.extend([s for s in arr_str.split(",") if s != ""])
			else:
				arr.extend([s for s in ln.split(",") if s != ""])
		if max_len is None:
			return None
		return max_len, arr

	def _on_save(self) -> None:
		if not self._data:
			if not messagebox.askyesno("Guardar", "La estructura está vacía. ¿Guardar de todos modos?"):
				return
		path = filedialog.asksaveasfilename(
			title="Guardar estructura",
			defaultextension=".txt",
			filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
		)
		if not path:
			return
		try:
			data = self._serialize()
			with open(path, "w", encoding="utf-8") as f:
				f.write(data)
			messagebox.showinfo("Éxito", "Estructura guardada correctamente")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_save_and_close(self) -> None:
		if not self._data:
			if not messagebox.askyesno("Guardar", "La estructura está vacía. ¿Guardar de todos modos?"):
				return
		path = filedialog.asksaveasfilename(
			title="Guardar estructura",
			defaultextension=".txt",
			filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
		)
		if not path:
			return
		try:
			data = self._serialize()
			with open(path, "w", encoding="utf-8") as f:
				f.write(data)
			messagebox.showinfo("Éxito", "Estructura guardada correctamente")
			self.app.navigate("internas")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_load(self) -> None:
		path = filedialog.askopenfilename(
			title="Cargar estructura",
			filetypes=[("Texto", "*.txt"), ("Todos", "*.*")],
		)
		if not path:
			return
		try:
			with open(path, "r", encoding="utf-8") as f:
				content = f.read()
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo leer: {e}")
			return
		parsed = self._parse(content)
		if not parsed:
			messagebox.showerror("Error", "Formato inválido")
			return
		max_len, arr = parsed
		# update max_len field
		self.entry_len.delete(0, tk.END)
		self.entry_len.insert(0, str(max_len))
		# validate numeric and lengths
		ok = all(x.isdigit() and len(x) <= max_len for x in arr)
		if not ok:
			messagebox.showerror("Error", "Clave supera el máximo de caracteres.")
			return
		self._data = list(arr)
		self._selected_index = None
		self._delete_index = None
		self._sort_data()
		self._draw()

	def _draw(self) -> None:
		self.tree.delete(*self.tree.get_children())
		try:
			capacity = int(self.entry_n.get())
		except Exception:
			capacity = len(self._data)
		capacity = max(capacity, len(self._data))
		for idx in range(capacity):
			value = self._data[idx] if idx < len(self._data) else "-"
			if self._delete_index == idx:
				tags = ("delete",)
			elif self._selected_index == idx:
				tags = ("current",)
			else:
				tags = ("normal",)
			self.tree.insert("", "end", values=(idx, value), tags=tags)


