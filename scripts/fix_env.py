#!/usr/bin/env python3
"""Sanitiza el archivo .env arreglando errores comunes que rompen `source .env`:
- Espacios alrededor del =
- Comillas envolventes innecesarias
- Espacios al final de la línea
- Saltos de línea CRLF (Windows)

Uso: python3 scripts/fix_env.py [archivo]  (default: .env)
"""
import sys, re
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else ".env")
if not path.exists():
    print(f"ℹ️  {path} no existe — nada que arreglar.")
    sys.exit(0)

raw = path.read_text(encoding="utf-8", errors="ignore")
original = raw

# Normalizar finales de línea
raw = raw.replace("\r\n", "\n").replace("\r", "\n")

lines = []
changes = []
for i, line in enumerate(raw.splitlines(), 1):
    stripped = line.rstrip()
    # Pasar comentarios y vacías sin tocar
    if not stripped or stripped.lstrip().startswith("#"):
        lines.append(stripped)
        continue
    m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$", line)
    if not m:
        lines.append(stripped)
        continue
    key, value = m.group(1), m.group(2)
    # Quitar comillas envolventes
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    new = f"{key}={value}"
    if new != line:
        changes.append(f"  L{i}: '{line}' → '{new}'")
    lines.append(new)

fixed = "\n".join(lines) + "\n"

if fixed == original:
    print(f"✅ {path} ya está bien formateado.")
else:
    path.write_text(fixed, encoding="utf-8")
    print(f"✅ Arreglado {path}:")
    for c in changes:
        print(c)
