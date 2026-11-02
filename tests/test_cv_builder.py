"""Automatische Tests fuer den cv-builder-Skill.

Schnell (ohne Browser): Gate, Job-Abgleich, Befuellen, Builder-Patches, Skill-Texte, Zip.
Langsam (Playwright + Chromium): alle 12 Vorlagen und alle 6 Stile als PDF mit ATS-Check.

Aufruf aus dem Projektordner:
    python3 -m pytest tests -q                # alles
    python3 -m pytest tests -q -m "not slow"  # nur die schnellen
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
# Arbeitsordner: skill/cv-builder, GitHub-Repo: cv-builder direkt an der Wurzel
SKILL = next(p for p in [ROOT / "skill" / "cv-builder", ROOT / "cv-builder"] if p.exists())
SCRIPTS = SKILL / "scripts"
EXAMPLE = SKILL / "examples" / "lena-berger.json"
ASSET = SKILL / "assets" / "builder.html"
ZIP = ROOT / "dist" / "cv-builder.zip"
STYLES = ["e3xler", "vent3x", "3xlabs", "forest", "atelier", "signal"]

sys.path.insert(0, str(SCRIPTS))
import check_cv  # noqa: E402
import fill_builder  # noqa: E402


def example() -> dict:
    """Frische Kopie der Musterkandidatin, damit kein Test den anderen beeinflusst."""
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def run(script: str, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], capture_output=True, text=True)


def write(tmp_path: Path, doc: dict, name: str = "cv.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return path


# --- Gate (check_cv.py) -------------------------------------------------------------------------

def test_example_passes_gate():
    errors, _ = check_cv.check(example(), None)
    assert errors == []


@pytest.mark.parametrize("marker", ["[ZAHL?]", "[DATUM?]", "[FIRMA?]"])
def test_placeholder_blocks_output(tmp_path, marker):
    doc = example()
    doc["cv"]["experience"][0]["bullets"][0] = f"Umsatz um {marker} gesteigert."
    result = run("check_cv.py", write(tmp_path, doc))
    assert result.returncode == 1
    assert marker in result.stdout


@pytest.mark.parametrize("field", ["name", "title", "location"])
def test_missing_required_field(field):
    doc = example()
    doc["cv"][field] = ""
    errors, _ = check_cv.check(doc, None)
    assert any(field in e for e in errors)


def test_missing_contact():
    doc = example()
    doc["cv"]["email"] = doc["cv"]["phone"] = ""
    errors, _ = check_cv.check(doc, None)
    assert any("Kontakt" in e for e in errors)


@pytest.mark.parametrize("value,ok", [("04/2022", True), ("2018", True), ("heute", True),
                                      ("April 2022", False), ("4/22", False)])
def test_date_format(value, ok):
    doc = example()
    doc["cv"]["experience"][0]["start"] = value
    errors, _ = check_cv.check(doc, None)
    assert (not any("Datum" in e for e in errors)) == ok


def test_length_warning_for_junior():
    doc = example()
    doc["level"] = "junior"
    doc["cv"]["summary"] = "Wort " * 500
    _, notes = check_cv.check(doc, None)
    assert any("Wörter" in n for n in notes)


def test_job_matching_ignores_punctuation_and_verbs():
    job = ("Du verantwortest die Roadmap im E-Commerce. Du arbeitest mit Jira und Confluence, "
           "kennst Google Analytics und SAFe.")
    _, notes = check_cv.check(example(), job)
    line = next(n for n in notes if n.startswith("Begriffe"))
    missing = line.split(": ", 1)[1].split(", ")
    assert "Confluence" in missing and "SAFe" in missing
    assert "E-Commerce" not in missing and "E-Commerce." not in missing   # steht im CV
    assert not {"verantwortest", "arbeitest", "kennst"} & set(missing)    # Verben zaehlen nicht


# --- Befuellen (fill_builder.py) ----------------------------------------------------------------

def seed_of(html_path: Path) -> dict:
    m = re.search(r'<script id="cvb-seed" type="application/json">(.*?)</script>', html_path.read_text(encoding="utf-8"), re.S)
    return json.loads(m.group(1).replace("<\\/", "</"))


def test_fill_writes_seed(tmp_path):
    out = tmp_path / "out.html"
    assert run("fill_builder.py", EXAMPLE, out).returncode == 0
    seed = seed_of(out)
    assert seed["state"]["cv"]["name"] == "Lena Berger"
    assert seed["state"]["tpl"] == 5 and seed["state"]["sty"] == "e3xler"


def test_fill_hides_empty_sections():
    state = fill_builder.build_state(example())
    assert {"projects", "interests", "skillsRated"} <= set(state["hidden"])
    assert "experience" not in state["hidden"]


def test_fill_does_not_mutate_input():
    doc = example()
    before = copy.deepcopy(doc)
    fill_builder.build_state(doc)
    assert doc == before


def test_seed_id_stable_and_content_based(tmp_path):
    a, b = tmp_path / "a.html", tmp_path / "b.html"
    run("fill_builder.py", EXAMPLE, a)
    run("fill_builder.py", EXAMPLE, b)
    assert seed_of(a)["id"] == seed_of(b)["id"]
    doc = example()
    doc["cv"]["title"] = "Senior Product Managerin"
    c = tmp_path / "c.html"
    run("fill_builder.py", write(tmp_path, doc), c)
    assert seed_of(c)["id"] != seed_of(a)["id"]


def test_script_tag_in_data_cannot_break_out(tmp_path):
    doc = example()
    doc["cv"]["summary"] = "</script><script>alert(1)</script>"
    out = tmp_path / "x.html"
    run("fill_builder.py", write(tmp_path, doc), out)
    assert "</script><script>alert(1)" not in out.read_text(encoding="utf-8")
    assert seed_of(out)["state"]["cv"]["summary"] == doc["cv"]["summary"]


def test_asset_stays_unseeded(tmp_path):
    run("fill_builder.py", EXAMPLE, tmp_path / "out.html")
    assert fill_builder.SEED_EMPTY in ASSET.read_text(encoding="utf-8")


# --- Builder-Patches (assets/builder.html) ------------------------------------------------------

@pytest.fixture(scope="module")
def bundle() -> tuple[dict, str]:
    html = ASSET.read_text(encoding="utf-8")
    manifest = json.loads(re.search(r'<script type="__bundler/manifest">(.*?)</script>', html, re.S).group(1))
    template = json.loads(re.search(r'<script type="__bundler/template">(.*?)</script>', html, re.S).group(1))
    return manifest, template


@pytest.mark.parametrize("name", ["JobSprout", "JobTactics", "YourUnique", "src:'LLD'", "name:'VENT3X'", "name:'3xLABS'"])
def test_no_vendor_or_company_names(bundle, name):
    assert name not in bundle[1]


def test_ats_patches_present(bundle):
    template = bundle[1]
    assert "'calt' 0" in template                     # Bindestrich zwischen Versalien bleibt ein Bindestrich
    assert "hyphens:'auto'" not in template           # keine automatische Silbentrennung
    assert "sty: 'e3xler'" in template                # Default-Stil


def test_no_legacy_fonts_and_size(bundle):
    mimes = {e["mime"] for e in bundle[0].values()}
    assert "font/woff" not in mimes and "application/vnd.ms-fontobject" not in mimes
    assert ASSET.stat().st_size < 8e6


# --- Skill-Texte --------------------------------------------------------------------------------

def skill_texts():
    return [p for p in SKILL.rglob("*") if p.suffix in {".md", ".json"}]


@pytest.mark.parametrize("path", skill_texts(), ids=lambda p: p.name)
def test_no_em_dash(path):
    assert "—" not in path.read_text(encoding="utf-8")


def test_skill_frontmatter():
    head = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
    assert re.search(r"^name: cv-builder$", head, re.M)
    assert re.search(r"^description: .{100,}", head, re.M)


def test_referenced_files_exist():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for ref in set(re.findall(r"`((?:reference|scripts|assets|examples)/[\w./-]+)`", text)):
        assert (SKILL / ref).exists(), ref


# --- Zip ----------------------------------------------------------------------------------------

needs_zip = pytest.mark.skipif(not ZIP.exists(), reason="kein dist/cv-builder.zip (im Repo liegt es als Release)")


@needs_zip
def test_zip_layout():
    names = zipfile.ZipFile(ZIP).namelist()
    assert "cv-builder/SKILL.md" in names
    assert all(n.startswith("cv-builder/") for n in names)
    assert not any("__pycache__" in n or ".DS_Store" in n for n in names)
    assert ZIP.stat().st_size < 10e6


@needs_zip
def test_zip_matches_skill_folder():
    with zipfile.ZipFile(ZIP) as z:
        for path in SKILL.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.name != ".DS_Store":
                rel = "cv-builder/" + path.relative_to(SKILL).as_posix()
                assert z.read(rel) == path.read_bytes(), f"veraltet im Zip: {rel}"


# --- PDF und ATS (langsam) ----------------------------------------------------------------------

def render(tmp_path: Path, template: int, style: str) -> tuple[subprocess.CompletedProcess, str]:
    pytest.importorskip("playwright")
    from pypdf import PdfReader
    doc = example()
    doc["template"], doc["style"] = template, style
    # Vorlagen mit bewerteten Kenntnissen zeigen sonst keine Kompetenzen
    doc["cv"]["rated"] = [{"name": "A/B-Tests", "level": 4}, {"name": "SQL", "level": 3}]
    html, pdf = tmp_path / f"t{template}-{style}.html", tmp_path / f"t{template}-{style}.pdf"
    run("fill_builder.py", write(tmp_path, doc, f"t{template}-{style}.json"), html)
    result = run("render_pdf.py", html, pdf)
    text = "".join(p.extract_text() or "" for p in PdfReader(str(pdf)).pages)
    return result, re.sub(r"-\s+", "-", re.sub(r"\s+", " ", text))


@pytest.mark.slow
@pytest.mark.parametrize("template", range(1, 13))
def test_every_template_renders_ats_clean(tmp_path, template):
    result, text = render(tmp_path, template, "e3xler")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PROBLEM" not in result.stdout, result.stdout
    assert "Seiten: 1" in result.stdout
    assert "lena berger" in text.lower()
    assert "a/b-tests" in text.lower()


@pytest.mark.slow
@pytest.mark.parametrize("style", STYLES)
def test_every_style_keeps_hyphens(tmp_path, style):
    result, text = render(tmp_path, 5, style)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PROBLEM" not in result.stdout, result.stdout
    for word in ["A/B-Tests", "E-Commerce", "B2B-SaaS", "Wirtschaftsinformatik"]:
        assert word in text, f"{word} fehlt im PDF-Text ({style})"
