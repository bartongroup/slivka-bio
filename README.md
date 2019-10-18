slivka-bio
==========

Slivka-bio is a pre-configured instance of a slivka project using conda targeted for bioinformatics.
It contains configurations for tools such as Clustal Omega, ClustalW2, Muscle, IUPred, Mafft and more.
The goal is to provide (almost) ready to use package which bundles all the most important tools.

Installation
============

Most of the sources for the bioinformatic software is already bundled in the `bin` directory.
For the best compatibility and performance they need to be compiled from the sources for each operating system.
Compliation of the tools require Fortran, C and C++ compilers to be available.
Additionally, some of the tools used are distributed as conda packages, so conda package manager is also required.

Conda
-----
Miniconda, which is a minimal installer for conda, can be downloaded from [conda website](https://docs.conda.io/en/latest/miniconda.html).
When the installation is complete, you can create a new environment e.g. "slivka-bio" for the project dependencies with

    conda env create -n slivka-bio

After that, activate the new environment using 

    conda activate slivka-bio

GNU toolchain
-------------
A commonly used tools for building C, C++ and Fortran software are part of the GNU toolchain.
Before you can compile the sources, make sure that `make`, `cc`, `g++` and `f77` are available on your system.
On most UNIX systems they are included in `make`, `gcc`, `g++` and `gfortran` packages respectively.
For debian-based systems (Debian, Ubuntu) use:

    apt-get install make gcc g++ gfortran

On CentOS (Redhat, Fedora) you can install them with:

    yum group install "Development Tools"

For other operating systems refer to your package manager documentation.
The compilers may also be available as conda packages.
Check out [anaconda cloud](https://anaconda.org/search) for the packages matching your operatig system and CPU architecture.

Installation
------------
Once all the tools are installed, navigate to the project directory and run

    make all

which will compile all the programs from their sources and download and install necessary conda packages.
The packages will be installed to the currently active conda environment so make sure to activate it before executing `make`.

Mongodb
-------
Slivka relies of mongodb as a message broker and a persistent data storage.
If mongodb is not provided on your system, you can install it through conda with:

    conda install -c anaconda mongodb

and start it with:

    mongod --dbpath /path/to/mongo/data

Refer to [mongod documentation](https://docs.mongodb.com/manual/reference/program/mongod/)
for more information about available command line parameters and mongodb configuration.

IUPred
------
Due to the legal limitations, we could not bundle IUPred tool within the slivka package.
If you wish to use UIPred you can obtain it from its author's [website](http://iupred.enzim.hu/).
Extract the archive to the project's `bin` directory and follow the compilation instructions provided with IUPred.
Otherwise, comment-out or delete the iupred section from `services.yml` configuration file.


Configuration
=============

The main project configuration is stored in the `settings.yml` file.
The following properties may need to be modified for proper operation,
(it's recommended to leave other parameters unchanged):

| parameter | description |
|-----------|-------------|
|`UPLOADS_DIR`|Directory where the uploaded files are stored. Absolute or relative path.|
|`JOBS_DIR`|Directory where the job working directories will be created.|
|`UPLOADS_URL_PATH`|URI where uploaded files will be available for download at.|
|`JOBS_URL_PATH`|URI where job files from `JOBS_DIR` will be available at.|
|`SECRET_KEY`|A key used for authentication. Change it to random ascii letters.|
|`SERVER_HOST`|Address which the server will accept connections from. Set to `0.0.0.0` to accept all connection or to the proxy server address if using behind the proxy.|
|`SERVER_PORT`|A port the REST server will be listening at.|
|`SLIVKA_QUEUE_ADDR`|The address of slivka-local-queue. Can be either TCP address or UNIX domain socket.|
|`MONGODB_ADDR`|Address of mongo database following [MongoDB URI format](https://docs.mongodb.com/manual/reference/connection-string/). Default is `mongodb://127.0.0.1:27017`.|


Running the project
===================

Once you have mongod server running you can start slivka-bio.
Three processes: server, scheduler and local queue are preferrably started through `manage.py` script.

    python manage.py server -t gunicorn
    python manage.py scheduler
    python manage.py local-queue

They can work in the background or be started in separate screens.
For convenience, the `slivkad` script can be used to start|stop|restart slivka manually or use it as a init.d service.
