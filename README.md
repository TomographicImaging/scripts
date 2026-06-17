# scripts

Static hosting:

- Source: https://github.com/TomographicImaging/scripts
- Rendered: https://tomographicimaging.github.io/scripts

## Environment files for installing software

### CIL-Demos
`cil_demos.yml` - for installing the latest release of CIL-Demos on a system with a GPU.

`cil_demos_cpu.yml` - for installing the latest release of CIL-Demos on a system without a GPU.


### CILViewer
`cilviewer_ui` - for installing the latest release of CILViewer, with packages needed to run the GUI.


## Script for Testing CIL demos

`test_notebooks_sequential.py` is a script for testing the CIL-Demos

To use it:
1. Clone [CIL-Demos](https://github.com/TomographicImaging/CIL-Demos), if you haven't already, and move to the branch of CIL-Demos you would like to test.
2. Clone [scripts](https://github.com/TomographicImaging/scripts)
3. Download all datasets used by the [CIL-Demos](https://github.com/TomographicImaging/CIL-Demos) notebooks you would like to test.
4. Create an environment using: 
    ```sh
    conda env create -f https://tomographicimaging.github.io/scripts/env/cil_test_demos.yml
    ```
5. Clone [CIL](https://github.com/TomographicImaging/CIL), if you haven't already, and move to the branch of CIL you would like to test the demos with.
6. Activate the environment you created:
    ```sh
    conda activate cil_test_demos
    ```
7. Navigate into the CIL directory and install CIL into this environment:
    ```sh
    pip install -e .
    ```
8. The script uses `nbmake` and needs to point to the kernel to run the notebooks with. We need to make sure our conda environment is registered with the correct jupyter kernel name. Run:
    ```sh
    jupyter kernelspec list
    ```
    If there is a kernel with name `cil_test_demos` then move to step 9. If not, run:
    ```sh
    python -m ipykernel install --user --name cil_test_demos --display-name "cil_test_demos"
    ```
9. At the top of the `test_notebooks_sequential.py` file, update these variables:
    `CIL_DEMOS_DIR` - should point to your clone of CIL-Demos
    `DATA_PATH` and `DATA_PATH_ALT` should point to directories where the CIL-Demos data is saved.
10. Run `test_notebooks_sequential.py`. This is likely to take quite a long time. It will create the following inside the current directory:

    `test_notebooks_*.log` log file (with name including date and time of run): This shows which notebooks have run and whether they have passed or failed.

    `tmp_notebooks` directory: This contains the run and rendered `.ipynb` notebook files.
    

