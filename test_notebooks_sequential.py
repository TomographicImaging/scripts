import pytest
import nbformat
import os
import re
import shutil
import subprocess
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CIL_DEMOS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../CIL-Demos'))
PDF_OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'pdf_outputs')
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

LOG_NAME = "test_notebooks_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"

folders = [
    os.path.join(CIL_DEMOS_DIR, 'demos'),
    os.path.join(CIL_DEMOS_DIR, 'how-to')
]

def preprocess_notebook(original_path):
    """Copy a notebook to _tmp and apply preprocessing."""
    tmp_path = original_path.replace('.ipynb', '_tmp.ipynb')
    shutil.copy(original_path, tmp_path)

    with open(tmp_path, 'r') as f:
        notebook = nbformat.read(f, as_version=4)

    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.source = re.sub(r'/mnt/materials/', '/mnt/share/materials/', cell.source)
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

def run_notebook_test(tmp_path):
    """Run pytest for a single notebook and log output live."""
    with open(LOG_NAME, "a") as log_file:
        result = subprocess.run(
            [
                'pytest',
                '--nbmake',
                '--nbmake-kernel=cil_test_demos',
                '--nbmake-timeout=900',
                '--overwrite',
                '-W', 'error',
                '-W', 'ignore::ResourceWarning',
                tmp_path
            ],
            cwd=CIL_DEMOS_DIR,
            stdout=log_file,
            stderr=subprocess.STDOUT
        )
    return result.returncode == 0

def convert_notebook_to_pdf(tmp_path):
    """Convert a single notebook to PDF."""
    try:
        subprocess.run(
            ['jupyter', 'nbconvert', '--to', 'latex', tmp_path],
            cwd=CIL_DEMOS_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        tex_file = tmp_path.replace('.ipynb', '.tex')

        subprocess.run(
            ['tectonic', tex_file, '--print', '--outdir', PDF_OUTPUT_DIR],
            cwd=CIL_DEMOS_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        pdf_name = os.path.basename(tex_file).replace('.tex', '.pdf')
        pdf_output_path = os.path.join(PDF_OUTPUT_DIR, pdf_name)
        with open(LOG_NAME, "a") as log_file:
            log_file.write(f"Saved PDF to: {pdf_output_path}\n")

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
    for folder in folders:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith('.ipynb') and not file.endswith('_tmp.ipynb'):
                    original_path = os.path.join(root, file)
                    with open(LOG_NAME, "a") as log_file:
                        log_file.write(f"\n=== Processing notebook: {original_path} ===\n")
                    tmp_path = preprocess_notebook(original_path)
                    passed = run_notebook_test(tmp_path)
                    results[original_path] = 'passed' if passed else 'failed'
                    convert_notebook_to_pdf(tmp_path)
                    cleanup_notebook_files(tmp_path)

    with open(LOG_NAME, "a") as log_file:
        log_file.write("\n======== Notebook Test Summary =========\n")
        for nb, status in results.items():
            log_file.write(f"{nb}: {status}\n")

if __name__ == "__main__":
    main()
