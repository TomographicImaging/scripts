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
    # os.path.join(CIL_DEMOS_DIR, 'demos'),
    os.path.join(CIL_DEMOS_DIR, 'how-to')
]

def preprocess():
    for folder in folders:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith('.ipynb') and not file.endswith('_tmp.ipynb'):
                    original_path = os.path.join(root, file)
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
                                        log_file.write(f"Snippet load failed: {e}")
                            if '...' in cell.source:
                                cell.source = ""

                    with open(tmp_path, 'w') as f:
                        nbformat.write(notebook, f)

def cleanup_files():
    with open(LOG_NAME, "a") as log_file:
        for folder in folders:
            for root, dirs, files in os.walk(folder):
                
                for dir_name in dirs:
                    if dir_name.endswith('_files'):
                        dir_path = os.path.join(root, dir_name)
                        try:
                            shutil.rmtree(dir_path)
                            log_file.write(f"Deleted folder: {dir_path}")
                        except Exception as e:
                            log_file.write(f"Failed to delete folder {dir_path}: {e}")

                for file in files:
                    if file.endswith('_tmp.ipynb') or file.endswith('.tex'):
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            log_file.write(f"Deleted: {file_path}")
                        except Exception as e:
                            log_file.write(f"Failed to delete {file_path}: {e}")

def run_notebooks_tests():
    notebook_paths = []
    for folder in folders:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith('_tmp.ipynb'):
                    notebook_paths.append(os.path.join(root, file))
    # Run pytest on the collected notebooks
    if notebook_paths:
        with open(LOG_NAME, "a") as log_file:
            subprocess.run(
                [
                    'pytest',
                    '--nbmake',
                    '--nbmake-kernel=cil_test_demos',
                    '--nbmake-timeout=900',
                    '--overwrite',
                    '--capture=tee-sys',
                    '--log-file-level=INFO',
                    '-W', 'error',
                    '-W', 'ignore::ResourceWarning'
                ] + notebook_paths,
                cwd=CIL_DEMOS_DIR,
                stdout=log_file,
                stderr=subprocess.STDOUT
                )
            
        convert_notebooks_to_pdf(notebook_paths)

    else:
        with open(LOG_NAME, "a") as log_file:
            log_file.write("No '_tmp.ipynb' notebooks found.")

def convert_notebooks_to_pdf(notebook_paths):
    for notebook in notebook_paths:
        try:
            
            subprocess.run(
                ['jupyter', 'nbconvert', '--to', 'latex', notebook],
                cwd=CIL_DEMOS_DIR,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )

            tex_file = notebook.replace('.ipynb', '.tex')
            
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
                log_file.write(f"Saved PDF to: {pdf_output_path}")

        except subprocess.CalledProcessError as e:
            with open(LOG_NAME, "a") as log_file:
                log_file.write(f"Failed to convert {notebook} to PDF: {e}")

if __name__ == "__main__":
    preprocess()
    run_notebooks_tests()
    cleanup_files()
