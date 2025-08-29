import pytest
import nbformat
import os
import re
import shutil
import subprocess
from datetime import datetime

DATA_PATH = '/mnt/share/materials/SIRF/Fully3D/CIL/'
DATA_PATH_ALT = '/mnt/share/materials/CIL/'

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CIL_DEMOS_DIR = os.path.expanduser(os.path.join('~', 'CIL-Demos'))

PDF_OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'html_outputs')
TMP_OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'tmp_notebooks')

os.makedirs(TMP_OUTPUT_DIR, exist_ok=True)
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

folders = [
    os.path.join(CIL_DEMOS_DIR, 'demos'),
    os.path.join(CIL_DEMOS_DIR, 'how-to')
]

LOG_NAME = "test_notebooks_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"

def preprocess_notebook(original_path):
    rel_path = os.path.relpath(original_path, CIL_DEMOS_DIR)
    rel_path = rel_path.replace("..", "_")
    tmp_path = os.path.join(TMP_OUTPUT_DIR, rel_path)
    tmp_dir = os.path.dirname(tmp_path)
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = tmp_path.replace('.ipynb', '_tmp.ipynb')

    shutil.copy(original_path, tmp_path)

    with open(tmp_path, 'r') as f:
        notebook = nbformat.read(f, as_version=4)

    warning_cell = nbformat.v4.new_code_cell(
    source="""import warnings
notebook_warnings = []
def warning_collector(message, category, filename, lineno, file=None, line=None):
    notebook_warnings.append(f"{category.__name__}: {message} (File {filename}, line {lineno})")
warnings.showwarning = warning_collector
"""
    )

    notebook.cells.insert(0, warning_cell)

    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.source = re.sub(r'/mnt/materials/SIRF/Fully3D/CIL/', DATA_PATH, cell.source)
            cell.source = re.sub(r'/mnt/materials/CIL/', DATA_PATH_ALT, cell.source)
            if '# %load' in cell.source:
                try:
                    snippet_file = cell.source.split('snippets/')[1].split('\'')[0]
                    snippet_path = os.path.join(os.path.dirname(original_path), 'snippets', snippet_file)
                    with open(snippet_path, 'r') as sf:
                        cell.source = sf.read()
                except Exception as e:
                    with open(LOG_NAME, "a") as log_file:
                        log_file.write(f"Snippet load failed for {original_path}: {e}\n")
            if '...' in cell.source:
                cell.source = ""

    with open(tmp_path, 'w') as f:
        nbformat.write(notebook, f)

    return tmp_path

def run_notebook_test(tmp_path, original_path, all_warnings):
    original_folder = os.path.dirname(os.path.abspath(original_path))
    tmp_abs_path = os.path.abspath(tmp_path)
    with open(LOG_NAME, "a") as log_file:
        result = subprocess.run(
            [
                'pytest',
                '--nbmake',
                '--nbmake-kernel=cil_test_demos',
                '--nbmake-timeout=900',
                '--overwrite',
                tmp_abs_path
            ],
            cwd=original_folder,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            env={**os.environ, 'PYTHONPATH': original_folder}
        )

    try:
        with open(tmp_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)

        for cell in nb.cells:
            if cell.cell_type == 'code' and 'notebook_warnings' not in cell.source:
                for out in cell.get('outputs', []):
                    if out.output_type == 'stream':
                        text = out.get('text', '')
                        for line in text.splitlines():
                            if 'Warning' in line or 'Error' in line:
                                all_warnings.setdefault(tmp_path, []).append(line)

        if tmp_path in all_warnings:
            with open(LOG_NAME, "a") as log_file:
                log_file.write(f"\n=== Warnings in {tmp_path} ===\n")
                for w in all_warnings[tmp_path]:
                    log_file.write(w + "\n")

    except Exception:
        pass

    return result.returncode == 0

def convert_notebook_to_html(tmp_path):
    parent_dir_name = os.path.basename(os.path.dirname(tmp_path))
    subfolder_path = os.path.join(PDF_OUTPUT_DIR, parent_dir_name)
    os.makedirs(subfolder_path, exist_ok=True)
    html_output_path = os.path.join(subfolder_path, os.path.basename(tmp_path).replace('.ipynb', '.html'))
    subprocess.run(
        [
            'jupyter', 'nbconvert',
            '--to', 'html',
            '--template', 'lab',
            '--HTMLExporter.embed_mathjax=True',
            '--HTMLExporter.mathjax_url=nbextensions/mathjax/MathJax.js?config=TeX-AMS_HTML',
            '--output', os.path.basename(html_output_path),
            '--output-dir', subfolder_path,
            tmp_path
        ],
        cwd=os.path.dirname(tmp_path),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    with open(LOG_NAME, "a") as log_file:
        log_file.write(f"Saved HTML to: {html_output_path}\n")

def convert_notebook_to_pdf(tmp_path):
    subprocess.run(
        ['jupyter', 'nbconvert', '--to', 'latex', tmp_path],
        cwd=os.path.dirname(tmp_path),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    tex_file = tmp_path.replace('.ipynb', '.tex')
    parent_dir_name = os.path.basename(os.path.dirname(tmp_path))
    subfolder_path = os.path.join(PDF_OUTPUT_DIR, parent_dir_name)
    os.makedirs(subfolder_path, exist_ok=True)
    subprocess.run(
        ['tectonic', tex_file, '--print', '--outdir', subfolder_path],
        cwd=os.path.dirname(tmp_path),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    pdf_name = os.path.basename(tex_file).replace('.tex', '.pdf')
    subfolder_pdf_path = os.path.join(subfolder_path, pdf_name)
    with open(LOG_NAME, "a") as log_file:
        log_file.write(f"Saved PDF to: {subfolder_pdf_path}\n")

def cleanup_notebook_files(tmp_path):
    try:
        os.remove(tmp_path)
    except Exception:
        pass
    tex_file = tmp_path.replace('.ipynb', '.tex')
    if os.path.exists(tex_file):
        try:
            os.remove(tex_file)
        except Exception:
            pass
    files_dir = tmp_path.replace('.ipynb', '_files')
    if os.path.exists(files_dir):
        try:
            shutil.rmtree(files_dir)
        except Exception:
            pass

def main():
    results = {}
    all_warnings = {}
    for folder in folders:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith('.ipynb') and not file.endswith('_tmp.ipynb'):
                    original_path = os.path.join(root, file)
                    rel_path = os.path.relpath(original_path, CIL_DEMOS_DIR)
                    rel_path = rel_path.replace("..", "_")
                    tmp_path = os.path.join(TMP_OUTPUT_DIR, rel_path).replace('.ipynb', '_tmp.ipynb')

                    if os.path.exists(tmp_path):
                        with open(LOG_NAME, "a") as log_file:
                            log_file.write(f"Skipping (tmp exists): {original_path}\n")
                        continue

                    with open(LOG_NAME, "a") as log_file:
                        log_file.write(f"\n=== Processing notebook: {original_path} ===\n")
                    tmp_path = preprocess_notebook(original_path)
                    passed = run_notebook_test(tmp_path, original_path, all_warnings)
                    results[original_path] = 'passed' if passed else 'failed'

    with open(LOG_NAME, "a") as log_file:
        log_file.write("\n======== Notebook Test Summary =========\n")
        for nb, status in results.items():
            log_file.write(f"{nb}: {status}\n")

        log_file.write("\n======== All Warnings Summary =========\n")
        for nb, warns in all_warnings.items():
            log_file.write(f"\n{nb}:\n")
            for w in warns:
                log_file.write(f"  {w}\n")

if __name__ == "__main__":
    main()
