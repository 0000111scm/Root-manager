#!/usr/bin/env python3
import os
import subprocess
from dataclasses import dataclass, field
from typing import List, Tuple

# ───────────────── CONFIGURAÇÃO ─────────────────

JUNK_PATHS = [
    "/cache",
    "/data/cache",
    "/data/dalvik-cache",
    "/data/system/dropbox",
    "/data/log",
    "/sdcard/Android/data",
    "/sdcard/Android/obb",
    "/sdcard/Download",
]

TEMP_EXTENSIONS = [".tmp", ".log", ".bak", ".old"]


@dataclass
class CleanReport:
    removed_paths: List[str] = field(default_factory=list)
    removed_files: List[str] = field(default_factory=list)
    total_bytes_freed: int = 0

    def add_file(self, path: str, size: int):
        self.removed_files.append(path)
        self.total_bytes_freed += size

    def add_path(self, path: str):
        self.removed_paths.append(path)


def run_root(cmd: str) -> Tuple[str, str, int]:
    proc = subprocess.Popen(
        ["su", "-c", cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = proc.communicate()
    return out.strip(), err.strip(), proc.returncode


def has_root() -> bool:
    out, err, code = run_root("id")
    return code == 0 and "uid=0" in out


def human_size(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.2f} PB"


def estimate_dir_size(path: str) -> int:
    total = 0
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            fpath = os.path.join(root, name)
            try:
                total += os.path.getsize(fpath)
            except OSError:
                continue
    return total


def clean_dir_root(path: str, report: CleanReport, delete_self: bool = False):
    size = estimate_dir_size(path)
    if size > 0:
        report.add_file(path + "/**", size)

    target = path if delete_self else os.path.join(path, "*")
    _, err, code = run_root(f"rm -rf '{target}'")
    if code == 0:
        report.add_path(path)
    else:
        print(f"[ERRO] Falha ao limpar {path}: {err}")


def clean_temp_extensions(root_path: str, report: CleanReport):
    for r, dirs, files in os.walk(root_path, topdown=True):
        for name in files:
            if any(name.lower().endswith(ext) for ext in TEMP_EXTENSIONS):
                full = os.path.join(r, name)
                try:
                    size = os.path.getsize(full)
                except OSError:
                    size = 0
                _, err, code = run_root(f"rm -f '{full}'")
                if code == 0:
                    report.add_file(full, size)
                else:
                    print(f"[ERRO] Não foi possível remover {full}: {err}")


def clean_app_caches(report: CleanReport):
    out, err, code = run_root("cmd package list packages | cut -d':' -f2")
    if code != 0:
        print(f"[ERRO] Não foi possível listar pacotes: {err}")
        return

    packages = [p.strip() for p in out.splitlines() if p.strip()]
    for pkg in packages:
        cmd = f"pm clear --cache-only {pkg}"
        _, err, code = run_root(cmd)
        if code != 0:
            cache_path = f"/data/data/{pkg}/cache"
            size = estimate_dir_size(cache_path)
            if size > 0:
                _, err2, code2 = run_root(f"rm -rf '{cache_path}'/*")
                if code2 == 0:
                    report.add_file(cache_path + "/**", size)


def fast_clean() -> CleanReport:
    report = CleanReport()
    if not has_root():
        print("[ERRO] Sem acesso root (su).")
        return report

    print("[+] Limpando cache dos apps...")
    clean_app_caches(report)

    basic_paths = ["/cache", "/data/cache", "/sdcard/Android/data"]
    for p in basic_paths:
        if os.path.exists(p):
            print(f"[+] Limpando {p}/...")
            clean_dir_root(p, report, delete_self=False)

    return report


def aggressive_clean() -> CleanReport:
    report = fast_clean()

    extra_paths = ["/data/dalvik-cache", "/data/system/dropbox", "/data/log"]
    for p in extra_paths:
        if os.path.exists(p):
            print(f"[+] Limpando {p}/...")
            clean_dir_root(p, report, delete_self=False)

    print("[+] Limpando arquivos temporários em /sdcard...")
    clean_temp_extensions("/sdcard", report)

    return report


def analyze_only() -> CleanReport:
    report = CleanReport()
    total = 0
    for p in JUNK_PATHS:
        if os.path.exists(p):
            s = estimate_dir_size(p)
            total += s
            print(f"{p}: {human_size(s)}")
    print(f"\nTotal potencial a limpar: {human_size(total)}")
    report.total_bytes_freed = total
    return report


def main():
    print("=== RootCleaner (core) ===")
    if not has_root():
        print("[ERRO] Sem acesso root (su). Conceda root ao app / processo.")
        return

    print("Opções:")
    print(" 1) Limpeza rápida")
    print(" 2) Limpeza agressiva")
    print(" 3) Apenas análise")
    choice = input("Escolha [1/2/3]: ").strip() or "1"

    if choice == "1":
        report = fast_clean()
    elif choice == "2":
        report = aggressive_clean()
    else:
        report = analyze_only()

    print("\n=== Relatório ===")
    print(f"Total estimado liberado: {human_size(report.total_bytes_freed)}")


if __name__ == "__main__":
    main()
