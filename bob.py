#!/usr/bin/env python3
import sys, subprocess, ast, pathlib, argparse, urllib.request, json

VENV = pathlib.Path(".bob-venv")

ALIASES = {
    "PIL":   "Pillow",
    "docx":  "python-docx",
    "cv2":   "opencv-python",
    "sklearn": "scikit-learn",
    "yaml":  "pyyaml",
    "bs4":   "beautifulsoup4",
    "wx":    "wxPython",
}

def is_local(name):
    for f in pathlib.Path(".").rglob(f"{name}.py"):
        if ".bob-venv" not in f.parts:
            return True
    for d in pathlib.Path(".").rglob(name):
        if d.is_dir() and (d / "__init__.py").exists() and ".bob-venv" not in d.parts:
            return True
    return False

def collect_deps(recursive=False):
    imports = set()
    pattern = "**/*.py" if recursive else "*.py"
    for file in pathlib.Path(".").glob(pattern):
        if file.name == "bob.py":
            continue
        if ".bob-venv" in file.parts:
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

def resolve_package_name(module):
    if module in ALIASES:
        return ALIASES[module]
    try:
        url = f"https://pypi.org/pypi/{module}/json"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
            return data["info"]["name"]
    except:
        pass
    return module

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

def bootstrap(recursive=False):
    deps = [
        d for d in collect_deps(recursive)
        if d not in sys.stdlib_module_names and not is_local(d)
    ]
    missing = []
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            log(f"[bob] resolvendo: {dep}...")
            missing.append(resolve_package_name(dep))

    if missing:
        log(f"[bob] instalando: {missing}")
        pip_install(missing)
        subprocess.check_call([sys.executable, *sys.argv])
        sys.exit()

def build_executable(entry):
    log("[bob] buildando executável com pyinstaller...")
    try: __import__("PyInstaller")
    except ImportError:
        log("[bob] instalando pyinstaller...")
        pip_install(["pyinstaller"])

    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--onefile", entry],
        capture_output=True, text=True
    )
    log(result.stdout)
    if result.returncode != 0:
        log("[bob] erro:\n" + result.stderr)
    else:
        log(f"[bob] executável gerado em dist/{pathlib.Path(entry).stem}")

parser = argparse.ArgumentParser()
parser.add_argument("entry", nargs="?", default="main.py", help="arquivo entry point (default: main.py)")
parser.add_argument("-c", "--clear", action="store_true", help="limpa a tela após instalar")
parser.add_argument("-e", "--executable", action="store_true", help="gera executável com pyinstaller")
parser.add_argument("-r", "--recursive", action="store_true", help="varre subpastas em busca de imports")
args = parser.parse_args()

bootstrap(args.recursive)

if args.clear:
    subprocess.call("clear", shell=True)

if args.executable:
    build_executable(args.entry)
else:
    subprocess.check_call([sys.executable, args.entry])
