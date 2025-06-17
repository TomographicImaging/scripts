# CIL - Core Imaging Library

[![CI-master](https://github.com/TomographicImaging/CIL/actions/workflows/build.yml/badge.svg)](https://github.com/TomographicImaging/CIL/actions/workflows/build.yml) ![conda-ver](https://anaconda.org/ccpi/cil/badges/version.svg) ![conda-date](https://anaconda.org/ccpi/cil/badges/latest_release_date.svg) [![conda-plat](https://anaconda.org/ccpi/cil/badges/platforms.svg) ![conda-dl](https://anaconda.org/ccpi/cil/badges/downloads.svg)](https://anaconda.org/ccpi/cil)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/TomographicImaging/CIL-Demos/HEAD?urlpath=lab/tree/binder%2Findex.ipynb)

The Core Imaging Library (CIL) is an open-source Python framework for tomographic imaging with particular emphasis on reconstruction of challenging datasets. Conventional filtered backprojection reconstruction tends to be insufficient for highly noisy, incomplete, non-standard or multichannel data arising for example in dynamic, spectral and in situ tomography. CIL provides an extensive modular optimisation framework for prototyping reconstruction methods including sparsity and total variation regularisation, as well as tools for loading, preprocessing and visualising tomographic data.

## Documentation

The documentation for CIL can be accessed [here](https://tomographicimaging.github.io/CIL).
## Installation instructions
CIL can be installed with one of the following methods

| Method             | Description                          |
|--------------------|--------------------------------------|
| [Conda](#installation-with-conda) | Recommended for most users. Install a tested combination of Python and Numpy |
| [Docker](#running-in-a-docker-container)  | Run a tested version via a Jupyter notebook| 
| [Build from source](#building-cil-from-source-code)| Recommended for experienced users who want to edit the code |

### Dependencies
CIL is tested with the following required dependencies
- Python versions 3.10-3.11
- Numpy versions 1.23-1.26
  
The following dependencies are optional
- astra-toolbox enables CIL support for [ASTRA toolbox](http://www.astra-toolbox.com) CPU projector (2D Parallel beam only) and GPU projectors (GPLv3 license)
- tigre (requires an NVIDIA GPU) enables support for [TIGRE](https://github.com/CERN/TIGRE) toolbox projectors (BSD license)
- ccpi-regulariser is the [CCPi Regularisation Toolkit](https://github.com/TomographicImaging/CCPi-Regularisation-Toolkit)
- tomophantom can generate phantoms to use as test data [Tomophantom](https://github.com/dkazanc/TomoPhantom)
- ipykernel  provides the IPython kernel for Jupyter (allowing jupyter notebooks to be run)
- ipywidgets enables visulisation tools within jupyter noteboooks

## Getting Started with CIL

### CIL Training

We typically run training courses at least twice a year - check <https://ccpi.ac.uk/training/> for our upcoming events!

### CIL on binder

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/TomographicImaging/CIL-Demos/HEAD?urlpath=lab/tree/binder%2Findex.ipynb)

Jupyter Notebooks usage examples without any local installation are provided in [Binder](https://mybinder.org/v2/gh/TomographicImaging/CIL-Demos/HEAD?urlpath=lab/tree/binder%2Findex.ipynb). Please click the launch binder icon above. For more information, go to [CIL-Demos](https://github.com/TomographicImaging/CIL-Demos) and [https://mybinder.org](https://mybinder.org).

### CIL Videos

- [PyCon DE & PyData Berlin 2022](https://2022.pycon.de), Apr 2022: [Abstract](https://2022.pycon.de/program/GSLJUY), [Video](https://www.youtube.com/watch?v=Xd4erPj0uEs), [Material](https://github.com/TomographicImaging/CIL-Demos/blob/main/binder/PyData22_deblurring.ipynb)
- [Training School for the Synergistic Image Reconstruction Framework (SIRF) and Core Imaging Library (CIL)](https://www.ccpsynerbi.ac.uk/SIRFCIL2021), Jun 2021: [Videos](https://www.youtube.com/playlist?list=PLTuAla-OP8WVNPWZfis6BRsWFq_S0bqvp), [Material](https://github.com/TomographicImaging/CIL-Demos/tree/main/training/2021_Fully3D)
- [Synergistic Reconstruction Symposium](https://www.ccpsynerbi.ac.uk/symposium2019), Nov 2019: [Slides](https://www.ccppetmr.ac.uk/sites/www.ccppetmr.ac.uk/files/Papoutsellis%202.pdf), [Videos](https://www.youtube.com/playlist?list=PLyxAZuV8tuKsOY4DTDzy04DRrwkxBkTYh), [Material](https://github.com/TomographicImaging/CIL-Demos/tree/main/training/2019_SynergisticSymposium)


### Installation with Conda
Binary installation of CIL can be achieved with conda.

We recommend using either miniconda or miniforge, which are both minimal installers for conda. We also recommend a conda version of at least 23.10 for quicker installation.

Create an environment with minimal depdendencies required to run cil using
```bash
conda env create -f https://raw.githubusercontent.com/TomographicImaging/Build-scripts/refs/heads/main/env_files/cil_env.yml
```
or include all the dependencies required to run our demos with
```bash
conda env create -f https://raw.githubusercontent.com/TomographicImaging/Build-scripts/refs/heads/main/env_files/cil_demos_env.yml
```


### Running in a Docker container
Finally, CIL can be run via a Jupyter Notebook enabled Docker container:

```sh
docker run --rm --gpus all -p 8888:8888 -it ghcr.io/tomographicimaging/cil:latest
```

> [!TIP]
> docker tag | CIL branch/tag
> :---|:---
> `latest` | [latest tag `v*.*.*`](https://github.com/TomographicImaging/CIL/releases/latest)
> `YY.M` | latest tag `vYY.M.*`
> `YY.M.m` | tag `vYY.M.m`
> `master` | `master`
> only build & test (no tag) | CI (current commit)
>
> See [`ghcr.io/tomographicimaging/cil`](https://github.com/TomographicImaging/CIL/pkgs/container/cil) for a full list of tags.

<!-- <br/> -->

> [!NOTE]
> GPU support requires [`nvidia-container-toolkit`](https://github.com/NVIDIA/nvidia-container-toolkit) and an NVIDIA GPU.
> Omit the `--gpus all` to run without GPU support.

<!-- <br/> -->

> [!IMPORTANT]
> Folders can be shared with the correct (host) user permissions using
> `--user $(id -u) --group-add users -v /local/path:/container/path`
> where `/local/path` is an existing directory on your local (host) machine which will be mounted at `/container/path` in the docker container.

<!-- <br/> -->

> [!TIP]
> See [jupyter-docker-stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/common.html) for more information.

### Building CIL from source code

#### Getting the code

In case of development it is useful to be able to build the software directly. You should clone this repository as

```sh
git clone --recurse-submodule git@github.com:TomographicImaging/CIL
```

The use of `--recurse-submodule` is necessary if the user wants the examples data to be fetched (they are needed by the unit tests). We have moved such data, previously hosted in this repo at `Wrappers/Python/data` to the [CIL-data](https://github.com/TomographicImaging/CIL-Data) repository and linked it to this one as submodule. If the data is not available it can be fetched in an already cloned repository as

```sh
git submodule update --init --recursive
```

#### Building with `pip`

##### Install Dependencies

To create a conda environment with all the dependencies for building CIL run the following shell script:

```sh
bash ./scripts/create_local_env_for_cil_development.sh
```

Or with the CIL build and test dependencies:

```sh
bash ./scripts/create_local_env_for_cil_development.sh -t
```

And then install CIL in to this environment using `pip`.

Alternatively, one can use the `scripts/requirements-test.yml` to create a conda environment with all the
appropriate dependencies on any OS, using the following command:

```sh
conda env create -f ./scripts/requirements-test.yml
```

##### Build CIL

A C++ compiler is required to build the source code. Let's suppose that the user is in the source directory, then the following commands should work:

```sh
pip install --no-deps .
```

If not installing inside a conda environment, then the user might need to set the locations of optional libraries:

```sh
pip install . -Ccmake.define.IPP_ROOT="<path_to_ipp>" -Ccmake.define.OpenMP_ROOT="<path_to_openmp>"
```

#### Building with Docker

In the repository root, simply update submodules and run `docker build`:

```sh
git submodule update --init --recursive
docker build . -t ghcr.io/tomographicimaging/cil
```

#### Testing

One installed, CIL functionality can be tested using the following command:

```sh
export TESTS_FORCE_GPU=1  # optional, makes GPU test failures noisy
python -m unittest discover -v ./Wrappers/Python/test
```
****
