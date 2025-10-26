# Ciencias de la Computación II - Aplicación de Búsquedas

Una aplicación educativa desarrollada en Python con Tkinter que implementa diversos algoritmos de búsqueda y estructuras de datos para el estudio de Ciencias de la Computación II.

## 🚀 Características Principales

- **Interfaz retro estilo Windows 95/98** con tema personalizado
- **Búsquedas internas**: lineal, binaria, hash, árboles digitales, Huffman
- **Búsquedas externas**: archivos de bloques, transformación de claves
- **Visualización interactiva** de algoritmos con animaciones
- **Persistencia de datos** con guardado/carga de archivos
- **Validación estricta** de entrada de datos

## 📁 Estructura del Proyecto

```
App-Fn-v2/
├── main.py                          # Punto de entrada principal
├── README.md                        # Este archivo
├── app/                            # Módulo principal de la aplicación
│   ├── app.py                      # Clase principal RetroApp
│   ├── core/                       # Algoritmos centrales
│   │   └── __init__.py
│   ├── theme/                      # Sistema de temas
│   │   ├── __init__.py
│   │   └── retro.py                # Tema retro Windows 95/98
│   └── views/                       # Vistas de la interfaz
│       ├── home.py                 # Pantalla principal
│       ├── busquedas.py            # Menú de búsquedas
│       ├── internas.py             # Búsquedas internas
│       ├── externas.py             # Búsquedas externas
│       ├── busqueda_lineal.py      # Búsqueda lineal
│       ├── busqueda_binaria.py    # Búsqueda binaria
│       ├── hash_view.py            # Funciones hash
│       ├── trie_view.py            # Árbol digital (Trie)
│       ├── huffman_view.py         # Árboles de Huffman
│       ├── residuos_multiples_view.py # Árbol de residuos múltiples
│       ├── residuos_tree_view.py   # Árbol de residuos
│       ├── grafos.py               # Algoritmos de grafos
│       ├── bloques_view.py         # Búsqueda en bloques (lineal)
│       ├── bloques_binaria_view.py # Búsqueda en bloques (binaria)
│       ├── dinamicas_view.py       # Estructuras dinámicas
│       ├── indices_view.py         # Índices
│       └── transformacion_view.py  # Transformación de claves
└── [archivos de prueba]            # Archivos de datos de ejemplo
```

## 🛠️ Tecnologías Utilizadas

- **Python 3.x**
- **Tkinter** - Interfaz gráfica
- **ttk** - Widgets temáticos
- **typing** - Anotaciones de tipo
- **pathlib** - Manejo de rutas
- **random** - Generación de datos aleatorios

## 🚀 Instalación y Ejecución

### Requisitos

- Python 3.7 o superior
- Tkinter (incluido con Python)

### Ejecutar la aplicación

```bash
python main.py
```

## 📚 Módulos y Funcionalidades

### 🏠 Pantalla Principal (`home.py`)

- Navegación principal a búsquedas y grafos
- Interfaz de bienvenida

### 🔍 Búsquedas (`busquedas.py`)

- Menú de navegación entre búsquedas internas y externas

### 🔎 Búsquedas Internas (`internas.py`)

- **Búsqueda Lineal** (`busqueda_lineal.py`)

  - Algoritmo de búsqueda secuencial
  - Validación de longitud exacta de claves
  - Prevención de duplicados
  - Visualización paso a paso

- **Búsqueda Binaria** (`busqueda_binaria.py`)

  - Algoritmo de búsqueda en arreglo ordenado
  - Validación de longitud exacta de claves
  - Prevención de duplicados
  - Visualización del rango de búsqueda

- **Función Hash** (`hash_view.py`)

  - Múltiples métodos de hash (módulo, centro del cuadrado)
  - Resolución de colisiones (lineal, cuadrática, doble hash)
  - Visualización de la tabla hash

- **Árbol Digital** (`trie_view.py`)

  - Estructura Trie para búsqueda de cadenas
  - Inserción, búsqueda y eliminación
  - Visualización del árbol

- **Árboles de Huffman** (`huffman_view.py`)

  - Compresión de datos
  - Construcción del árbol de Huffman
  - Codificación y decodificación

- **Árbol de Residuos** (`residuos_tree_view.py`)
  - Estructura de árbol para residuos
  - Operaciones de inserción y búsqueda

### 🌐 Búsquedas Externas (`externas.py`)

- **Búsqueda Lineal en Bloques** (`bloques_view.py`)

  - Búsqueda secuencial en archivos de bloques
  - Gestión de memoria secundaria

- **Búsqueda Binaria en Bloques** (`bloques_binaria_view.py`)

  - Búsqueda binaria en archivos de bloques
  - Optimización para acceso secuencial

- **Transformación de Claves** (`transformacion_view.py`)
  - Algoritmos de transformación de claves
  - Múltiples métodos de hash

### 📊 Grafos (`grafos.py`)

- Algoritmos de grafos
- Visualización de estructuras de grafos

### 🎨 Sistema de Temas (`theme/retro.py`)

- Paleta de colores estilo Windows 95/98
- Estilos personalizados para widgets
- Configuración de fuentes y colores

## 🔧 Características Técnicas

### Validación de Datos

- **Longitud exacta**: Las claves deben tener exactamente el número de dígitos especificado
- **Prevención de duplicados**: No se permiten claves repetidas
- **Validación numérica**: Solo se aceptan claves numéricas

### Persistencia

- **Guardado**: Exportación de estructuras de datos a archivos de texto
- **Carga**: Importación de datos desde archivos guardados
- **Formato**: Archivos de texto con metadatos y datos separados

### Visualización

- **Animaciones**: Visualización paso a paso de algoritmos
- **Colores**: Código de colores para diferentes estados
- **Interfaz**: Diseño retro con paneles y botones estilizados

## 📝 Uso de la Aplicación

1. **Ejecutar**: `python main.py`
2. **Navegar**: Usar los botones para moverse entre secciones
3. **Configurar**: Establecer parámetros (rango, dígitos, etc.)
4. **Generar**: Crear datos aleatorios o ingresar manualmente
5. **Operar**: Realizar búsquedas, inserciones, eliminaciones
6. **Guardar**: Exportar datos para uso posterior

## 🎯 Objetivos Educativos

Esta aplicación está diseñada para:

- **Aprender algoritmos** de búsqueda de manera visual
- **Entender estructuras** de datos complejas
- **Practicar implementaciones** de algoritmos clásicos
- **Visualizar el comportamiento** de diferentes métodos de búsqueda

## 🔄 Flujo de Navegación

```
Home → Búsquedas → Internas/Externas → Algoritmo Específico
  ↓
Grafos → Algoritmos de Grafos
```

## 📋 Archivos de Datos

La aplicación incluye archivos de ejemplo:

- `ARBOL.txt` - Datos de árbol
- `test_1.txt`, `test_3.txt`, `tet_3.txt` - Archivos de prueba

## 🛡️ Validaciones Implementadas

- **Longitud exacta de claves**: No se aceptan claves más cortas o largas
- **Prevención de duplicados**: Verificación antes de inserción
- **Validación numérica**: Solo dígitos permitidos
- **Límites de capacidad**: Control del tamaño máximo de estructuras

## 🎨 Personalización

El tema retro se puede modificar en `app/theme/retro.py`:

- Paleta de colores
- Fuentes
- Estilos de widgets
- Efectos visuales

---

**Desarrollado para Ciencias de la Computación II**  
_Aplicación educativa para el estudio de algoritmos de búsqueda y estructuras de datos_
