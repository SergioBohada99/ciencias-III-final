import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional


class BusquedaBinariaView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)

		title = ttk.Label(self, text="Búsqueda binaria", style="Title.TLabel")
		title.pack(pady=(20, 5))

		# Section 1: Parámetros
		params = ttk.Frame(self, style="Panel.TFrame", padding=10)
		params.pack(fill=tk.X, padx=4, pady=6)

		lbl_n = ttk.Label(params, text="Rango (n):")
		lbl_n.grid(row=0, column=0, sticky="w", padx=(0, 6))
		self.entry_n = ttk.Entry(params, width=10)
		self.entry_n.insert(0, "10")
		self.entry_n.grid(row=0, column=1, padx=(0, 16))

		lbl_digits = ttk.Label(params, text="Dígitos de la clave (solo números):")
		lbl_digits.grid(row=0, column=2, sticky="w", padx=(0, 6))
		self.entry_digits = ttk.Entry(params, width=10)
		self.entry_digits.insert(0, "4")
		self.entry_digits.grid(row=0, column=3, padx=(0, 16))

		btn_generate = ttk.Button(params, text="Generar datos", command=self._on_generate)
		btn_generate.grid(row=0, column=4, padx=(0, 6))

		# Visualización fija (lista)

		# Section 2: Panel paralelo (operaciones izquierda, visualización derecha)
		panel = ttk.Frame(self, padding=6)
		panel.pack(fill=tk.BOTH, expand=True)

		ops = ttk.Frame(panel, style="Panel.TFrame", padding=10)
		ops.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

		lbl_key = ttk.Label(ops, text="Número:")
		lbl_key.grid(row=0, column=0, sticky="w")
		self.entry_key = ttk.Entry(ops, width=16)
		self.entry_key.grid(row=1, column=0, pady=(0, 10))

		btn_insert = ttk.Button(ops, text="Insertar", style="Retro.TButton", command=self._on_insert)
		btn_insert.grid(row=2, column=0, pady=4, sticky="ew")

		btn_delete = ttk.Button(ops, text="Eliminar", style="Retro.TButton", command=self._on_delete)
		btn_delete.grid(row=3, column=0, pady=4, sticky="ew")

		btn_search = ttk.Button(ops, text="Buscar", style="Retro.TButton", command=self._on_search)
		btn_search.grid(row=4, column=0, pady=4, sticky="ew")

		btn_reset = ttk.Button(ops, text="Reiniciar", command=self._on_reset)
		btn_reset.grid(row=5, column=0, pady=4, sticky="ew")

		self.status = ttk.Label(ops, text="Estado: listo")
		self.status.grid(row=6, column=0, pady=(12, 0), sticky="w")

		viz = ttk.Frame(panel, style="Panel.TFrame", padding=8)
		viz.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.canvas = tk.Canvas(viz, background="#ffffff", height=460)

		# Treeview (lista)
		self.tree = ttk.Treeview(viz, columns=("idx", "val"), show="headings", height=18)
		self.tree.heading("idx", text="Dirección")
		self.tree.heading("val", text="Clave")
		self.tree.column("idx", width=100, anchor="center")
		self.tree.column("val", width=140, anchor="center")
		# tags for row coloring
		self.tree.tag_configure("normal", background="#ffffff")
		self.tree.tag_configure("inrange", background="#e6e6e6")
		self.tree.tag_configure("mid", background="#cfe8ff")
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
		back.pack(pady=6)

		self.app = app

		self._array: List[int] = []
		self._highlight_index: Optional[int] = None
		self._low: Optional[int] = None
		self._high: Optional[int] = None
		self._delete_index: Optional[int] = None
		self._draw()

	# no-op: visualización fija

	def _serialize(self) -> str:
		_, digits = self._read_params()
		numbers = ",".join(str(x) for x in self._array)
		return f"digits:{digits}\narray:{numbers}\n"

	def _parse_serialized(self, content: str) -> Optional[tuple[int, List[int]]]:
		lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
		if not lines:
			return None
		loaded_digits: Optional[int] = None
		numbers_str: str = ""
		for ln in lines:
			if ln.lower().startswith("digits:"):
				try:
					loaded_digits = int(ln.split(":", 1)[1].strip())
				except Exception:
					return None
			elif ln.lower().startswith("array:"):
				numbers_str = ln.split(":", 1)[1].strip()
			else:
				# allow bare numbers separated by commas or spaces as fallback
				numbers_str = (numbers_str + " " + ln).strip()
		if numbers_str:
			seps = "," if "," in numbers_str else " "
			tokens = [t for t in numbers_str.replace(",", " ").split() if t]
			if not tokens:
				return None
			try:
				numbers = [int(t) for t in tokens]
			except Exception:
				return None
		else:
			numbers = []
		return (loaded_digits if loaded_digits is not None else 1, numbers)

	def _on_save(self) -> None:
		if not self._array:
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
			self.status.configure(text=f"Guardado en {path}")
			messagebox.showinfo("Éxito", "Estructura guardada correctamente")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_save_and_close(self) -> None:
		if not self._array:
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
			self.status.configure(text=f"Guardado en {path}")
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
			messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
			return

		parsed = self._parse_serialized(content)
		if not parsed:
			messagebox.showerror("Error", "Formato de archivo inválido.")
			return
		loaded_digits, numbers = parsed
		# Validate numbers against digits in entry (or use loaded digits if larger)
		try:
			current_digits = int(self.entry_digits.get().strip())
		except Exception:
			current_digits = loaded_digits
		digits = max(current_digits, 1)
		max_len_ok = all(len(str(abs(n))) == digits for n in numbers)
		if not max_len_ok:
			messagebox.showerror("Error", "Clave fuera de máximo dígito en archivo.")
			return

		# Accept and set digits to max(current, loaded)
		self.entry_digits.delete(0, tk.END)
		self.entry_digits.insert(0, str(max(digits, loaded_digits)))

		self._array = sorted(numbers)
		self._low = None
		self._high = None
		self._highlight_index = None
		self.status.configure(text=f"Cargado {len(self._array)} elementos desde archivo")
		self._draw()

	def _on_reset(self) -> None:
		self._array = []
		self._highlight_index = None
		self._low = None
		self._high = None
		self._delete_index = None
		self.status.configure(text="Reiniciado")
		self._draw()

	def _read_params(self) -> (int, int):
		try:
			n = int(self.entry_n.get())
		except ValueError:
			n = 10
		try:
			d = int(self.entry_digits.get())
		except ValueError:
			d = 4
		return max(0, n), max(1, d)

	def _validate_key(self, key_str: str, digits: int) -> Optional[int]:
		if not key_str.isdigit():
			messagebox.showerror("Error", "La clave debe ser numérica.")
			return None
		if len(key_str) != digits:
			messagebox.showerror("Error", f"La clave debe tener exactamente {digits} dígitos.")
			return None
		return int(key_str)

	def _on_generate(self) -> None:
		n, digits = self._read_params()
		max_value = 10 ** digits - 1
		min_value = 0 if digits == 1 else 10 ** (digits - 1)
		values = set()
		attempts = 0
		limit = max(1000, n * 10)
		while len(values) < n and attempts < limit and (max_value - min_value + 1) > len(values):
			values.add(random.randint(min_value, max_value))
			attempts += 1
		self._array = sorted(values)
		self._low = None
		self._high = None
		self._highlight_index = None
		self.status.configure(text=f"Generado {n} elementos, dígitos ≤ {digits}")
		self._draw()

	def _on_insert(self) -> None:
		_, digits = self._read_params()
		try:
			capacity = int(self.entry_n.get())
		except Exception:
			capacity = len(self._array)
		if len(self._array) >= max(0, capacity):
			messagebox.showerror("Error", "Capacidad alcanzada (n)")
			return
		key_str = self.entry_key.get().strip()
		value = self._validate_key(key_str, digits)
		if value is None:
			return
		# Insert maintaining sorted order with duplicate check
		lo, hi = 0, len(self._array)
		while lo < hi:
			mid = (lo + hi) // 2
			if self._array[mid] < value:
				lo = mid + 1
			else:
				hi = mid
		if lo < len(self._array) and self._array[lo] == value:
			messagebox.showerror("Duplicado", f"La clave {str(value).zfill(digits)} ya existe.")
			return
		self._array.insert(lo, value)
		self.status.configure(text=f"Insertado {value}")
		self._draw()

	def _on_delete(self) -> None:
		_, digits = self._read_params()
		key_str = self.entry_key.get().strip()
		value = self._validate_key(key_str, digits)
		if value is None:
			return

		lo, hi = 0, len(self._array) - 1
		self._low, self._high = lo, hi
		self._highlight_index = None
		self._delete_index = None
		self._draw()
		self.update_idletasks()

		while lo <= hi:
			mid = (lo + hi) // 2
			self._highlight_index = mid
			self._low, self._high = lo, hi
			self._draw()
			self.after(700)
			self.update_idletasks()

			if self._array[mid] == value:
				# highlight in red before deletion
				self._delete_index = mid
				self._draw()
				self.after(1400)
				self.update_idletasks()
				del self._array[mid]
				self._delete_index = None
				self._highlight_index = None
				self._low = None
				self._high = None
				self.status.configure(text=f"Eliminado {value}")
				self._draw()
				return
			elif self._array[mid] < value:
				lo = mid + 1
			else:
				hi = mid - 1

		self.status.configure(text=f"No encontrado {value}")
		self._highlight_index = None
		self._low = None
		self._high = None
		self._draw()
		messagebox.showinfo("Búsqueda", "Valor no encontrado")

	def _on_search(self) -> None:
		_, digits = self._read_params()
		key_str = self.entry_key.get().strip()
		value = self._validate_key(key_str, digits)
		if value is None:
			return

		lo, hi = 0, len(self._array) - 1
		self._low, self._high = lo, hi
		self._highlight_index = None
		self._draw()
		self.update_idletasks()

		while lo <= hi:
			mid = (lo + hi) // 2
			self._highlight_index = mid
			self._low, self._high = lo, hi
			self._draw()
			self.after(700)
			self.update_idletasks()

			if self._array[mid] == value:
				self.status.configure(text=f"Encontrado {value} en dirección {mid}")
				return
			elif self._array[mid] < value:
				lo = mid + 1
			else:
				hi = mid - 1

		self.status.configure(text="No encontrado")
		self._highlight_index = None
		self._draw()
		messagebox.showinfo("Búsqueda", "Valor no encontrado")

	def _draw(self) -> None:
		self.tree.delete(*self.tree.get_children())
		try:
			capacity = int(self.entry_n.get())
		except Exception:
			capacity = len(self._array)
		capacity = max(capacity, len(self._array))
		for idx in range(capacity):
			value = self._array[idx] if idx < len(self._array) else "-"
			if self._delete_index == idx:
				tags = ("delete",)
			elif self._highlight_index == idx:
				tags = ("mid",)
			elif (
				self._low is not None
				and self._high is not None
				and self._low <= self._high
				and idx < len(self._array)
				and self._low <= idx <= self._high
			):
				tags = ("inrange",)
			else:
				tags = ("normal",)
			self.tree.insert("", "end", values=(idx, value), tags=tags)


