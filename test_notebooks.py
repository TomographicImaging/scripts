import pytest
import nbformat
import os
import re
import shutil
import subprocess

folders = ['../CIL-Demos/demos', '../CIL-Demos/how-to']
skip_notebooks = ['../CIL-Demos/demos/2_Iterative/04_SPDHG.ipynb'
]

def run_tmp_notebook(notebook_path):  

    tmp_notebook_path = notebook_path.replace('.ipynb', '_tmp.ipynb')
    shutil.copy(notebook_path, tmp_notebook_path)

    with open(tmp_notebook_path, 'r') as f:
        notebook = nbformat.read(f, as_version=4)
    
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            # Update filepath
            if '/mnt/materials/' in cell.source:
                cell.source = re.sub(r'/mnt/materials/', '/mnt/share/materials/', cell.source)

            # Replace commented %load lines with the correct snippet
            if '# %load' in cell.source:
                snippet_file = cell.source.split('snippets/')[1].split('\'')[0]
                snippet_path = os.path.join(os.path.dirname(notebook_path), 'snippets', snippet_file)
                if os.path.exists(snippet_path):
                    with open(snippet_path, 'r') as snippet_file:
                        snippet_code = snippet_file.read()
                    cell.source = cell.source.replace('# %load', '') 
                    cell.source = snippet_code  
                else:
                    print(f"Warning: Snippet path {snippet_path} does not exist.")

            # Clear cells containing ellipses
            if '...' in cell.source:
                cell.source = ""  

    with open(tmp_notebook_path, 'w') as f:
        nbformat.write(notebook, f)

    print(f"\t\t Testing notebook: {tmp_notebook_path}")
    log_file_path = os.path.abspath("notebook_test_output.log")
    pytest.main([
        "--nbmake",
        "--nbmake-kernel=cil",
        "--nbmake-timeout=900",
        "--overwrite",  
        "--rootdir", os.path.abspath(os.path.dirname(tmp_notebook_path)),
        os.path.abspath(tmp_notebook_path),
        "--capture=tee-sys",  
        f"--log-file={log_file_path}",
        "--log-file-level=INFO",
        "-W", "error"  # Treat warnings as errors

    ])

    
    try:
        subprocess.run([
            "jupyter", "nbconvert",
            "--to", "html",
            "--output-dir", os.path.dirname(notebook_path),
            "--output", os.path.basename(notebook_path).replace('.ipynb', '.html'),
            tmp_notebook_path
        ], check=True)

        print(f"Successfully converted to HTML: {notebook_path.replace('.ipynb', '.html')}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert {tmp_notebook_path} to HTML. Error: {e}")

    os.remove(tmp_notebook_path)

def test_notebook_runs():
    for folder in folders: 
        print(f"Searching in folder: {folder}")
        for root, dirs, files in os.walk(folder):
            print(f"\tIn directory: {root}")
            for file in files:
                if not file.endswith('.ipynb'):
                    continue
                if file.endswith('_tmp.ipynb'):
                    continue

                notebook_path = os.path.join(root, file)             
                if notebook_path in skip_notebooks:
                    print(f"\t\t Skipping notebook: {notebook_path}")
                else:
                    run_tmp_notebook(notebook_path)
