import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional, Dict


class HashView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)

		title = ttk.Label(self, text="Función Hash", style="Title.TLabel")
		title.pack(pady=(20, 5))

		# Parámetros
		params = ttk.Frame(self, style="Panel.TFrame", padding=10)
		params.pack(fill=tk.X, padx=4, pady=6)

		lbl_n = ttk.Label(params, text="Rango (n):")
		lbl_n.grid(row=0, column=0, sticky="w", padx=(0, 6))
		self.entry_n = ttk.Entry(params, width=8)
		self.entry_n.insert(0, "10")
		self.entry_n.grid(row=0, column=1, padx=(0, 12))

		lbl_digits = ttk.Label(params, text="Dígitos clave:")
		lbl_digits.grid(row=0, column=2, sticky="w", padx=(0, 6))
		self.entry_digits = ttk.Entry(params, width=6)
		self.entry_digits.insert(0, "4")
		self.entry_digits.grid(row=0, column=3, padx=(0, 12))

		lbl_hash = ttk.Label(params, text="Función Hash:")
		lbl_hash.grid(row=0, column=4, sticky="w", padx=(0, 6))
		self.hash_mode = tk.StringVar(value="modulo")
		combo_hash = ttk.Combobox(params, values=["modulo", "cuadrado", "plegamiento", "truncamiento"], state="readonly", textvariable=self.hash_mode, width=14)
		combo_hash.grid(row=0, column=5, padx=(0, 12))

		# Segunda fila de parámetros
		lbl_probe = ttk.Label(params, text="Resolución colisión:")
		lbl_probe.grid(row=1, column=0, sticky="w", padx=(0, 6), pady=(6, 0))
		self.probe_mode = tk.StringVar(value="lineal")
		probe_combo = ttk.Combobox(
			params, 
			values=["lineal", "cuadrática", "doble hash", "arreglo anidado", "lista enlazada"], 
			state="readonly", 
			textvariable=self.probe_mode, 
			width=14
		)
		probe_combo.grid(row=1, column=1, columnspan=2, sticky="w", pady=(6, 0))
		probe_combo.bind("<<ComboboxSelected>>", self._on_probe_change)

		btn_new = ttk.Button(params, text="Generar datos", command=self._on_generate)
		btn_new.grid(row=1, column=4, columnspan=2, pady=(6, 0), sticky="w")

		# Panel paralelo
		panel = ttk.Frame(self, padding=6)
		panel.pack(fill=tk.BOTH, expand=True)

		ops = ttk.Frame(panel, style="Panel.TFrame", padding=10)
		ops.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

		lbl_key = ttk.Label(ops, text="Clave:")
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

		self.status = ttk.Label(ops, text="Estado: listo", wraplength=120)
		self.status.grid(row=6, column=0, pady=(12, 0), sticky="w")

		# Panel de visualización
		viz = ttk.Frame(panel, style="Panel.TFrame", padding=8)
		viz.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		# Crear Treeview con scroll
		tree_container = ttk.Frame(viz)
		tree_container.pack(fill=tk.BOTH, expand=True)
		
		self.tree = ttk.Treeview(tree_container, columns=("slot", "valor", "anidado"), show="headings", height=18)
		self.tree.heading("slot", text="Dirección")
		self.tree.heading("valor", text="Clave")
		self.tree.heading("anidado", text="Colisiones")
		self.tree.column("slot", width=80, anchor="center")
		self.tree.column("valor", width=120, anchor="center")
		self.tree.column("anidado", width=200, anchor="w")
		self.tree.tag_configure("normal", background="#ffffff")
		self.tree.tag_configure("hit", background="#cfe8ff")
		self.tree.tag_configure("delete", background="#ffd6d6")
		
		scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
		self.tree.configure(yscrollcommand=scroll.set)
		scroll.pack(side=tk.RIGHT, fill=tk.Y)
		self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

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

		# Estructuras de datos
		# Para lineal, cuadrática, doble_hash: lista simple
		self._table: List[Optional[int]] = []
		# Para arreglo_anidado: lista de listas
		self._table_anidado: List[List[int]] = []
		# Para lista_enlazada: lista de listas (cadenas)
		self._table_enlazada: List[List[int]] = []
		
		self._highlight: Optional[int] = None
		self._delete_index: Optional[int] = None
		self._on_init()

	def _on_probe_change(self, event=None) -> None:
		"""Reinicia la tabla cuando cambia el método de resolución"""
		self._on_init()
	
	def _configure_columns(self) -> None:
		"""Configura las columnas según el modo de resolución"""
		mode = self.probe_mode.get()
		
		if mode == "arreglo anidado":
			self.tree.heading("anidado", text="Arreglo Anidado")
			self.tree.column("anidado", width=200)
			self.tree.heading("valor", text="Clave")
			self.tree.column("valor", width=120)
		elif mode == "lista enlazada":
			self.tree.heading("anidado", text="")
			self.tree.column("anidado", width=0)
			self.tree.heading("valor", text="Lista Enlazada")
			self.tree.column("valor", width=300)
		else:
			self.tree.heading("anidado", text="")
			self.tree.column("anidado", width=0)
			self.tree.heading("valor", text="Clave")
			self.tree.column("valor", width=120)

	def _read_params(self) -> tuple:
		try:
			n = int(self.entry_n.get())
		except Exception:
			n = 10
		try:
			d = int(self.entry_digits.get())
		except Exception:
			d = 4
		return max(1, n), max(1, d)

	def _hash(self, k: int, n: int, d: int) -> int:
		"""Calcula el hash de una clave"""
		mode = self.hash_mode.get()
		table_size, _ = self._read_params()
		
		if mode == "modulo":
			return k % table_size
			
		elif mode == "cuadrado":
			# Cuadrado: toma dígitos centrales de K²
			k2 = k * k
			k2_str = str(k2).zfill(2 * d)
			center_len = d
			start = max(0, (len(k2_str) - center_len) // 2)
			center = int(k2_str[start:start + center_len]) if k2_str[start:start + center_len] else 0
			return center % table_size
			
		elif mode == "plegamiento":
			# Plegamiento: H(K) = dig_men_sig(K) + 1
			# El tamaño de parte depende de los dígitos de N (cantidad de ceros)
			# n=10 → 1 dígito → partes de 1: 1035 → 1*0*3*5
			# n=100 → 2 dígitos → partes de 2: 1035 → 10*35
			k_str = str(k)
			
			# Calcular tamaño de parte según dígitos de table_size
			part_size = len(str(table_size)) - 1  # n=10→1, n=100→2, n=1000→3
			if part_size < 1:
				part_size = 1
			
			# Dividir en partes y multiplicar
			parts = []
			for i in range(0, len(k_str), part_size):
				part = k_str[i:i + part_size]
				if part:
					parts.append(int(part))
			
			# Multiplicar todas las partes
			if not parts:
				result = 0
			elif len(parts) == 1:
				result = parts[0]
			else:
				result = 1
				for p in parts:
					result *= p
			
			# Tomar primeros dígitos (según part_size) de izquierda a derecha + 1
			result_str = str(result)
			if len(result_str) >= part_size:
				direccion = int(result_str[:part_size])
			else:
				direccion = result
			
			return (direccion + 1) % table_size
			
		elif mode == "truncamiento":
			# Truncamiento: H(K) = elegir_dig(d1, d2, ...) + 1
			# Cantidad de dígitos a elegir depende de N
			# n=10 → 1 dígito → elegir d1
			# n=100 → 2 dígitos → elegir d1, d2
			k_str = str(k).zfill(d)
			
			# Calcular cuántos dígitos elegir según table_size
			num_digits = len(str(table_size)) - 1  # n=10→1, n=100→2, n=1000→3
			if num_digits < 1:
				num_digits = 1
			
			# Elegir los primeros num_digits dígitos
			selected = k_str[:num_digits] if len(k_str) >= num_digits else k_str
			direccion = int(selected) if selected else 0
			
			return (direccion + 1) % table_size
		
		return k % table_size

	def _double_hash(self, d: int, n: int) -> int:
		"""Doble hash: H(D) = (D + 1) mod n + 1"""
		return ((d + 1) % n) + 1

	def _probe_indices(self, k: int, n: int, d: int):
		"""Genera índices de prueba según el método seleccionado"""
		base = self._hash(k, n, d)
		mode = self.probe_mode.get()
		
		if mode == "lineal":
			# D, D+1, D+2, D+3...
			for t in range(n):
				yield (base + t) % n
		elif mode == "cuadrática":
			# D, D+1², D+2², D+3²... (D+1, D+4, D+9...)
			for t in range(n):
				yield (base + t * t) % n
		elif mode == "doble hash":
			# Aplica doble hash a la dirección colisionada
			current = base
			visited = set()
			for _ in range(n):
				if current in visited:
					break
				visited.add(current)
				yield current
				current = (current + self._double_hash(current, n)) % n

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
		mode = self.probe_mode.get()
		self._configure_columns()
		
		if mode in ["lineal", "cuadrática", "doble hash"]:
			self._table = [None] * n
			self._table_anidado = []
			self._table_enlazada = []
		elif mode == "arreglo anidado":
			self._table = [None] * n
			self._table_anidado = [[] for _ in range(n)]
			self._table_enlazada = []
		else:  # lista enlazada
			self._table = []
			self._table_anidado = []
			self._table_enlazada = [[] for _ in range(n)]
		
		self._highlight = None
		self._delete_index = None
		self.status.configure(text=f"Tabla reiniciada (n={n})")
		self._draw()

	def _on_generate(self) -> None:
		n, d = self._read_params()
		self._on_init()
		
		max_value = 10 ** d - 1
		min_value = 10 ** (d - 1) if d > 1 else 0
		target = n  # Llenar todas las direcciones
		inserted = 0
		seen = set()
		attempts = 0
		max_attempts = target * 50
		
		mode = self.probe_mode.get()
		
		while inserted < target and attempts < max_attempts:
			attempts += 1
			k = random.randint(min_value, max_value)
			if k in seen:
				continue
			seen.add(k)
			
			if self._insert_key(k, n, d, animate=False):
				inserted += 1
		
		self.status.configure(text=f"Generados {inserted} elementos")
		self._draw()

	def _insert_key(self, k: int, n: int, d: int, animate: bool = True) -> bool:
		"""Inserta una clave según el método de resolución"""
		mode = self.probe_mode.get()
		base = self._hash(k, n, d)
		
		if mode in ["lineal", "cuadrática", "doble hash"]:
			# Verificar duplicado
			for idx in self._probe_indices(k, n, d):
				if self._table[idx] is None:
					break
				if self._table[idx] == k:
					return False  # Duplicado
			
			# Insertar
			for idx in self._probe_indices(k, n, d):
				if animate:
					self._highlight = idx
					self._draw()
					self.update_idletasks()
					self.after(300)
				if self._table[idx] is None:
					self._table[idx] = k
					return True
			return False  # Tabla llena
			
		elif mode == "arreglo anidado":
			# Verificar duplicado en posición base y anidados
			if self._table[base] == k:
				return False
			if k in self._table_anidado[base]:
				return False
			
			if animate:
				self._highlight = base
				self._draw()
				self.update_idletasks()
				self.after(300)
			
			if self._table[base] is None:
				self._table[base] = k
			else:
				self._table_anidado[base].append(k)
			return True
			
		else:  # lista enlazada
			# Verificar duplicado en la cadena
			if k in self._table_enlazada[base]:
				return False
			
			if animate:
				self._highlight = base
				self._draw()
				self.update_idletasks()
				self.after(300)
			
			self._table_enlazada[base].append(k)
			return True

	def _on_insert(self) -> None:
		n, d = self._read_params()
		key_str = self.entry_key.get().strip()
		k = self._validate_key(key_str, d)
		if k is None:
			return
		
		mode = self.probe_mode.get()
		
		# Verificar capacidad para métodos de direccionamiento abierto
		if mode in ["lineal", "cuadrática", "doble hash"]:
			if sum(1 for v in self._table if v is not None) >= n:
				messagebox.showerror("Error", "Tabla llena")
				return
		
		if self._insert_key(k, n, d, animate=True):
			base = self._hash(k, n, d)
			self.status.configure(text=f"Insertado {k} (hash={base})")
			self._draw()
		else:
			messagebox.showerror("Error", "No se pudo insertar (duplicado o tabla llena)")

	def _on_search(self) -> None:
		n, d = self._read_params()
		key_str = self.entry_key.get().strip()
		k = self._validate_key(key_str, d)
		if k is None:
			return
		
		mode = self.probe_mode.get()
		base = self._hash(k, n, d)
		
		if mode in ["lineal", "cuadrática", "doble hash"]:
			for idx in self._probe_indices(k, n, d):
				if self._table[idx] is None:
					break
				self._highlight = idx
				self._draw()
				self.update_idletasks()
				self.after(500)
				if self._table[idx] == k:
					self.status.configure(text=f"Encontrado {k} en dirección {idx}")
					messagebox.showinfo("Búsqueda", f"Número encontrado en la dirección {idx}")
					return
					
		elif mode == "arreglo anidado":
			self._highlight = base
			self._draw()
			self.update_idletasks()
			self.after(500)
			
			if self._table[base] == k:
				self.status.configure(text=f"Encontrado {k} en dirección {base}")
				messagebox.showinfo("Búsqueda", f"Número encontrado en la dirección {base}")
				return
			if k in self._table_anidado[base]:
				pos = self._table_anidado[base].index(k)
				self.status.configure(text=f"Encontrado {k} en dirección {base}, colisión #{pos+1}")
				messagebox.showinfo("Búsqueda", f"Número encontrado en la dirección {base}, colisión #{pos+1}")
				return
				
		else:  # lista enlazada
			self._highlight = base
			self._draw()
			self.update_idletasks()
			self.after(500)
			
			if k in self._table_enlazada[base]:
				pos = self._table_enlazada[base].index(k)
				self.status.configure(text=f"Encontrado {k} en dirección {base}, posición {pos}")
				messagebox.showinfo("Búsqueda", f"Número encontrado en la dirección {base}, posición {pos}")
				return
		
		self._highlight = None
		self._draw()
		self.status.configure(text="No encontrado")
		messagebox.showinfo("Búsqueda", "Valor no encontrado")

	def _on_delete(self) -> None:
		n, d = self._read_params()
		key_str = self.entry_key.get().strip()
		k = self._validate_key(key_str, d)
		if k is None:
			return
		
		mode = self.probe_mode.get()
		base = self._hash(k, n, d)
		
		if mode in ["lineal", "cuadrática", "doble hash"]:
			for idx in self._probe_indices(k, n, d):
				if self._table[idx] is None:
					break
				self._highlight = idx
				self._draw()
				self.update_idletasks()
				self.after(500)
				if self._table[idx] == k:
					self._delete_index = idx
					self._draw()
					self.update_idletasks()
					self.after(800)
					self._table[idx] = None
					self._delete_index = None
					self._highlight = None
					self.status.configure(text=f"Eliminado {k}")
					self._draw()
					return
					
		elif mode == "arreglo anidado":
			self._highlight = base
			self._draw()
			self.update_idletasks()
			self.after(500)
			
			if self._table[base] == k:
				self._delete_index = base
				self._draw()
				self.update_idletasks()
				self.after(800)
				# Mover primer anidado a posición principal si existe
				if self._table_anidado[base]:
					self._table[base] = self._table_anidado[base].pop(0)
				else:
					self._table[base] = None
				self._delete_index = None
				self._highlight = None
				self.status.configure(text=f"Eliminado {k}")
				self._draw()
				return
			elif k in self._table_anidado[base]:
				self._delete_index = base
				self._draw()
				self.update_idletasks()
				self.after(800)
				self._table_anidado[base].remove(k)
				self._delete_index = None
				self._highlight = None
				self.status.configure(text=f"Eliminado {k}")
				self._draw()
				return
				
		else:  # lista enlazada
			self._highlight = base
			self._draw()
			self.update_idletasks()
			self.after(500)
			
			if k in self._table_enlazada[base]:
				self._delete_index = base
				self._draw()
				self.update_idletasks()
				self.after(800)
				self._table_enlazada[base].remove(k)
				self._delete_index = None
				self._highlight = None
				self.status.configure(text=f"Eliminado {k}")
				self._draw()
				return
		
		self._highlight = None
		self._draw()
		self.status.configure(text="No encontrado")
		messagebox.showinfo("Búsqueda", "Valor no encontrado")

	def _draw(self) -> None:
		self.tree.delete(*self.tree.get_children())
		n, d = self._read_params()
		mode = self.probe_mode.get()
		
		for idx in range(n):
			if self._delete_index == idx:
				tags = ("delete",)
			elif self._highlight == idx:
				tags = ("hit",)
			else:
				tags = ("normal",)
			
			if mode in ["lineal", "cuadrática", "doble hash"]:
				# Asegurar que la tabla tiene el tamaño correcto
				if len(self._table) <= idx:
					self._table.extend([None] * (idx + 1 - len(self._table)))
				val = self._table[idx]
				val_str = "-" if val is None else str(val).zfill(d)
				self.tree.insert("", "end", values=(idx, val_str, ""), tags=tags)
				
			elif mode == "arreglo anidado":
				if len(self._table) <= idx:
					self._table.extend([None] * (idx + 1 - len(self._table)))
				if len(self._table_anidado) <= idx:
					self._table_anidado.extend([[] for _ in range(idx + 1 - len(self._table_anidado))])
				
				val = self._table[idx]
				val_str = "-" if val is None else str(val).zfill(d)
				
				# Mostrar arreglo anidado
				anidados = self._table_anidado[idx]
				anidado_str = ", ".join(str(x).zfill(d) for x in anidados) if anidados else "-"
				
				self.tree.insert("", "end", values=(idx, val_str, anidado_str), tags=tags)
				
			else:  # lista enlazada
				if len(self._table_enlazada) <= idx:
					self._table_enlazada.extend([[] for _ in range(idx + 1 - len(self._table_enlazada))])
				
				cadena = self._table_enlazada[idx]
				if cadena:
					# Mostrar como: 2035 -> 4035 -> 6035
					val_str = " → ".join(str(x).zfill(d) for x in cadena)
				else:
					val_str = "-"
				
				self.tree.insert("", "end", values=(idx, val_str, ""), tags=tags)

	def _serialize(self) -> str:
		n, d = self._read_params()
		mode = self.probe_mode.get()
		
		lines = [
			f"n:{n}",
			f"d:{d}",
			f"hash:{self.hash_mode.get()}",
			f"probe:{mode}"
		]
		
		if mode in ["lineal", "cuadrática", "doble hash"]:
			vals = ["" if v is None else str(v) for v in self._table[:n]]
			lines.append(f"table:{','.join(vals)}")
		elif mode == "arreglo anidado":
			vals = ["" if v is None else str(v) for v in self._table[:n]]
			lines.append(f"table:{','.join(vals)}")
			for i, arr in enumerate(self._table_anidado[:n]):
				if arr:
					lines.append(f"anidado_{i}:{','.join(str(x) for x in arr)}")
		else:  # lista enlazada
			for i, cadena in enumerate(self._table_enlazada[:n]):
				if cadena:
					lines.append(f"lista_{i}:{','.join(str(x) for x in cadena)}")
		
		return "\n".join(lines) + "\n"

	def _parse(self, content: str):
		lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
		n = d = None
		hash_mode = "modulo"
		probe_mode = "lineal"
		table = []
		anidados: Dict[int, List[int]] = {}
		listas: Dict[int, List[int]] = {}
		
		for ln in lines:
			if ln.lower().startswith("n:"):
				n = int(ln.split(":", 1)[1])
			elif ln.lower().startswith("d:"):
				d = int(ln.split(":", 1)[1])
			elif ln.lower().startswith("hash:"):
				hash_mode = ln.split(":", 1)[1].strip()
			elif ln.lower().startswith("probe:"):
				probe_mode = ln.split(":", 1)[1].strip()
			elif ln.lower().startswith("table:"):
				parts = ln.split(":", 1)[1].split(",")
				table = [int(p) if p.strip() else None for p in parts]
			elif ln.lower().startswith("anidado_"):
				idx = int(ln.split("_")[1].split(":")[0])
				vals = [int(x) for x in ln.split(":", 1)[1].split(",") if x.strip()]
				anidados[idx] = vals
			elif ln.lower().startswith("lista_"):
				idx = int(ln.split("_")[1].split(":")[0])
				vals = [int(x) for x in ln.split(":", 1)[1].split(",") if x.strip()]
				listas[idx] = vals
		
		if n is None or d is None:
			return None
		return n, d, hash_mode, probe_mode, table, anidados, listas

	def _on_save(self) -> None:
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
		
		n, d, hash_mode, probe_mode, table, anidados, listas = parsed
		
		self.entry_n.delete(0, tk.END)
		self.entry_n.insert(0, str(n))
		self.entry_digits.delete(0, tk.END)
		self.entry_digits.insert(0, str(d))
		self.hash_mode.set(hash_mode if hash_mode in ("modulo", "cuadrado", "plegamiento", "truncamiento") else "modulo")
		self.probe_mode.set(probe_mode if probe_mode in ("lineal", "cuadrática", "doble hash", "arreglo anidado", "lista enlazada") else "lineal")
		
		if probe_mode in ["lineal", "cuadrática", "doble hash"]:
			self._table = table + [None] * (n - len(table))
			self._table_anidado = []
			self._table_enlazada = []
		elif probe_mode == "arreglo anidado":
			self._table = table + [None] * (n - len(table))
			self._table_anidado = [anidados.get(i, []) for i in range(n)]
			self._table_enlazada = []
		else:  # lista enlazada
			self._table = []
			self._table_anidado = []
			self._table_enlazada = [listas.get(i, []) for i in range(n)]
		
		self._highlight = None
		self._delete_index = None
		self.status.configure(text=f"Tabla cargada (n={n}, d={d})")
		self._draw()
