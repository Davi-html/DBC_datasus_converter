#!/usr/bin/env python3
"""
Converte arquivos .DBC do DATASUS (DBF comprimido com PKWARE blast) para CSV.

Requer:
    pip install climasus_readdbc_py

Uso:
    python convert_dbc_to_csv.py entrada.DBC saida.csv
    python convert_dbc_to_csv.py entrada.DBC saida.csv --sep ";" --encoding utf-8-sig
"""

import argparse
import os
import sys

def convert(in_path: str, out_path: str, sep: str = ";", encoding: str = "utf-8-sig"):
    try:
        import climasus_readdbc as readdbc
    except ImportError:
        sys.exit(
            "Pacote 'climasus_readdbc_py' não encontrado.\n"
            "Instale com: pip install climasus_readdbc_py"
        )

    if not os.path.exists(in_path):
        sys.exit(f"Arquivo não encontrado: {in_path}")

    print(f"Lendo {in_path} ...")
    df = readdbc.read_dbc(in_path)

    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    df.to_csv(out_path, index=False, sep=sep, encoding=encoding)
    print(f"OK: {len(df)} registros e {len(df.columns)} colunas salvos em {out_path}")

def main():
    ap = argparse.ArgumentParser(description="Converte .DBC do DATASUS para CSV.")
    ap.add_argument("input", help="arquivo .DBC de entrada")
    ap.add_argument("output", nargs="?", help="arquivo CSV de saída (padrão: mesmo nome, extensão .csv)")
    ap.add_argument("--sep", default=";", help="separador CSV (padrão: ;)")
    ap.add_argument("--encoding", default="utf-8-sig", help="encoding do CSV de saída (padrão: utf-8-sig)")
    args = ap.parse_args()

    out_path = args.output or os.path.splitext(args.input)[0] + ".csv"
    convert(args.input, out_path, sep=args.sep, encoding=args.encoding)

if __name__ == "__main__":
    main()