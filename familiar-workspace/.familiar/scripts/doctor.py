"""familiar doctor - cross-platform preflight check for the local toolchain.

WHO RUNS THIS: a user setting familiar up on a new machine (Windows, macOS or Linux), and anyone
debugging a document or deck build that failed for an environment reason. It checks what familiar's
document and deck paths assume and prints what is missing plus what breaks without it. One script for
every OS: the PowerShell doctor.ps1 that once sat beside it was retired at 1.0.0.

HOW TO RUN (from anywhere):
    python3 <path-to-this-file>       (or python, or py -3 on Windows: whichever exists)

Every FAIL line ends with a command that fixes it on this machine, so the assistant can offer to run
it. It deliberately runs on old Pythons (no 3.10 syntax): diagnosing one is its job.

EXIT CODE: 0 if every REQUIRED check passed, 1 otherwise. Optional checks never fail the run.
Standard library only. ASCII output.
"""
import importlib.util
import glob
import os
import platform
import shutil
import sys
import sysconfig

IS_WIN = os.name == "nt"
IS_MAC = sys.platform == "darwin"
fails = 0
warns = 0
missing_dists = []
VENV = os.path.join(os.path.expanduser("~"), ".familiar", "venv")
VENV_PY = os.path.join(VENV, "Scripts", "python.exe") if IS_WIN else os.path.join(VENV, "bin", "python")


def ok(name, detail):
    print("  [ OK ]   %-22s %s" % (name, detail))


def fail(name, detail, fix):
    global fails
    print("  [FAIL]   %-22s %s" % (name, detail))
    print("           -> %s" % fix)
    fails += 1


def warn(name, detail, fix):
    global warns
    print("  [WARN]   %-22s %s" % (name, detail))
    print("           -> %s" % fix)
    warns += 1


def module_version(import_name, dist_name):
    try:
        from importlib import metadata
        return metadata.version(dist_name)
    except Exception:
        return None


def find_soffice():
    """Same lookup order as the draft-document build scripts: PATH, then default install folders."""
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
    candidates = ["/Applications/LibreOffice.app/Contents/MacOS/soffice",
                  "/usr/lib/libreoffice/program/soffice"]
    candidates += sorted(glob.glob("/opt/libreoffice*/program/soffice"))
    for var in ("ProgramFiles", "ProgramFiles(x86)"):
        base = os.environ.get(var)
        if base:
            candidates += [os.path.join(base, "LibreOffice", "program", "soffice.com"),
                           os.path.join(base, "LibreOffice", "program", "soffice.exe")]
    return next((c for c in candidates if os.path.isfile(c)), None)


def version_tuple(v):
    parts = []
    for piece in v.split(".")[:3]:
        digits = "".join(ch for ch in piece if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def shell_path(path):
    return '"%s"' % path if " " in path else path


def linux_installer():
    """The system package manager's install command prefix, or None. Non-interactive: the assistant
    cannot answer a confirmation prompt."""
    for tool, cmd in (("apt-get", "sudo apt-get install -y"), ("dnf", "sudo dnf install -y"),
                      ("pacman", "sudo pacman -S --noconfirm"), ("zypper", "sudo zypper -n install")):
        if shutil.which(tool):
            return cmd
    return None


def install_python_fix():
    """How to get Python 3.10+ on this OS, per the python.org 'Using Python' pages."""
    if IS_WIN:
        return ("Install the Python install manager: winget install 9NQ7512CXL7T -e --accept-package-agreements "
                "--disable-interactivity  (or from python.org/downloads). Then open a new terminal; it provides "
                "python, py and python3.")
    if IS_MAC:
        fix = ("Install current Python with the macOS installer from python.org/downloads, then double-click "
               "'Install Certificates.command' in its Applications folder. Leave /usr/bin/python3 alone: it is "
               "Apple's own, older copy.")
        if shutil.which("brew"):
            fix += " Homebrew also works: brew install python"
        return fix
    pm = linux_installer()
    if pm:
        return ("Install a newer Python with the system package manager, e.g. %s python3.12 (the exact package "
                "name varies by distribution), then run it as python3.12." % pm)
    return "Install Python 3.10 or newer with your distribution's package manager."


def externally_managed():
    """PEP 668: the system Python refuses pip installs outside a virtual environment."""
    if sys.prefix != sys.base_prefix:
        return False
    try:
        stdlib = sysconfig.get_path("stdlib", sysconfig.get_default_scheme())
    except AttributeError:  # get_default_scheme is 3.10+; older Pythons fail the version check anyway
        stdlib = sysconfig.get_path("stdlib")
    return os.path.isfile(os.path.join(stdlib, "EXTERNALLY-MANAGED"))


print("")
print("===== familiar doctor =====")
print("")

print("Host")
ok("OS", "%s %s" % (platform.system(), platform.release()))
ok("Python", "%s  (%s)" % (platform.python_version(), sys.executable))
old_python = sys.version_info < (3, 10)
if old_python:
    fail("Python version", platform.python_version(),
         "familiar needs Python 3.10 or newer; its scripts stop on this one. " + install_python_fix())
others = [c for c in ("python3", "python", "py") if shutil.which(c)]
ok("Commands on PATH", ", ".join(others) if others else "none of python3, python, py")
if IS_WIN and "windowsapps" in sys.executable.lower():
    warn("Store alias path", sys.executable,
         "Running from WindowsApps. A Python Install Manager alias is real Python; a Store stub is not. "
         "This process runs, so it is the former - informational only.")
if "libreoffice" in sys.executable.lower():
    warn("Python", "this is LibreOffice's bundled interpreter",
         "Not a supported familiar runtime: no python-docx/python-pptx. Install standalone Python and put it first on PATH.")
print("")

print("Python packages")
# Install with this exact interpreter (python -m pip), never a bare `pip` that may belong to another one.
# Where the system Python refuses pip (PEP 668: Debian/Ubuntu, Homebrew), the packages go into one
# per-user virtual environment at ~/.familiar/venv instead, and its Python runs familiar's scripts.
managed = externally_managed()
if managed:
    pip = shell_path(VENV_PY) + " -m pip install --upgrade"
else:
    pip = shell_path(sys.executable) + " -m pip install --upgrade"
# (import name, distribution name, what breaks without it, minimum version or None)
for imp, dist, breaks, minimum in (
        ("docx", "python-docx", "document build (/draft-document) cannot run", "1.2.0"),
        ("pptx", "python-pptx", "deck build (/draft-document) cannot run", None),
        ("pymupdf", "PyMuPDF", "PDF ingest and deck render-QA cannot run", None),
        ("pymupdf4llm", "pymupdf4llm", "PDF ingest (extract_pdf.py) cannot run", None)):
    if old_python:
        print("  skipped: packages belong to the new Python; run this check again with it.")
        break
    if importlib.util.find_spec(imp) is None:
        fail(dist, "not importable", "%s %s   - without it, %s." % (pip, dist, breaks))
        missing_dists.append(dist)
        continue
    ver = module_version(imp, dist)
    if minimum and ver and version_tuple(ver) < version_tuple(minimum):
        fail(dist, "%s installed, need >= %s" % (ver, minimum),
             "%s %s   - without it, %s." % (pip, dist, breaks))
        missing_dists.append(dist)
    else:
        ok(dist, ver or "importable")
if missing_dists and not old_python:
    steps = []
    pm = None if (IS_WIN or IS_MAC) else linux_installer()
    if managed:
        if pm and "apt-get" in pm:  # Debian and Ubuntu ship venv support separately
            steps.append("%s python3-venv" % pm)
        steps.append("%s -m venv %s" % (shell_path(sys.executable), VENV))
        print("  note:    this Python is managed by the system and refuses pip installs (PEP 668), so the")
        print("           packages go into a familiar-only environment at %s." % VENV)
        print("           Afterwards, run familiar's scripts with %s." % VENV_PY)
    elif importlib.util.find_spec("pip") is None:
        steps.append("%s python3-pip" % pm if pm else "%s -m ensurepip --upgrade" % shell_path(sys.executable))
    steps.append("%s %s" % (pip, " ".join(missing_dists)))
    print("  fix all: " + "\n           ".join(steps))
print("")

if IS_WIN:
    print("Encoding (Windows)")
    # Windows locale is cp1252. Without PYTHONUTF8=1 the docx validator can report a PASSING document
    # as corrupt: "'charmap' codec can't decode byte 0x9d".
    if os.environ.get("PYTHONUTF8") == "1":
        ok("PYTHONUTF8", "1")
    else:
        warn("PYTHONUTF8", "'%s'" % os.environ.get("PYTHONUTF8", ""),
             "Set PYTHONUTF8=1. Without it the docx validator can report a valid document as corrupt (charmap codec error).")
    print("           note: `python -I` ignores PYTHONUTF8; scripts run with -I need `-X utf8` (file-handling.md).")
    print("")

print("Office toolchain")


def office_apps():
    """Microsoft Office applications registered for automation (Windows only)."""
    if not IS_WIN:
        return []
    try:
        import winreg
    except ImportError:
        return []
    found = []
    for prog, label in (("PowerPoint.Application", "PowerPoint"), ("Word.Application", "Word"),
                        ("Excel.Application", "Excel")):
        try:
            winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, prog))
            found.append(label)
        except OSError:
            pass
    return found


office = office_apps()
if office:
    ok("Microsoft Office", ", ".join(office) + " (Office-native final check: office_render.ps1)")
soffice = find_soffice()
if soffice:
    base = os.path.basename(soffice).lower()
    if IS_WIN and base == "soffice.exe":
        warn("LibreOffice", soffice + " (soffice.exe only)",
             "Never invoke soffice.exe headless - it can hang the build. Put the LibreOffice program folder on PATH so soffice.com is found.")
    else:
        ok("LibreOffice", soffice)
elif "PowerPoint" in office:
    warn("LibreOffice", "not found",
         "Optional here: PowerPoint renders decks for the visual check. Install LibreOffice for a build-time render too.")
else:
    fail("LibreOffice", "not found",
         "Install LibreOffice. Without a renderer, decks get only structural checks "
         "(deck-rules.md -> Validation and delivery).")
pandoc = shutil.which("pandoc")
if pandoc:
    ok("pandoc", pandoc)
else:
    warn("pandoc", "not found in this process",
         "Optional. Check a fresh terminal before concluding it is missing; docx work has a Python fallback either way.")
print("")

print("OCR chain (optional - scanned PDFs only)")
for tool, alts, purpose in (
        ("tesseract", ("tesseract",), "OCR of scanned PDFs"),
        ("ghostscript", ("gs", "gswin64c") if IS_WIN else ("gs",), "PDF pre-processing"),
        ("qpdf", ("qpdf",), "PDF repair and linearisation")):
    hit = next((p for p in (shutil.which(a) for a in alts) if p), None)
    if hit:
        ok(tool, hit)
    else:
        warn(tool, "not found", "Optional. Without it: %s is unavailable." % purpose)
print("")

print("=======================")
if fails == 0:
    print("READY. %d warning(s)." % warns)
    print("")
    sys.exit(0)
print("NOT READY. %d required check(s) failed, %d warning(s)." % (fails, warns))
if old_python:
    print("Fix the FAIL lines above. Until Python is fixed, familiar's helper scripts do not run and the")
    print("assistant does their checks by hand, more slowly and less reliably.")
else:
    print("Fix the FAIL lines above. familiar still runs - only the document and deck build paths are affected.")
print("")
sys.exit(1)
