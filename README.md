# Savings Goal Tracker CLI

> **Herramienta de línea de comandos para gestionar metas de ahorro personal con seguimiento de abonos y progreso en tiempo real.**

Parte del ecosistema de finanzas personales:
[Savings Goal Tracker CLI](.) · [Expense Analyzer](../proyecto2_automatizacion) · [Expense Tracker API](../proyecto3_flask_api)

---

## Características

- Crear y gestionar múltiples metas de ahorro con prioridad y fecha límite
- Registrar abonos individuales con notas personalizadas
- Visualizar progreso en tiempo real con barra gráfica en terminal
- Resumen general con avance global entre todas las metas
- Persistencia automática en SQLite — sin configuración adicional
- 100% stdlib de Python — sin dependencias externas

---

## Stack Técnico

| Tecnología | Uso |
|------------|-----|
| Python 3.10+ | Lenguaje principal |
| SQLite | Persistencia de datos (stdlib) |
| argparse | Interfaz de línea de comandos (stdlib) |

---

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/sssexpistols/savings-goal-tracker
cd savings-goal-tracker

# No requiere instalación de dependencias
python main.py --help
```

---

## Uso

### Metas de ahorro

```bash
# Crear una meta
python main.py meta add "Laptop para desarrollo" 15000 --prioridad alta --fecha-limite 2025-12-01

# Crear meta sin fecha límite
python main.py meta add "Fondo de emergencia" 10000 --prioridad alta

# Ver todas las metas con progreso
python main.py meta list

# Marcar meta como completada
python main.py meta done 1

# Eliminar meta
python main.py meta delete 2
```

### Abonos

```bash
# Registrar un abono a la meta #1
python main.py abono add 1 500 --nota "Ahorro quincena enero"

# Ver historial de abonos de una meta
python main.py abono list 1
```

### Progreso y resumen

```bash
# Ver progreso detallado de una meta
python main.py progreso 1

# Resumen general de todas las metas
python main.py resumen
```

### Salida de ejemplo

```
ID   NOMBRE                  OBJETIVO   AHORRADO PROGRESO
------------------------------------------------------------------------
1    Laptop para desarrollo   $15,000    $2,350  [####------------------]  15.7%
2    Fondo de emergencia      $10,000    $1,800  [####------------------]  18.0%
3    Curso de inglés B2        $3,500      $500  [###-------------------]  14.3%

=== Resumen de Ahorros ===
  Metas activas    : 3
  Metas completadas: 0
  Total objetivos  : $    28,500.00
  Total ahorrado   : $     4,650.00
  Progreso global  : [####--------------------]  16.3%
```

---

## Estructura del Proyecto

```
savings-goal-tracker/
├── main.py      # Punto de entrada: comandos CLI y presentación en terminal
├── db.py        # Esquema SQLite: tablas metas y abonos con integridad referencial
├── models.py    # MetaModel y AbonoModel: operaciones CRUD desacopladas de la UI
├── ahorro.db    # Base de datos generada automáticamente en primer uso
└── README.md
```

### Decisiones de diseño

- **Separación de capas**: `main.py` (presentación) → `models.py` (lógica) → `db.py` (persistencia). Cada archivo tiene una responsabilidad única.
- **Sin dependencias externas**: el proyecto es completamente portable — solo requiere Python estándar.
- **Integridad referencial**: los abonos usan `ON DELETE CASCADE` para mantener consistencia al eliminar metas.

---

[![LinkedIn](https://img.shields.io/badge/LinkedIn-angel--gabriel--valderrama-blue?logo=linkedin)](https://linkedin.com/in/angel-gabriel-valderrama)
