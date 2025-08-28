# conda install pytest tectonic nbformat nbmake nbconvert

import pytest
import nbformat
import os
import re
import shutil
import subprocess
from datetime import datetime

DATA_PATH = '/mnt/share/materials/SIRF/Fully3D/CIL/'                        # specify where the notebook data is
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))                     # specify where this script is
CIL_DEMOS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../CIL-Demos'))   # specify where the CIL-Demos are in relation to this script
PDF_OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'html_outputs')                    # specify where you want the pdf outputs to go
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

folders = [                                                                 # specify which folders you want to test
    os.path.join(CIL_DEMOS_DIR, 'demos'),
    os.path.join(CIL_DEMOS_DIR, 'how-to') ]

LOG_NAME = "test_notebooks_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"


def preprocess_notebook(original_path):
    """Copy a notebook to _tmp and apply preprocessing."""
    tmp_path = original_path.replace('.ipynb', '_tmp.ipynb')
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

def run_notebook_test(tmp_path, all_warnings):
    """Run pytest for a single notebook and log output live."""
    with open(LOG_NAME, "a") as log_file:
        result = subprocess.run(
            [
                'pytest',
                '--nbmake',
                '--nbmake-kernel=cil_test_demos',
                '--nbmake-timeout=900',
                '--overwrite',
                tmp_path
            ],
            cwd=CIL_DEMOS_DIR,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True
        )

    try:
        with open(tmp_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)

        for cell in nb.cells:
            if cell.cell_type == 'code' and 'notebook_warnings' not in cell.source:
                for out in cell.get('outputs', []):
                    if out.output_type == 'stream':
                        text = out.get('text', '')
                        # Capture warnings emitted into notebook_warnings
                        for line in text.splitlines():
                            if 'Warning' in line or 'Error' in line:  # basic filter
                                all_warnings.setdefault(tmp_path, []).append(line)

        # Log immediately after running this notebook
        if tmp_path in all_warnings:
            with open(LOG_NAME, "a") as log_file:
                log_file.write(f"\n=== Warnings in {tmp_path} ===\n")
                for w in all_warnings[tmp_path]:
                    log_file.write(w + "\n")

    except Exception:
        pass  
    
    return result.returncode == 0

def convert_notebook_to_html(tmp_path):
    """Convert a notebook to HTML and save in the same folder structure as PDF outputs."""
    try:
        parent_dir_name = os.path.basename(os.path.dirname(tmp_path))
        subfolder_path = os.path.join(PDF_OUTPUT_DIR, parent_dir_name)
        os.makedirs(subfolder_path, exist_ok=True)

        html_output_path = os.path.join(
            subfolder_path,
            os.path.basename(tmp_path).replace('.ipynb', '.html')
        )

        subprocess.run(
            [
                'python', '-m', 'nbconvert',
                '--to', 'html',
                '--output', os.path.basename(html_output_path),
                '--output-dir', subfolder_path,
                tmp_path
            ],
            cwd=CIL_DEMOS_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        with open(LOG_NAME, "a") as log_file:
            log_file.write(f"Saved HTML to: {html_output_path}\n")

    except subprocess.CalledProcessError as e:
        with open(LOG_NAME, "a") as log_file:
            log_file.write(f"Failed to convert {tmp_path} to HTML: {e}\n")

def convert_notebook_to_pdf(tmp_path):
    """
    Convert a notebook to PDF and save
    Note: this fails for a lot of our rendered markdown maths, save html instead
    """
    try:
        subprocess.run(
            ['jupyter', 'nbconvert', '--to', 'latex', tmp_path],
            cwd=CIL_DEMOS_DIR,
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
            cwd=CIL_DEMOS_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        pdf_name = os.path.basename(tex_file).replace('.tex', '.pdf')
        subfolder_pdf_path = os.path.join(subfolder_path, pdf_name)

        with open(LOG_NAME, "a") as log_file:
            log_file.write(f"Saved PDF to: {subfolder_pdf_path}\n")

    except subprocess.CalledProcessError as e:
        with open(LOG_NAME, "a") as log_file:
            log_file.write(f"Failed to convert {tmp_path} to PDF: {e}\n")


def cleanup_notebook_files(tmp_path):
    """Delete tmp notebook, tex files, and any _files directories."""
    with open(LOG_NAME, "a") as log_file:
        # Remove _tmp.ipynb
        try:
            os.remove(tmp_path)
            log_file.write(f"Deleted: {tmp_path}\n")
        except Exception as e:
            log_file.write(f"Failed to delete {tmp_path}: {e}\n")

        # Remove tex file
        tex_file = tmp_path.replace('.ipynb', '.tex')
        if os.path.exists(tex_file):
            try:
                os.remove(tex_file)
                log_file.write(f"Deleted: {tex_file}\n")
            except Exception as e:
                log_file.write(f"Failed to delete {tex_file}: {e}\n")

        # Remove _files directory
        files_dir = tmp_path.replace('.ipynb', '_files')
        if os.path.exists(files_dir):
            try:
                shutil.rmtree(files_dir)
                log_file.write(f"Deleted folder: {files_dir}\n")
            except Exception as e:
                log_file.write(f"Failed to delete folder {files_dir}: {e}\n")

def main():
    results = {}
    all_warnings = {}
    for folder in folders:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith('.ipynb') and not file.endswith('_tmp.ipynb'):
                    original_path = os.path.join(root, file)
                    with open(LOG_NAME, "a") as log_file:
                        log_file.write(f"\n=== Processing notebook: {original_path} ===\n")
                    tmp_path = preprocess_notebook(original_path)
                    passed = run_notebook_test(tmp_path, all_warnings)
                    results[original_path] = 'passed' if passed else 'failed'
                    convert_notebook_to_html(tmp_path)
                    cleanup_notebook_files(tmp_path)

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
