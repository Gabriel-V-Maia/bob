#!/usr/bin/env python3
import sys, subprocess, ast, pathlib, argparse

VENV = pathlib.Path(".bob-venv")

def collect_deps():
    imports = set()
    for file in pathlib.Path(".").glob("*.py"):
        if file.name == "bob.py":
            continue
        try:
            tree = ast.parse(file.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
    return imports

def log(msg):
    with open("bob_log.txt", "a") as f:
        f.write(msg + "\n")
    print(msg)

def pip_install(packages):
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", *packages],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        log(result.stdout)
        return

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--break-system-packages", *packages],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        log(result.stdout)
        return

    log("[bob] criando venv...")
    subprocess.check_call([sys.executable, "-m", "venv", str(VENV)])
    venv_python = VENV / "bin" / "python"
    subprocess.check_call([str(venv_python), "-m", "pip", "install", *packages])
    subprocess.check_call([str(venv_python), *sys.argv])
    sys.exit()

def bootstrap():
    deps = [d for d in collect_deps() if d not in sys.stdlib_module_names]
    missing = []
    for dep in deps:
        try: __import__(dep)
        except ImportError: missing.append(dep)

    if missing:
        log(f"[bob] instalando: {missing}")
        pip_install(missing)
        subprocess.check_call([sys.executable, *sys.argv])
        sys.exit()

def build_executable():
    log("[bob] buildando executável com pyinstaller...")
    try: __import__("PyInstaller")
    except ImportError:
        log("[bob] instalando pyinstaller...")
        pip_install(["pyinstaller"])

    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--onefile", "main.py"],
        capture_output=True, text=True
    )
    log(result.stdout)
    if result.returncode != 0:
        log("[bob] erro:\n" + result.stderr)
    else:
        log("[bob] executável gerado em dist/main")

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--clear", action="store_true", help="limpa a tela após instalar")
parser.add_argument("-e", "--executable", action="store_true", help="gera executável com pyinstaller")
args = parser.parse_args()

bootstrap()

if args.clear:
    subprocess.call("clear")

if args.executable:
    build_executable()
else:
    subprocess.check_call([sys.executable, "main.py"])
