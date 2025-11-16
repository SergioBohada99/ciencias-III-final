import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional


class HashView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)

		title = ttk.Label(self, text="Función hash", style="Title.TLabel")
		title.pack(pady=(20, 5))

		# Parámetros (alineado a binaria/lineal)
		params = ttk.Frame(self, style="Panel.TFrame", padding=10)
		params.pack(fill=tk.X, padx=4, pady=6)

		lbl_n = ttk.Label(params, text="Tamaño tabla (n):")
		lbl_n.grid(row=0, column=0, sticky="w", padx=(0, 6))
		self.entry_n = ttk.Entry(params, width=10)
		self.entry_n.insert(0, "10")
		self.entry_n.grid(row=0, column=1, padx=(0, 16))

		lbl_digits = ttk.Label(params, text="Dígitos de la clave (numérica):")
		lbl_digits.grid(row=0, column=2, sticky="w", padx=(0, 6))
		self.entry_digits = ttk.Entry(params, width=10)
		self.entry_digits.insert(0, "3")
		self.entry_digits.grid(row=0, column=3, padx=(0, 16))

		lbl_hash = ttk.Label(params, text="Hash:")
		lbl_hash.grid(row=0, column=4, sticky="w", padx=(0, 6))
		self.hash_mode = tk.StringVar(value="modulo")
		combo = ttk.Combobox(params, values=["modulo", "centro_cuadrado"], state="readonly", textvariable=self.hash_mode, width=16)
		combo.grid(row=0, column=5, padx=(0, 6))

		# Resolución de colisión: combobox en barra superior
		lbl_probe = ttk.Label(params, text="Resolución de colisión:")
		lbl_probe.grid(row=0, column=6, sticky="w", padx=(12, 6))
		self.probe_mode = tk.StringVar(value="lineal")
		probe_combo = ttk.Combobox(params, values=["lineal", "cuadratica", "doble_hash"], state="readonly", textvariable=self.probe_mode, width=12)
		probe_combo.grid(row=0, column=7)

		btn_new = ttk.Button(params, text="Generar datos", command=self._on_generate)
		btn_new.grid(row=0, column=8, padx=(8, 0))

		# Panel paralelo
		panel = ttk.Frame(self, padding=6)
		panel.pack(fill=tk.BOTH, expand=True)

		ops = ttk.Frame(panel, style="Panel.TFrame", padding=10)
		ops.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

		# Tabs eliminadas; UI simplificada

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

		btn_reset = ttk.Button(ops, text="Reiniciar", command=self._on_init)
		btn_reset.grid(row=5, column=0, pady=4, sticky="ew")

		self.status = ttk.Label(ops, text="Estado: listo")
		self.status.grid(row=6, column=0, pady=(12, 0), sticky="w")

		viz = ttk.Frame(panel, style="Panel.TFrame", padding=8)
		viz.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.tree = ttk.Treeview(viz, columns=("slot", "valor"), show="headings", height=18)
		self.tree.heading("slot", text="Dirección")
		self.tree.heading("valor", text="Clave")	
		self.tree.column("slot", width=100, anchor="center")
		self.tree.column("valor", width=140, anchor="center")
		self.tree.tag_configure("normal", background="#ffffff")
		self.tree.tag_configure("hit", background="#cfe8ff")
		self.tree.tag_configure("delete", background="#ffd6d6")
		self.tree.pack(fill=tk.BOTH, expand=True)

		# Save/load panel
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

		self._table: List[Optional[int]] = []
		self._highlight: Optional[int] = None
		self._delete_index: Optional[int] = None
		self._on_init()

	def _read_params(self) -> (int, int):
		try:
			n = int(self.entry_n.get())
		except Exception:
			n = 10
		try:
			d = int(self.entry_digits.get())
		except Exception:
			d = 3
		return max(1, n), max(1, d)

	def _hash(self, k: int, n: int, d: int) -> int:
		mode = self.hash_mode.get()
		if mode == "modulo":
			return (k % n)
		# centro del cuadrado: dig_cent(K^2) + 1 (ajuste a 0-index internamente)
		k2 = k * k
		k2_str = str(k2).zfill(2 * d)
		center_len = d
		start = max(0, (len(k2_str) - center_len) // 2)
		center = int(k2_str[start:start + center_len]) if k2_str[start:start + center_len] else 0
		return center % n

	def _secondary_hash(self, k: int, n: int) -> int:
		# Standard double-hash step avoiding 0
		return 1 + (k % (n - 1)) if n > 1 else 1

	def _probe_indices(self, k: int, n: int, d: int):
		base = self._hash(k, n, d)
		mode = self.probe_mode.get()
		if mode == "lineal":
			for t in range(n):
				yield (base + t) % n
		elif mode == "cuadratica":
			for t in range(n):
				yield (base + t * t) % n
		else:  # doble_hash
			step = self._secondary_hash(k, n)
			for t in range(n):
				yield (base + t * step) % n

	def _validate_key(self, s: str, d: int) -> Optional[int]:
		if not s.isdigit():
			messagebox.showerror("Error", "La clave debe ser numérica.")
			return None
		if len(s) != d:
			messagebox.showerror("Error", f"La clave debe tener exactamente {d} dígitos.")
			return None
		return int(s)

	def _on_init(self) -> None:
		n, _ = self._read_params()
		self._table = [None] * n
		self._highlight = None
		self._delete_index = None
		self.status.configure(text=f"Tabla reiniciada (n={n})")
		self._draw()

	def _on_generate(self) -> None:
		n, d = self._read_params()
		self._table = [None] * n
		self._highlight = None
		self._delete_index = None
		max_value = max(1, 10 ** d - 1)
		min_value = 0 if d == 1 else 10 ** (d - 1)
		target = max(1, min(n, n // 2))
		inserted = 0
		seen = set()
		attempts = 0
		max_attempts = max(50, target * 10)
		while inserted < target and attempts < max_attempts:
			attempts += 1
			k = random.randint(min_value, max_value)
			if k in seen:
				continue
			seen.add(k)
			placed = False
			for idx in self._probe_indices(k, n, d):
				if self._table[idx] is None:
					self._table[idx] = k
					placed = True
					inserted += 1
					break
			if not placed:
				break
		self.status.configure(text=f"Generados {inserted} elementos (n={n}, d={d})")
		self._draw()

	def _on_insert(self) -> None:
		n, d = self._read_params()
		key_str = self.entry_key.get().strip()
		k = self._validate_key(key_str, d)
		if k is None:
			return
		# capacity check
		if sum(1 for v in self._table if v is not None) >= n:
			messagebox.showerror("Error", "Capacidad alcanzada (n)")
			return
		# duplicate check
		for idx in self._probe_indices(k, n, d):
			if self._table[idx] is None:
				break
			if self._table[idx] == k:
				messagebox.showerror("Duplicado", f"La clave {str(k).zfill(d)} ya existe en la tabla.")
				return
		i = self._hash(k, n, d)
		placed = False
		for idx in self._probe_indices(k, n, d):
			self._highlight = idx
			self._delete_index = None
			self._draw()
			self.update_idletasks()
			self.after(300)
			if self._table[idx] is None:
				self._table[idx] = k
				placed = True
				break
		if not placed:
			messagebox.showerror("Error", "Tabla llena")
			return
		self.status.configure(text=f"Insertado {k} en dirección {self._highlight}")
		self._draw()

	def _on_search(self) -> None:
		n, d = self._read_params()
		key_str = self.entry_key.get().strip()
		k = self._validate_key(key_str, d)
		if k is None:
			return
		for idx in self._probe_indices(k, n, d):
			if self._table[idx] is None:
				break
			self._highlight = idx
			self._delete_index = None
			self._draw()
			self.update_idletasks()
			self.after(700)
			if self._table[idx] == k:
				self.status.configure(text=f"Encontrado {k} en índice {idx}")
				return
		self.status.configure(text="No encontrado")
		self._highlight = None
		self._draw()
		messagebox.showinfo("Búsqueda", "Valor no encontrado")

	def _on_delete(self) -> None:
		n, d = self._read_params()
		key_str = self.entry_key.get().strip()
		k = self._validate_key(key_str, d)
		if k is None:
			return
		for idx in self._probe_indices(k, n, d):
			if self._table[idx] is None:
				break
			self._highlight = idx
			self._delete_index = None
			self._draw()
			self.update_idletasks()
			self.after(700)
			if self._table[idx] == k:
				self._delete_index = idx
				self._draw()
				self.update_idletasks()
				self.after(1400)
				self._table[idx] = None
				self._delete_index = None
				self._highlight = None
				self.status.configure(text=f"Eliminado {k} de dirección {idx}")
				self._draw()
				return
		self.status.configure(text="No encontrado")
		self._highlight = None
		self._draw()
		messagebox.showinfo("Búsqueda", "Valor no encontrado")

	def _serialize(self) -> str:
		n, d = self._read_params()
		vals = ["" if v is None else str(v) for v in self._table]
		return f"n:{n}\nd:{d}\nmode:{self.hash_mode.get()}\nprobe:{self.probe_mode.get()}\narray:{','.join(vals)}\n"

	def _parse(self, content: str) -> Optional[tuple[int, int, str, List[Optional[int]]]]:
		lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
		n = d = None
		mode = "modulo"
		arr: List[Optional[int]] = []
		for ln in lines:
			if ln.lower().startswith("n:"):
				n = int(ln.split(":", 1)[1])
			elif ln.lower().startswith("d:"):
				d = int(ln.split(":", 1)[1])
			elif ln.lower().startswith("mode:"):
				mode = ln.split(":", 1)[1].strip()
			elif ln.lower().startswith("probe:"):
				probe = ln.split(":", 1)[1].strip()
			elif ln.lower().startswith("array:"):
				parts = ln.split(":", 1)[1].split(",")
				arr = [int(p) if p.strip() != "" else None for p in parts]
		if n is None or d is None or not isinstance(arr, list):
			return None
		return n, d, mode, arr, locals().get("probe", "lineal")

	def _on_save(self) -> None:
		if not self._table:
			if not messagebox.askyesno("Guardar", "La tabla está vacía. ¿Guardar de todos modos?"):
				return
		path = filedialog.asksaveasfilename(title="Guardar tabla", defaultextension=".txt", filetypes=[("Texto", "*.txt")])
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Tabla guardada correctamente")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_save_and_close(self) -> None:
		if not self._table:
			if not messagebox.askyesno("Guardar", "La tabla está vacía. ¿Guardar de todos modos?"):
				return
		path = filedialog.asksaveasfilename(title="Guardar tabla", defaultextension=".txt", filetypes=[("Texto", "*.txt")])
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Tabla guardada correctamente")
			self.app.navigate("internas")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_load(self) -> None:
		path = filedialog.askopenfilename(title="Cargar tabla", filetypes=[("Texto", "*.txt")])
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
		n, d, mode, arr, probe = parsed
		self.entry_n.delete(0, tk.END)
		self.entry_n.insert(0, str(n))
		self.entry_digits.delete(0, tk.END)
		self.entry_digits.insert(0, str(d))
		self.hash_mode.set(mode if mode in ("modulo", "cuadrada") else "modulo")
		# set probe tab
		if probe not in ("lineal", "cuadratica", "doble_hash"):
			probe = "lineal"
		self.probe_mode.set(probe)
		# validate arr size
		if len(arr) != n:
			messagebox.showerror("Error", "Tamaño de tabla no coincide con n")
			return
		# validate digits (exact length)
		for v in arr:
			if v is None:
				continue
			if not isinstance(v, int) or len(str(v)) != d:
				messagebox.showerror("Error", f"Clave debe tener exactamente {d} dígitos")
				return
		self._table = arr
		self._highlight = None
		self._delete_index = None
		self.status.configure(text=f"Tabla cargada (n={n}, d={d}, {self.hash_mode.get()})")
		self._draw()

	def _draw(self) -> None:
		self.tree.delete(*self.tree.get_children())
		n, _ = self._read_params()
		# ensure table displays exactly n rows, fill with '-'
		if len(self._table) < n:
			self._table += [None] * (n - len(self._table))
		for idx in range(n):
			val = self._table[idx]
			if self._delete_index == idx:
				tags = ("delete",)
			elif self._highlight == idx:
				tags = ("hit",)
			else:
				tags = ("normal",)
			self.tree.insert("", "end", values=(idx, "-" if val is None else val), tags=tags)


