import math
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional, Dict, Any


class BloquesView(ttk.Frame):
	def __init__(self, parent: tk.Misc, app) -> None:
		super().__init__(parent)

		title = ttk.Label(self, text="Búsquedas por Bloques", style="Title.TLabel")
		title.pack(pady=(20, 5))

		# Section 1: Parámetros
		params = ttk.Frame(self, style="Panel.TFrame", padding=10)
		params.pack(fill=tk.X, padx=4, pady=6)

		lbl_n = ttk.Label(params, text="Número de registros (n):")
		lbl_n.grid(row=0, column=0, sticky="w", padx=(0, 6))
		self.entry_n = ttk.Entry(params, width=10)
		self.entry_n.insert(0, "16")
		self.entry_n.grid(row=0, column=1, padx=(0, 16))
		self.entry_n.bind("<KeyRelease>", self._on_n_change)

		lbl_b = ttk.Label(params, text="Número de bloques (B = ⌈√n⌉):")
		lbl_b.grid(row=0, column=2, sticky="w", padx=(0, 6))
		self.lbl_b_value = ttk.Label(params, text="4", style="TLabel")
		self.lbl_b_value.grid(row=0, column=3, padx=(0, 16))

		lbl_digits = ttk.Label(params, text="Dígitos de la clave:")
		lbl_digits.grid(row=0, column=4, sticky="w", padx=(0, 6))
		self.entry_digits = ttk.Entry(params, width=10)
		self.entry_digits.insert(0, "3")
		self.entry_digits.grid(row=0, column=5, padx=(0, 16))

		btn_generate = ttk.Button(params, text="Generar datos", command=self._on_generate)
		btn_generate.grid(row=0, column=6, padx=(0, 6))

		btn_gen_struct = ttk.Button(params, text="Generar estructura", command=self._on_generate_structure)
		btn_gen_struct.grid(row=0, column=7, padx=(0, 6))

		# Panel paralelo
		panel = ttk.Frame(self, padding=6)
		panel.pack(fill=tk.BOTH, expand=True)

		ops = ttk.Frame(panel, style="Panel.TFrame", padding=10)
		ops.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

		lbl_key = ttk.Label(ops, text="Clave:")
		lbl_key.grid(row=0, column=0, sticky="w")
		self.entry_key = ttk.Entry(ops, width=16)
		self.entry_key.grid(row=1, column=0, pady=(0, 10))

		btn_rebuild = ttk.Button(ops, text="Regenerar estructura", style="Retro.TButton", command=self._on_rebuild_structure)
		btn_rebuild.grid(row=2, column=0, pady=4, sticky="ew")

		btn_insert = ttk.Button(ops, text="Insertar", style="Retro.TButton", command=self._on_insert)
		btn_insert.grid(row=3, column=0, pady=4, sticky="ew")

		btn_delete = ttk.Button(ops, text="Eliminar", style="Retro.TButton", command=self._on_delete)
		btn_delete.grid(row=4, column=0, pady=4, sticky="ew")

		# Controles de búsqueda (lineal fija)
		btn_search = ttk.Button(ops, text="Buscar", style="Retro.TButton", command=self._on_search)
		btn_search.grid(row=5, column=0, pady=4, sticky="ew")

		btn_reset = ttk.Button(ops, text="Reiniciar", command=self._on_reset)
		btn_reset.grid(row=6, column=0, pady=4, sticky="ew")

		btn_clear = ttk.Button(ops, text="Borrar estructura", command=self._on_clear)
		btn_clear.grid(row=7, column=0, pady=4, sticky="ew")

		# Animation controls
		anim_lbl = ttk.Label(ops, text="Controles de animación")
		anim_lbl.grid(row=10, column=0, sticky="w", pady=(8, 2))
		btn_play = ttk.Button(ops, text="▶ Reproducir", command=self._on_play)
		btn_play.grid(row=11, column=0, pady=2, sticky="ew")
		btn_pause = ttk.Button(ops, text="⏸ Pausa", command=self._on_pause)
		btn_pause.grid(row=12, column=0, pady=2, sticky="ew")
		btn_next = ttk.Button(ops, text="Paso", command=self._on_next)
		btn_next.grid(row=13, column=0, pady=2, sticky="ew")
		btn_reset_anim = ttk.Button(ops, text="Reiniciar animación", command=self._on_reset_anim)
		btn_reset_anim.grid(row=14, column=0, pady=2, sticky="ew")

		# Botón de deshacer
		btn_undo = ttk.Button(ops, text="↶ Deshacer (Ctrl+Z)", command=self._on_undo)
		btn_undo.grid(row=15, column=0, pady=2, sticky="ew")

		self.status = ttk.Label(ops, text="Estado: listo")
		self.status.grid(row=16, column=0, pady=(12, 0), sticky="w")

		viz = ttk.Frame(panel, style="Panel.TFrame", padding=8)
		viz.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		# Canvas con scrollbar vertical
		canvas_wrap = ttk.Frame(viz)
		canvas_wrap.pack(fill=tk.BOTH, expand=True)
		self.canvas = tk.Canvas(canvas_wrap, background="#ffffff", height=460)
		self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		vscroll = ttk.Scrollbar(canvas_wrap, orient="vertical", command=self.canvas.yview)
		vscroll.pack(side=tk.RIGHT, fill=tk.Y)
		self.canvas.configure(yscrollcommand=vscroll.set)

		# Save/load panel
		file_panel = ttk.Frame(self, style="Panel.TFrame", padding=8)
		file_panel.pack(fill=tk.X, padx=4, pady=6)

		btn_save_close = ttk.Button(file_panel, text="Guardar y cerrar", command=self._on_save_and_close)
		btn_save_close.grid(row=0, column=0, padx=4, pady=2)

		btn_save = ttk.Button(file_panel, text="Guardar", command=self._on_save)
		btn_save.grid(row=0, column=1, padx=4, pady=2)

		btn_load = ttk.Button(file_panel, text="Cargar", command=self._on_load)
		btn_load.grid(row=0, column=2, padx=4, pady=2)

		back = ttk.Button(self, text="← Volver", command=lambda: app.navigate("externas"))
		back.pack(pady=6)

		self.app = app

		# Data structures
		self.n: int = 16
		self.b: int = 4
		self.block_size: int = 4
		self.blocks: List[List[int]] = []
		self._highlight_block: Optional[int] = None
		self._highlight_position: Optional[int] = None
		self._current_block: Optional[int] = None
		self._current_position: Optional[int] = None
		
		# Animation
		self._anim_steps: List[Dict[str, Any]] = []
		self._anim_index: int = 0
		self._anim_running: bool = False
		
		# Undo mechanism
		self._history: List[Dict[str, Any]] = []
		self._max_history = 20
		self.bind_all("<Control-z>", self._on_undo)

		self._initialize_blocks()
		# Esperar un poco antes de dibujar para que el canvas se inicialice correctamente
		self.after(100, self._draw)

	def _save_state(self) -> None:
		"""Guarda el estado actual en el historial"""
		current_state = {
			'n': self.n,
			'b': self.b,
			'block_size': self.block_size,
			'blocks': [block[:] for block in self.blocks]  # Deep copy
		}
		self._history.append(current_state)
		
		if len(self._history) > self._max_history:
			self._history.pop(0)

	def _on_n_change(self, event=None) -> None:
		"""Actualiza B cuando cambia n"""
		try:
			n = int(self.entry_n.get())
			if n > 0:
				b = int(math.sqrt(n))
				self.lbl_b_value.configure(text=str(b))
		except ValueError:
			pass

	def _read_params(self) -> tuple[int, int, int]:
		"""Lee los parámetros de la interfaz"""
		try:
			n = int(self.entry_n.get())
		except ValueError:
			n = 16
		try:
			digits = int(self.entry_digits.get())
		except ValueError:
			digits = 3
		
		n = max(1, n)
		b = math.ceil(math.sqrt(n))
		block_size = math.ceil(n / b) if b > 0 else n
		digits = max(1, digits)
		
		return n, b, digits

	def _validate_key(self, key_str: str, digits: int) -> Optional[int]:
		"""Valida una registro numérico con exactamente el número de dígitos especificado"""
		if not key_str.isdigit():
			messagebox.showerror("Error", "El registro debe ser numérico.")
			return None
		if len(key_str) != digits:
			messagebox.showerror("Error", f"El registro debe tener exactamente {digits} dígitos.")
			return None
		return int(key_str)

	def _initialize_blocks(self) -> None:
		"""Inicializa la estructura de bloques"""
		self.n, self.b, _ = self._read_params()
		self.block_size = math.ceil(self.n / self.b) if self.b > 0 else self.n
		self.blocks = [[] for _ in range(self.b)]
		self._highlight_block = None
		self._highlight_position = None
		self._current_block = None
		self._current_position = None

	def _on_generate(self) -> None:
		"""Genera datos aleatorios completos con exactamente el número de dígitos especificado"""
		self._save_state()
		
		n, b, digits = self._read_params()
		self.n, self.b = n, b
		self.block_size = math.ceil(n / b) if b > 0 else n
		
		# Generar números únicos con exactamente 'digits' dígitos
		min_value = 10 ** (digits - 1) if digits > 1 else 0  # Mínimo valor con 'digits' dígitos
		max_value = 10 ** digits - 1  # Máximo valor con 'digits' dígitos
		available_count = max_value - min_value + 1
		
		if n > available_count:
			messagebox.showwarning("Advertencia", f"Solo se pueden generar {available_count} números únicos con exactamente {digits} dígitos")
			n = available_count
		
		numbers = random.sample(range(min_value, max_value + 1), n)
		numbers.sort()
		
		# Distribuir en bloques
		self.blocks = [[] for _ in range(b)]
		for i, num in enumerate(numbers):
			block_idx = min(i // self.block_size, b - 1)
			self.blocks[block_idx].append(num)
		
		self.status.configure(text=f"Generados {len(numbers)} registros en {b} bloques")
		self._draw()

	def _on_generate_structure(self) -> None:
		"""Genera/Regenera la estructura vacía con n, B y tamaño de bloque calculados"""
		self._save_state()
		n, b, _ = self._read_params()
		self.n, self.b = n, b
		self.block_size = math.ceil(n / b) if b > 0 else n
		self.blocks = [[] for _ in range(b)]
		self.status.configure(text=f"Estructura generada (vacía): n={n}, B={b}, tamaño de bloque={self.block_size}")
		self._draw()


	def _key_exists(self, key: int) -> bool:
		"""Verifica si el registro ya existe en la estructura"""
		for block in self.blocks:
			if key in block:
				return True
		return False

	def _on_insert(self) -> None:
		"""Inserte  un registro manteniendo el orden"""
		_, _, digits = self._read_params()
		key_str = self.entry_key.get().strip()
		key = self._validate_key(key_str, digits)
		if key is None:
			return
		
		# Verificar si la clave ya existe
		if self._key_exists(key):
			messagebox.showwarning("Registro duplicado", f" El registro {key} ya existe en la estructura. No se permiten registros repetidos.")
			return
		
		self._save_state()
		
		# Verificar si hay espacio total disponible
		total_elements = sum(len(block) for block in self.blocks)
		if total_elements >= self.n:
			messagebox.showerror("Error", "La estructura está llena")
			return
		
		# Encontrar la posición correcta en toda la estructura (como lista continua)
		insert_position = 0
		for block_idx, block in enumerate(self.blocks):
			for pos, value in enumerate(block):
				if key <= value:
					# Encontramos la posición correcta
					insert_block_idx = block_idx
					insert_pos = pos
					
					# Insertar en la posición correcta
					block.insert(insert_pos, key)
					
					# Si el bloque se desborda, desplazar elementos hacia adelante
					if len(block) > self.block_size:
						# El último elemento debe moverse al siguiente bloque
						overflow_element = block.pop()
						
						# Buscar el siguiente bloque con espacio
						next_block_idx = insert_block_idx + 1
						while next_block_idx < len(self.blocks):
							if len(self.blocks[next_block_idx]) < self.block_size:
								# Insertar al inicio del siguiente bloque
								self.blocks[next_block_idx].insert(0, overflow_element)
								break
							else:
								# Este bloque también está lleno, desplazar su último elemento
								next_overflow = self.blocks[next_block_idx].pop()
								self.blocks[next_block_idx].insert(0, overflow_element)
								overflow_element = next_overflow
								next_block_idx += 1
						else:
							# No hay más bloques, crear uno nuevo si es posible
							if len(self.blocks) < self.b:
								self.blocks.append([overflow_element])
							else:
								# No se puede insertar más
								messagebox.showerror("Error", "No hay espacio disponible")
								return
					
					self.status.configure(text=f"Insertado registro {key} en bloque {insert_block_idx}")
					self.entry_key.delete(0, tk.END)
					self._draw()
					return
				insert_position += 1
			insert_position += len(block)
		
		# Si llegamos aquí, el valor va al final
		# Buscar el último bloque con espacio
		for block_idx in range(len(self.blocks)):
			if len(self.blocks[block_idx]) < self.block_size:
				self.blocks[block_idx].append(key)
				self.status.configure(text=f"Insertado registro {key} en bloque {block_idx}")
				self.entry_key.delete(0, tk.END)
				self._draw()
				return
		
		# Si no hay espacio en ningún bloque existente, crear uno nuevo
		if len(self.blocks) < self.b:
			self.blocks.append([key])
			self.status.configure(text=f"Insertado registro {key} en nuevo bloque {len(self.blocks)-1}")
		else:
			messagebox.showerror("Error", "No hay espacio disponible")
			return
		
		self.entry_key.delete(0, tk.END)
		self._draw()

	def _on_delete(self) -> None:
		"""Elimina un registro y reorganiza los elementos hacia atrás"""
		_, _, digits = self._read_params()
		key_str = self.entry_key.get().strip()
		key = self._validate_key(key_str, digits)
		if key is None:
			return
		
		self._save_state()
		
		# Buscar y eliminar la clave
		found = False
		for block_idx, block in enumerate(self.blocks):
			if key in block:
				block.remove(key)
				found = True
				self.status.configure(text=f"Eliminado registro {key} del bloque {block_idx}")
				
				# Reorganizar elementos hacia atrás para llenar espacios vacíos
				# Recopilar todos los elementos restantes
				all_elements = []
				for b in self.blocks:
					all_elements.extend(b)
				
				# Reorganizar en bloques manteniendo el orden
				self.blocks = [[] for _ in range(self.b)]
				for i, num in enumerate(all_elements):
					block_idx_new = min(i // self.block_size, self.b - 1)
					self.blocks[block_idx_new].append(num)
				
				self.entry_key.delete(0, tk.END)
				self._draw()
				return
		
		if not found:
			messagebox.showinfo("Búsqueda", "Registro no encontrado")

	def _on_search(self) -> None:
		"""Realiza búsqueda por bloques"""
		_, _, digits = self._read_params()
		key_str = self.entry_key.get().strip()
		key = self._validate_key(key_str, digits)
		if key is None:
			return
		
		# Búsqueda lineal fija (externas - Lineal)
		self._anim_steps = []
		self._highlight_block = None
		self._highlight_position = None
		self._search_sequential_blocks(key)
		
		self._prepare_animation()
		# Iniciar la animación automáticamente
		if self._anim_steps:
			self._anim_index = 0
			self._anim_running = True
			self._anim_step()

	def _search_binary_blocks(self, key: int) -> None:
		"""Búsqueda binaria entre bloques"""
		self._anim_steps.append({
			'type': 'start',
			'message': f'Iniciando búsqueda binaria de {key}',
			'highlight_block': None,
			'highlight_position': None
		})
		
		left, right = 0, len(self.blocks) - 1
		target_block = -1
		
		while left <= right:
			mid = (left + right) // 2
			
			# Mostrar bloque actual siendo evaluado
			self._anim_steps.append({
				'type': 'check_block',
				'message': f'Evaluando bloque {mid}',
				'highlight_block': mid,
				'highlight_position': None,
				'left': left,
				'right': right,
				'mid': mid
			})
			
			if not self.blocks[mid]:
				right = mid - 1
				continue
			
			last_element = self.blocks[mid][-1]
			
			# Mostrar comparación con último elemento
			self._anim_steps.append({
				'type': 'compare',
				'message': f'¿{key} ≤ {last_element}? (último elemento del bloque {mid})',
				'highlight_block': mid,
				'highlight_position': len(self.blocks[mid]) - 1,
				'comparing': True
			})
			
			if key <= last_element:
				target_block = mid
				right = mid - 1
				self._anim_steps.append({
					'type': 'decision',
					'message': f'Sí, {key} ≤ {last_element}. El bloque podría estar aquí o a la izquierda',
					'highlight_block': mid,
					'highlight_position': len(self.blocks[mid]) - 1
				})
			else:
				left = mid + 1
				self._anim_steps.append({
					'type': 'decision',
					'message': f'No, {key} > {last_element}. Buscar en bloques de la derecha',
					'highlight_block': mid,
					'highlight_position': len(self.blocks[mid]) - 1
				})
		
		if target_block >= 0:
			self._search_within_block(target_block, key)
		else:
			self._anim_steps.append({
				'type': 'not_found',
				'message': 'Valor no encontrado en ningún bloque',
				'highlight_block': None,
				'highlight_position': None
			})

	def _search_sequential_blocks(self, key: int) -> None:
		"""Búsqueda secuencial entre bloques"""
		self._anim_steps.append({
			'type': 'start',
			'message': f'Iniciando búsqueda secuencial de {key}',
			'highlight_block': None,
			'highlight_position': None
		})
		
		for block_idx in range(len(self.blocks)):
			if not self.blocks[block_idx]:
				continue
			
			# Mostrar bloque actual
			self._anim_steps.append({
				'type': 'check_block',
				'message': f'Evaluando bloque {block_idx}',
				'highlight_block': block_idx,
				'highlight_position': None
			})
			
			last_element = self.blocks[block_idx][-1]
			
			# Mostrar comparación
			self._anim_steps.append({
				'type': 'compare',
				'message': f'¿{key} ≤ {last_element}? (último elemento del bloque {block_idx})',
				'highlight_block': block_idx,
				'highlight_position': len(self.blocks[block_idx]) - 1,
				'comparing': True
			})
			
			if key <= last_element:
				self._anim_steps.append({
					'type': 'decision',
					'message': f'Sí, {key} ≤ {last_element}. Buscar en este bloque',
					'highlight_block': block_idx,
					'highlight_position': len(self.blocks[block_idx]) - 1
				})
				self._search_within_block(block_idx, key)
				return
			else:
				self._anim_steps.append({
					'type': 'decision',
					'message': f'No, {key} > {last_element}. Continuar con siguiente bloque',
					'highlight_block': block_idx,
					'highlight_position': len(self.blocks[block_idx]) - 1
				})
		
		self._anim_steps.append({
			'type': 'not_found',
			'message': 'Valor no encontrado en ningún bloque',
			'highlight_block': None,
			'highlight_position': None
		})

	def _search_within_block(self, block_idx: int, key: int) -> None:
		"""Búsqueda lineal dentro del bloque"""
		self._anim_steps.append({
			'type': 'block_search_start',
			'message': f'Iniciando búsqueda lineal en bloque {block_idx}',
			'highlight_block': block_idx,
			'highlight_position': None
		})
		
		block = self.blocks[block_idx]
		for pos, value in enumerate(block):
			self._anim_steps.append({
				'type': 'linear_check',
				'message': f'Comparando {key} con {value} en posición {pos}',
				'highlight_block': block_idx,
				'highlight_position': pos,
				'comparing': True
			})
			
			if value == key:
				self._anim_steps.append({
					'type': 'found',
					'message': f'¡Encontrado! {key} en bloque {block_idx}, posición {pos}',
					'highlight_block': block_idx,
					'highlight_position': pos
				})
				return
			elif value > key:
				break
		
		self._anim_steps.append({
			'type': 'not_found',
			'message': f'Valor {key} no encontrado en bloque {block_idx}',
			'highlight_block': block_idx,
			'highlight_position': None
		})

	def _on_rebuild_structure(self) -> None:
		"""Regenera la estructura con los parámetros actuales manteniendo los datos"""
		if not any(self.blocks):  # Si no hay datos
			messagebox.showinfo("Información", "No hay datos para reorganizar. Use 'Generar datos' primero.")
			return
		
		self._save_state()
		
		# Recopilar todos los datos actuales
		all_data = []
		for block in self.blocks:
			all_data.extend(block)
		
		if not all_data:
			messagebox.showinfo("Información", "No hay datos para reorganizar.")
			return
		
		# Leer nuevos parámetros
		n, b, digits = self._read_params()
		self.n, self.b = n, b
		self.block_size = math.ceil(n / b) if b > 0 else n
		
		# Reorganizar los datos existentes en la nueva estructura
		all_data.sort()  # Asegurar que estén ordenados
		self.blocks = [[] for _ in range(b)]
		
		for i, num in enumerate(all_data):
			block_idx = min(i // self.block_size, b - 1)
			self.blocks[block_idx].append(num)
		
		self.status.configure(text=f"Estructura reorganizada: {len(all_data)} elementos en {b} bloques")
		self._draw()

	def _on_reset(self) -> None:
		"""Reinicia la estructura"""
		self._save_state()
		self._initialize_blocks()
		self.status.configure(text="Estructura reiniciada")
		self._draw()

	def _on_clear(self) -> None:
		"""Borra por completo la estructura actual (todos los bloques vacíos)"""
		if not any(self.blocks):
			self.status.configure(text="Estructura ya vacía")
			return
		self._save_state()
		self.blocks = [[] for _ in range(self.b)]
		self.status.configure(text="Estructura borrada")
		self._draw()

	def _on_undo(self, event=None) -> None:
		"""Deshace la última operación"""
		if not self._history:
			self.status.configure(text="No hay operaciones para deshacer")
			messagebox.showinfo("Deshacer", "No hay operaciones para deshacer")
			return
		
		last_state = self._history.pop()
		self.n = last_state['n']
		self.b = last_state['b']
		self.block_size = last_state['block_size']
		self.blocks = last_state['blocks']
		
		self.entry_n.delete(0, tk.END)
		self.entry_n.insert(0, str(self.n))
		self.lbl_b_value.configure(text=str(self.b))
		
		self.status.configure(text=f"Operación deshecha. Estados restantes: {len(self._history)}")
		self._draw()

	def _prepare_animation(self) -> None:
		"""Prepara la animación"""
		self._anim_index = 0
		self._anim_running = False
		self.status.configure(text=f"Animación lista: {len(self._anim_steps)} pasos")

	def _anim_step(self) -> None:
		"""Ejecuta un paso de la animación"""
		if self._anim_index >= len(self._anim_steps):
			self._anim_running = False
			self.status.configure(text="Animación terminada")
			# Verificar si necesitamos mostrar mensaje de "no encontrado"
			if self._anim_steps and self._anim_steps[-1]['type'] == 'not_found':
				messagebox.showinfo("Búsqueda", "Registro no encontrado")
			return
		
		step = self._anim_steps[self._anim_index]
		self._highlight_block = step.get('highlight_block')
		self._highlight_position = step.get('highlight_position')
		
		self.status.configure(text=step['message'])
		self._draw()  # Redibujar para mostrar los cambios de resaltado
		
		self._anim_index += 1
		if self._anim_running and self._anim_index < len(self._anim_steps):
			self.after(1200, self._anim_step)  # Un poco más lento para ver mejor

	def _on_play(self) -> None:
		"""Reproduce la animación"""
		if not self._anim_steps:
			return
		if self._anim_index >= len(self._anim_steps):
			self._anim_index = 0
		self._anim_running = True
		self._anim_step()

	def _on_pause(self) -> None:
		"""Pausa la animación"""
		self._anim_running = False

	def _on_next(self) -> None:
		"""Ejecuta el siguiente paso"""
		self._anim_running = False
		self._anim_step()

	def _on_reset_anim(self) -> None:
		"""Reinicia la animación"""
		self._anim_running = False
		self._anim_index = 0
		self._highlight_block = None
		self._highlight_position = None
		self._draw()

	def _serialize(self) -> str:
		"""Serializa el estado para guardar"""
		result = f"n:{self.n}\n"
		result += f"b:{self.b}\n"
		result += f"block_size:{self.block_size}\n"
		
		for i, block in enumerate(self.blocks):
			if block:
				result += f"block_{i}:{','.join(map(str, block))}\n"
		
		return result

	def _parse(self, content: str) -> bool:
		"""Parsea el contenido de un archivo"""
		lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
		
		try:
			for line in lines:
				if line.startswith("n:"):
					self.n = int(line[2:])
				elif line.startswith("b:"):
					self.b = int(line[2:])
				elif line.startswith("block_size:"):
					self.block_size = int(line[11:])
				elif line.startswith("block_"):
					parts = line.split(":", 1)
					block_idx = int(parts[0].split("_")[1])
					values = [int(x) for x in parts[1].split(",") if x.strip()]
					
					# Asegurar que tenemos suficientes bloques
					while len(self.blocks) <= block_idx:
						self.blocks.append([])
					
					self.blocks[block_idx] = values
			
			# Actualizar interfaz
			self.entry_n.delete(0, tk.END)
			self.entry_n.insert(0, str(self.n))
			self.lbl_b_value.configure(text=str(self.b))
			
			return True
		except Exception:
			return False

	def _on_save(self) -> None:
		"""Guarda la estructura"""
		path = filedialog.asksaveasfilename(
			title="Guardar estructura de bloques",
			defaultextension=".txt",
			filetypes=[("Texto", "*.txt")]
		)
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Estructura guardada correctamente")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_save_and_close(self) -> None:
		"""Guarda y cierra"""
		path = filedialog.asksaveasfilename(
			title="Guardar estructura de bloques",
			defaultextension=".txt",
			filetypes=[("Texto", "*.txt")]
		)
		if not path:
			return
		try:
			with open(path, "w", encoding="utf-8") as f:
				f.write(self._serialize())
			messagebox.showinfo("Éxito", "Estructura guardada correctamente")
			self.app.navigate("externas")
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo guardar: {e}")

	def _on_load(self) -> None:
		"""Carga una estructura"""
		self._save_state()
		
		path = filedialog.askopenfilename(
			title="Cargar estructura de bloques",
			filetypes=[("Texto", "*.txt")]
		)
		if not path:
			if self._history:
				self._history.pop()
			return
		
		try:
			with open(path, "r", encoding="utf-8") as f:
				content = f.read()
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo leer: {e}")
			if self._history:
				self._history.pop()
			return
		
		self.blocks = []
		success = self._parse(content)
		if not success:
			messagebox.showerror("Error", "Formato inválido")
			if self._history:
				self._history.pop()
			return
		
		self.status.configure(text="Estructura cargada")
		self._draw()

	def _draw(self) -> None:
		"""Dibuja la estructura de bloques"""
		self.canvas.delete("all")
		
		if not self.blocks:
			# Mostrar mensaje cuando no hay bloques
			self.canvas.update_idletasks()
			width = max(self.canvas.winfo_width(), 600)
			height = max(self.canvas.winfo_height(), 400)
			self.canvas.create_text(
				width // 2, height // 2,
				text="Haga clic en 'Generar datos' para crear la estructura de bloques",
				fill="#666666", font=("MS Sans Serif", 12)
			)
			return
		
		# Forzar actualización del canvas para obtener dimensiones correctas
		self.canvas.update_idletasks()
		width = max(self.canvas.winfo_width(), 600)
		height = max(self.canvas.winfo_height(), 400)
		
		# Configuración para una sola columna de bloques
		block_width = min(200, max(150, width - 100))
		cell_height = 25
		gap_y = 15
		start_x = (width - block_width) // 2
		start_y = 50
		max_bottom = start_y
		
		# Determinar qué bloques mostrar
		total_blocks = len(self.blocks)
		blocks_to_draw: List[Optional[int]] = []
		
		if total_blocks <= 5:
			# Mostrar todos los bloques cuando la estructura es pequeña
			blocks_to_draw = list(range(total_blocks))
		else:
			# Encontrar el último bloque que tiene datos
			last_block_with_data = -1
			for i in range(total_blocks - 1, -1, -1):
				if self.blocks[i]:
					last_block_with_data = i
					break
			
			# Índice máximo visible por defecto (primeros 5 bloques: 0..4)
			initial_visible_end = 4
			visible_end = initial_visible_end
			
			if last_block_with_data >= 0:
				visible_end = max(visible_end, last_block_with_data)
			
			# Asegurar que el bloque resaltado sea visible
			if self._highlight_block is not None:
				visible_end = max(visible_end, min(self._highlight_block, total_blocks - 1))
			
			visible_end = min(visible_end, total_blocks - 1)
			
			blocks_to_draw = list(range(visible_end + 1))
			
			# Si todavía hay bloques ocultos, mostrar "..." y el último bloque
			if visible_end < total_blocks - 1:
				blocks_to_draw.append(None)
				blocks_to_draw.append(total_blocks - 1)
		
		# Dibujar bloques en una sola columna
		visual_idx = 0
		for block_idx in blocks_to_draw:
			if block_idx is None:
				# Dibujar "..."
				block_y = start_y + visual_idx * ((30 + self.block_size * (cell_height + 2)) + gap_y)
				self.canvas.create_text(
					start_x + block_width // 2, block_y + 15,
					text="...", fill="#666666", font=("MS Sans Serif", 12, "bold")
				)
				visual_idx += 1
				continue
			
			block = self.blocks[block_idx]
			block_x = start_x
			block_y = start_y + visual_idx * ((30 + self.block_size * (cell_height + 2)) + gap_y)
			
			# Color del bloque
			block_color = "#4da3ff" if block_idx == self._highlight_block else "#e0e0e0"
			outline_color = "#255eaa" if block_idx == self._highlight_block else "#808080"
			
			# Dibujar header del bloque
			self.canvas.create_rectangle(
				block_x, block_y, block_x + block_width, block_y + 30,
				fill=block_color, outline=outline_color, width=2
			)
			self.canvas.create_text(
				block_x + block_width // 2, block_y + 15,
				text=f"Bloque {block_idx + 1}", fill="#000000", font=("MS Sans Serif", 10, "bold")
			)
			
			# Dibujar celdas del bloque
			cell_y = block_y + 35
			for pos, value in enumerate(block):
				cell_color = "#ff6666" if (block_idx == self._highlight_block and pos == self._highlight_position) else "#ffffff"
				text_color = "#ffffff" if cell_color == "#ff6666" else "#000000"
				
				self.canvas.create_rectangle(
					block_x, cell_y, block_x + block_width, cell_y + cell_height,
					fill=cell_color, outline="#808080", width=1
				)
				self.canvas.create_text(
					block_x + block_width // 2, cell_y + cell_height // 2,
					text=str(value), fill=text_color, font=("MS Sans Serif", 9)
				)
				
				cell_y += cell_height + 2
			
			# Mostrar espacios vacíos si el bloque no está lleno
			remaining_slots = max(0, self.block_size - len(block))
			for _ in range(remaining_slots):
				self.canvas.create_rectangle(
					block_x, cell_y, block_x + block_width, cell_y + cell_height,
					fill="#f5f5f5", outline="#cccccc", width=1, stipple="gray25"
				)
				cell_y += cell_height + 2
			# Actualizar fondo máximo para scroll
			max_bottom = max(max_bottom, cell_y)
			visual_idx += 1
		
		# Información adicional
		info_text = f"n={self.n}, B={self.b}, Tamaño de bloque={self.block_size}"
		self.canvas.create_text(
			width // 2, height - 30,
			text=info_text, fill="#666666", font=("MS Sans Serif", 9)
		)
		# Definir región de scroll
		self.canvas.configure(scrollregion=(0, 0, width, max(height, max_bottom + 40)))