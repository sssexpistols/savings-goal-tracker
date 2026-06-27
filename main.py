"""
Savings Goal Tracker CLI
=========================
Gestor de metas de ahorro por terminal con persistencia en SQLite.
Registra metas, abonos y consulta el progreso en tiempo real.

Autor: Gabriel Valderrama
GitHub: github.com/sssexpistols

Uso:
    python main.py meta add "Laptop gaming" 15000
    python main.py meta list
    python main.py abono add 1 500
    python main.py progreso 1
    python main.py resumen
"""

import argparse
import sys
from db import init_db
from models import MetaModel, AbonoModel


# ── Parser ────────────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ahorro",
        description="Savings Goal Tracker — Gabriel Valderrama",
    )
    sub = parser.add_subparsers(dest="grupo", metavar="GRUPO")

    # --- METAS ---
    meta_p = sub.add_parser("meta", help="Gestionar metas de ahorro")
    meta_sub = meta_p.add_subparsers(dest="accion", metavar="ACCION")

    # meta add
    m_add = meta_sub.add_parser("add", help="Crear meta de ahorro")
    m_add.add_argument("nombre", help="Nombre de la meta")
    m_add.add_argument("objetivo", type=float, help="Monto objetivo (MXN)")
    m_add.add_argument("--prioridad", choices=["alta", "media", "baja"],
                       default="media")
    m_add.add_argument("--fecha-limite", default=None,
                       help="Fecha límite YYYY-MM-DD (opcional)")

    # meta list
    meta_sub.add_parser("list", help="Listar todas las metas")

    # meta done
    m_done = meta_sub.add_parser("done", help="Marcar meta como completada")
    m_done.add_argument("id", type=int)

    # meta delete
    m_del = meta_sub.add_parser("delete", help="Eliminar meta")
    m_del.add_argument("id", type=int)

    # --- ABONOS ---
    abono_p = sub.add_parser("abono", help="Registrar abonos a una meta")
    abono_sub = abono_p.add_subparsers(dest="accion", metavar="ACCION")

    # abono add
    a_add = abono_sub.add_parser("add", help="Registrar abono")
    a_add.add_argument("meta_id", type=int, help="ID de la meta")
    a_add.add_argument("monto", type=float, help="Monto del abono (MXN)")
    a_add.add_argument("--nota", default="", help="Nota opcional")

    # abono list
    a_list = abono_sub.add_parser("list", help="Ver abonos de una meta")
    a_list.add_argument("meta_id", type=int)

    # --- PROGRESO y RESUMEN ---
    prog_p = sub.add_parser("progreso", help="Ver progreso de una meta")
    prog_p.add_argument("id", type=int)

    sub.add_parser("resumen", help="Resumen general de todas las metas")

    return parser


# ── Comandos ──────────────────────────────────────────────────────────────────
def barra(porcentaje: float, ancho: int = 25) -> str:
    lleno = int(ancho * porcentaje / 100)
    return "[" + "#" * lleno + "-" * (ancho - lleno) + f"] {porcentaje:.1f}%"


def cmd_meta_add(meta_m, args):
    m = meta_m.create(args.nombre, args.objetivo, args.prioridad, args.fecha_limite)
    print(f"\n[+] Meta #{m['id']} creada: '{m['nombre']}'")
    print(f"    Objetivo : ${m['objetivo']:,.2f} MXN")
    print(f"    Prioridad: {m['prioridad']}")
    if m["fecha_limite"]:
        print(f"    Límite   : {m['fecha_limite']}\n")


def cmd_meta_list(meta_m, abono_m):
    metas = meta_m.list_all()
    if not metas:
        print("No hay metas registradas. Crea una con: python main.py meta add")
        return
    print(f"\n{'ID':<4} {'NOMBRE':<22} {'OBJETIVO':>10} {'AHORRADO':>10} PROGRESO")
    print("-" * 72)
    for m in metas:
        ahorrado = abono_m.total_ahorrado(m["id"])
        pct = min((ahorrado / m["objetivo"]) * 100, 100) if m["objetivo"] else 0
        estado = " [COMPLETADA]" if m["completada"] else ""
        print(f"{m['id']:<4} {m['nombre'][:21]:<22} "
              f"${m['objetivo']:>9,.0f} ${ahorrado:>9,.0f} "
              f"{barra(pct, 18)}{estado}")
    print()


def cmd_abono_add(meta_m, abono_m, args):
    meta = meta_m.get_by_id(args.meta_id)
    if not meta:
        print(f"[!] Meta #{args.meta_id} no encontrada.")
        return
    a = abono_m.create(args.meta_id, args.monto, args.nota)
    total = abono_m.total_ahorrado(args.meta_id)
    pct = min((total / meta["objetivo"]) * 100, 100)
    print(f"\n[+] Abono registrado: ${args.monto:,.2f} MXN")
    print(f"    Meta    : {meta['nombre']}")
    print(f"    Ahorrado: ${total:,.2f} / ${meta['objetivo']:,.2f}")
    print(f"    {barra(pct)}\n")
    if pct >= 100:
        print("    *** META ALCANZADA! Usa: python main.py meta done {args.meta_id} ***\n")


def cmd_abono_list(abono_m, args):
    abonos = abono_m.list_by_meta(args.meta_id)
    if not abonos:
        print(f"No hay abonos para la meta #{args.meta_id}.")
        return
    print(f"\n{'ID':<5} {'FECHA':<12} {'MONTO':>10}  NOTA")
    print("-" * 45)
    for a in abonos:
        print(f"{a['id']:<5} {a['fecha']:<12} ${a['monto']:>9,.2f}  {a['nota']}")
    print(f"\nTotal: ${abono_m.total_ahorrado(args.meta_id):,.2f} MXN\n")


def cmd_progreso(meta_m, abono_m, args):
    meta = meta_m.get_by_id(args.id)
    if not meta:
        print(f"[!] Meta #{args.id} no encontrada.")
        return
    total = abono_m.total_ahorrado(args.id)
    pct = min((total / meta["objetivo"]) * 100, 100) if meta["objetivo"] else 0
    faltante = max(meta["objetivo"] - total, 0)
    print(f"\n--- Progreso: {meta['nombre']} ---")
    print(f"  Objetivo  : ${meta['objetivo']:>10,.2f}")
    print(f"  Ahorrado  : ${total:>10,.2f}")
    print(f"  Faltante  : ${faltante:>10,.2f}")
    print(f"  {barra(pct)}")
    if meta["fecha_limite"]:
        print(f"  Limite    : {meta['fecha_limite']}")
    print()


def cmd_resumen(meta_m, abono_m):
    metas = meta_m.list_all()
    total_obj = sum(m["objetivo"] for m in metas)
    total_aho = sum(abono_m.total_ahorrado(m["id"]) for m in metas)
    activas = sum(1 for m in metas if not m["completada"])
    completadas = len(metas) - activas
    print(f"\n=== Resumen de Ahorros ===")
    print(f"  Metas activas    : {activas}")
    print(f"  Metas completadas: {completadas}")
    print(f"  Total objetivos  : ${total_obj:>10,.2f}")
    print(f"  Total ahorrado   : ${total_aho:>10,.2f}")
    if total_obj:
        print(f"  Progreso global  : {barra((total_aho/total_obj)*100)}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    conn = init_db()
    meta_m = MetaModel(conn)
    abono_m = AbonoModel(conn)
    parser = build_parser()
    args = parser.parse_args()

    if args.grupo is None:
        parser.print_help()
        sys.exit(0)

    if args.grupo == "meta":
        if not args.accion:
            parser.parse_args(["meta", "--help"])
        elif args.accion == "add":
            cmd_meta_add(meta_m, args)
        elif args.accion == "list":
            cmd_meta_list(meta_m, abono_m)
        elif args.accion == "done":
            meta_m.complete(args.id)
            print(f"[OK] Meta #{args.id} marcada como completada.")
        elif args.accion == "delete":
            meta_m.delete(args.id)
            print(f"[OK] Meta #{args.id} eliminada.")

    elif args.grupo == "abono":
        if not args.accion:
            parser.parse_args(["abono", "--help"])
        elif args.accion == "add":
            cmd_abono_add(meta_m, abono_m, args)
        elif args.accion == "list":
            cmd_abono_list(abono_m, args)

    elif args.grupo == "progreso":
        cmd_progreso(meta_m, abono_m, args)

    elif args.grupo == "resumen":
        cmd_resumen(meta_m, abono_m)

    conn.close()


if __name__ == "__main__":
    main()
