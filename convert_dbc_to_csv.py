#!/usr/bin/env python3
"""
Converte um ou mais arquivos .DBC do DATASUS (DBF comprimido com PKWARE blast) para CSV.

Requer:
    pip install climasus_readdbc_py

Uso (arquivo único):
    python convert_dbc_to_csv.py entrada.dbc saida.csv

Uso (vários arquivos, um CSV pra cada):
    python convert_dbc_to_csv.py arquivo1.dbc arquivo2.dbc arquivo3.dbc --outdir saidas

Uso (pasta inteira, um CSV pra cada .dbc encontrado):
    python convert_dbc_to_csv.py --dir dados_brutos --outdir saidas

Uso (vários arquivos, mesclados em um único CSV):
    python convert_dbc_to_csv.py arquivo1.dbc arquivo2.dbc --merge saida_unica.csv
    python convert_dbc_to_csv.py --dir dados_brutos --merge saida_unica.csv
"""

import argparse
import glob
import os
import sys


def load_readdbc():
    try:
        import climasus_readdbc as readdbc
    except ImportError:
        sys.exit(
            "Pacote 'climasus_readdbc_py' não encontrado.\n"
            "Instale com: pip install climasus_readdbc_py"
        )
    return readdbc


def resolve_inputs(inputs, directory):
    files = list(inputs)
    if directory:
        if not os.path.isdir(directory):
            sys.exit(f"Pasta não encontrada: {directory}")
        found = sorted(glob.glob(os.path.join(directory, "*.dbc")) +
                        glob.glob(os.path.join(directory, "*.DBC")))
        files.extend(found)

    seen = set()
    unique_files = []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)

    missing = [f for f in unique_files if not os.path.exists(f)]
    if missing:
        sys.exit(f"Arquivo(s) não encontrado(s): {', '.join(missing)}")

    if not unique_files:
        sys.exit("Nenhum arquivo .dbc informado ou encontrado.")

    return unique_files


def convert_one(readdbc, in_path, out_path, sep, encoding):
    print(f"Lendo {in_path} ...")
    df = readdbc.read_dbc(in_path)
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    df.to_csv(out_path, index=False, sep=sep, encoding=encoding)
    print(f"  -> OK: {len(df)} registros, {len(df.columns)} colunas -> {out_path}")
    return df


def main():
    ap = argparse.ArgumentParser(description="Converte um ou mais .DBC do DATASUS para CSV.")
    ap.add_argument("inputs", nargs="*", help="arquivo(s) .dbc de entrada")
    ap.add_argument("--dir", dest="directory", help="pasta com arquivos .dbc (todos serão processados)")
    ap.add_argument("--outdir", default=".", help="pasta de saída para CSVs individuais (padrão: pasta atual)")
    ap.add_argument("--merge", metavar="ARQUIVO.csv", help="mescla todos os arquivos em um único CSV")
    ap.add_argument("--sep", default=";", help="separador CSV (padrão: ;)")
    ap.add_argument("--encoding", default="utf-8-sig", help="encoding do CSV de saída (padrão: utf-8-sig)")
    args = ap.parse_args()

    if not args.inputs and not args.directory:
        ap.error("informe ao menos um arquivo .dbc ou use --dir")

    readdbc = load_readdbc()
    files = resolve_inputs(args.inputs, args.directory)

    if args.merge:
        import pandas as pd
        dfs = []
        for f in files:
            print(f"Lendo {f} ...")
            df = readdbc.read_dbc(f)
            df["_arquivo_origem"] = os.path.basename(f)
            dfs.append(df)
        merged = pd.concat(dfs, ignore_index=True)
        out_dir = os.path.dirname(args.merge)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        merged.to_csv(args.merge, index=False, sep=args.sep, encoding=args.encoding)
        print(f"OK: {len(merged)} registros totais de {len(files)} arquivo(s) -> {args.merge}")
    else:
        os.makedirs(args.outdir, exist_ok=True)
        for f in files:
            base = os.path.splitext(os.path.basename(f))[0]
            out_path = os.path.join(args.outdir, base + ".csv")
            convert_one(readdbc, f, out_path, args.sep, args.encoding)


if __name__ == "__main__":
    main()