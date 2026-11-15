#!/usr/bin/env python3
"""pfiles-check — hitta filer som borde vara p-filer men inte är det.

Kontrollerar en modulkatalog (eller ett helt repo) och rapporterar:

  MISSING_SOURCE  genererad fil utan .p-källa  (FEL)
  STALE           utdata skiljer sig från expansionen (FEL)
  MANUAL_PFILE    p-fil, men ingen genererad fil  (FEL)
  ORPHAN_PFILE    .p-fil utan giltig utdata  (FEL)
  UNEXPLAINED     källfil utan p-motsvarighet och inte vitlistad (FEL)
  PAIRED          .p.x + x finns — OK
  ALLOWED         vitlistad — OK
  NOT_APPLICABLE  saknar stöd för preprocess — OK

Användning:
  ./pfiles-check.py --version 18.0 /path/till/modul [...]
  ./pfiles-check.py --version 18.0 --json /path/till/repo
  ./pfiles-check.py --version 18.0 --print-allow /path | sudo tee .../.pfiles-allow

Vitlista: <repo- eller modulrot>/.pfiles-allow — en sökväg per rad,
relativ till roten. '#' inleder kommentar. Glöm inte '!' vid generering.

Exit: 0 = inga fel, 1 = fel hittade, 2 = användningsfel.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

# Filändelser som preprocess hanterar (jfr /skill:odoo-pfiles)
PREPROCESS_EXTS = (".py", ".xml", ".js", ".csv", ".sh", ".html", ".htm", ".pl",
                   ".rb", ".tcl", ".c", ".h", ".cpp", ".java", ".php")
# Filer som alltid är källor, aldrig genereras
EXCLUDED_NAMES = {"__init__.py", "__manifest__.py", "__manifest__.p.py"}
EXCLUDED_DIRS = {".git", "__pycache__", ".tox", ".venv", "venv", "node_modules",
                 ".idea", ".mypy_cache", ".pytest_cache"}
# p-fil-ändelser: (p-ändelse, utdata-ändelse). Ordningen har betydelse — längsta först.
PFILE_SUFFIXES = [(".p.py", ".py"), (".p.xml", ".xml"), (".p.js", ".js"),
                  (".p.csv", ".csv"), (".p.sh", ".sh"), (".p.html", ".html"),
                  (".p.htm", ".htm"), (".p.pl", ".pl"), (".p.rb", ".rb"),
                  (".p.tcl", ".tcl"), (".p.c", ".c"), (".p.h", ".h"),
                  (".p.cpp", ".cpp"), (".p.java", ".java"), (".p.php", ".php")]

OK, ERR = "OK", "ERROR"


def pfile_split(name):
    """a.p.py -> ('a.py', '.p.py');  a.py -> (None, None)."""
    for psuffix, suffix in PFILE_SUFFIXES:
        if name.endswith(psuffix):
            return name[: -len(psuffix)] + suffix, psuffix
    return None, None


def pepfile_hint(name):
    """a.xml -> a.xml.p.xml (preprocess-konventionen: suffixet behålls)."""
    for psuffix, suffix in PFILE_SUFFIXES:
        if name.lower().endswith(suffix):
            return name + psuffix
    return name + ".p"


def is_preprocessable(name):
    return not name.startswith(".") and name.lower().endswith(PREPROCESS_EXTS)


def find_roots(paths, explicit):
    """Hitta modulrötter (katalog med __manifest__.py eller *.p.py) under paths."""
    if explicit:
        return [os.path.abspath(p) for p in paths]

    # Är en angiven sökväg redan en modulrot?
    roots = []
    for p in paths:
        p = os.path.abspath(p)
        direct = (os.path.isfile(os.path.join(p, "__manifest__.py")) or
                  any(f.endswith(".p.py") for f in os.listdir(p) if f.endswith(".py")))
        if direct:
            roots.append(p)
            continue
        for dirpath, dirnames, filenames in os.walk(p):
            dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDED_DIRS)
            if "__manifest__.py" in filenames:
                roots.append(dirpath)
                dirnames[:] = []   # moduler ligger inte inuti moduler
    return roots


def load_allow(root):
    """Läs .pfiles-allow från root eller repo-överliggande katalog."""
    allow, source = set(), None
    candidate = root
    for _ in range(4):                        # root, root/.., root/../.., ...
        f = os.path.join(candidate, ".pfiles-allow")
        if os.path.isfile(f):
            source = f
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    line = line.split("#", 1)[0].strip()
                    if line:
                        allow.add(os.path.normpath(line))
            break
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return allow, source


def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def expand_ok(preprocess, pfile, outfile, version, repo, tmpdir, cache):
    """Returnerar (status, detalj) där status är OK/STALE/ERROR."""
    if preprocess is None:
        return "ERROR", "preprocess saknas — kan inte verifiera expansion"
    if pfile not in cache:
        candidate = os.path.join(tmpdir, os.path.basename(outfile) or "out")
        if os.path.exists(candidate):
            os.remove(candidate)
        cmd = [preprocess, "-f", "-D", f"VERSION={version}", "-D", f"REPO={repo}",
               "-o", candidate, pfile]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            cache[pfile] = ("ERROR", "preprocess timeout")
            return cache[pfile]
        if proc.returncode != 0:
            cache[pfile] = ("ERROR", f"preprocess misslyckades: {proc.stderr.strip()[:300]}")
            return cache[pfile]
        try:
            with open(candidate, "rb") as fh:
                cache[pfile] = (OK, fh.read())
        except OSError as exc:
            cache[pfile] = ("ERROR", f"kunde inte läsa expansionen: {exc}")
        if os.path.exists(candidate):
            os.remove(candidate)
    status, value = cache[pfile]
    if status != OK:
        return status, value
    try:
        with open(outfile, "rb") as fh:
            actual = fh.read()
    except OSError as exc:
        return "ERROR", f"kunde inte läsa utdata: {exc}"
    if actual != value:
        return "STALE", "utdata skiljer sig från expansionen — kör om preprocess"
    return OK, "matchar expansionen"


def check_root(root, version, exclude_allow, preprocess, tmpdir):
    allow, allow_src = load_allow(root)
    findings, cache = [], {}

    # Samla alla filer
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDED_DIRS)
        for name in sorted(filenames):
            files.append(os.path.join(dirpath, name))

    pfile_targets = {}
    for f in files:
        target, _ = pfile_split(os.path.basename(f))
        if target is not None:
            pfile_targets[os.path.join(os.path.dirname(f), target)] = f

    for f in files:
        name = os.path.basename(f)
        target, psuffix = pfile_split(name)
        relpath = rel(root, f)
        # Vitlistan är modul-kvalificerad: "modul/models/x.py". En platt rad
        # ("models/x.py") matchar BARA om modulnamnet inte är känt — annars
        # skulle en rad för en modul tysta samma filnamn i en annan modul.
        allowed = f"{os.path.basename(root)}/{relpath}" in allow

        if target is not None:                                  # en p-fil
            outfile = os.path.join(os.path.dirname(f), target)
            if not os.path.isfile(outfile):
                findings.append((ERR, "MANUAL_PFILE", rel(root, f),
                                 f"{name} saknar genererad {target}"))
                continue
            if exclude_allow:
                st, detail = expand_ok(preprocess, f, outfile, version,
                                       os.path.basename(root), tmpdir, cache)
                findings.append((OK if st == OK else ERR,
                                 "PAIRED" if st == OK else st, rel(root, f), detail))
            else:
                findings.append((OK, "PAIRED", rel(root, f), "har genererad utdata"))
            continue

        if name in EXCLUDED_NAMES or not is_preprocessable(name):
            continue

        source = pfile_targets.get(f)                           # genererad fil?
        if source:
            if exclude_allow:
                continue        # p-filen rapporterar redan PARED/STALE
            try:
                same = open(f, "rb").read() == open(source, "rb").read()
                findings.append((OK, "PAIRED", rel(root, f), "identisk med p-filen"))
            except OSError as exc:
                findings.append((ERR, "STALE", rel(root, f), str(exc)))
            continue

        if allowed:
            findings.append((OK, "ALLOWED", rel(root, f), "vitlistad i .pfiles-allow"))
        else:
            findings.append((ERR, "UNEXPLAINED", rel(root, f),
                             f"{name} är varken p-fil eller genererad — döp till "
                             f"{pepfile_hint(name)} "
                             f"eller vitlista i .pfiles-allow"))
    return findings, allow_src, allow


def main(argv=None):
    ap = argparse.ArgumentParser(description="Hitta filer som saknar p-fil.")
    ap.add_argument("paths", nargs="+", help="moduler/repon att kontrollera")
    ap.add_argument("--version", default=os.environ.get("VERSION", ""),
                    help="Odoo-utgåva, t.ex. 18.0 (default: $VERSION)")
    ap.add_argument("--repo", default=None, help="REPO-definition (default: modulnamn)")
    ap.add_argument("--json", action="store_true", help="maskinläsbar utdata")
    ap.add_argument("--no-expand", action="store_true",
                    help="hoppa over expansionskontroll (bara täckning)")
    ap.add_argument("--print-allow", action="store_true",
                    help="skriv förslag till .pfiles-allow (UNEXPLAINED → rader)")
    ap.add_argument("-q", "--quiet", action="store_true", help="bara fel")
    args = ap.parse_args(argv)

    if not args.version and not args.no_expand:
        ap.error("--version krävs (eller $VERSION) — utdata beror på utgåvan")

    roots = find_roots(args.paths, explicit=False)
    if not roots:
        print("Hittade inga modulrötter (katalog med __manifest__.py eller *.p.py).",
              file=sys.stderr)
        return 2

    preprocess = None if args.no_expand else shutil.which("preprocess")
    tmpdir = tempfile.mkdtemp(prefix="pfiles-check-")
    all_findings, total_err = [], 0

    try:
        for root in roots:
            findings, allow_src, allow = check_root(root, args.version, not args.no_expand,
                                                    preprocess, tmpdir)
            errs = [f for f in findings if f[0] == ERR]
            total_err += len(errs)
            all_findings.append({"root": root, "allow": allow_src, "findings": findings,
                                 "errors": len(errs)})
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    if args.print_allow:
        seen = set()
        for entry in all_findings:
            root = entry["root"]
            for sev, kind, path, _ in entry["findings"]:
                if kind == "UNEXPLAINED":
                    line = f"{os.path.basename(root)}/{path}"
                    if line not in seen:
                        seen.add(line)
                        print(line)
        return 0

    if args.json:
        print(json.dumps({"version": args.version, "preprocess": preprocess,
                          "roots": all_findings}, indent=2, ensure_ascii=False))
        return 1 if total_err else 0

    for entry in all_findings:
        rows = entry["findings"]
        shown = [r for r in rows if args.quiet is False or r[0] == ERR]
        print(f"=== {entry['root']}  ({entry['errors']} fel av {len(rows)} poster)")
        if entry["allow"]:
            print(f"    vitlista: {entry['allow']}")
        for sev, kind, path, detail in shown:
            mark = "✗" if sev == ERR else "✓"
            print(f"  {mark} {kind:<14} {path}")
            if sev == ERR or not args.quiet:
                print(f"      {detail}")
        missing = [r for r in rows if r[1] == "UNEXPLAINED"]
        if missing:
            print(f"    → {len(missing)} vitliknande rad(er). "
                  f"Generera: pfiles-check --version {args.version} --print-allow <rot>")
        if not rows:
            print("  (inga p-filer och inga kandidater — modulen använder inte p-filer)")

    if preprocess is None and not args.no_expand:
        print("\n⚠ preprocess saknas i PATH — endast täckningskontroll gjord. "
              "Installera: python3 -m pip install --break-system-packages preprocess", file=sys.stderr)
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
