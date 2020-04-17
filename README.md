slivka-bio
==========

Slivka-bio is a pre-configured instance of a slivka project using conda
targeted for bioinformatics. It contains configurations for tools such
as Clustal Omega, ClustalW2, Muscle, IUPred, Mafft and more.
The goal is to provide (almost) ready to use package which bundles
bioinformatic software in one tool.
The applications currently available include:

 - [Clustal Omega](http://www.clustal.org/omega/)
 - [ClustalW2](http://www.clustal.org/clustal2/)
 - [MUSCLE](https://www.drive5.com/muscle/)
 - [T-Coffee](http://tcoffee.org/)
 - [AACon](https://www.compbio.dundee.ac.uk/aacon/)
 - [IUPred](http://iupred.enzim.hu) (sources not included)
 - [MAFFT](https://mafft.cbrc.jp/alignment/software/)
 - [ProbCons](http://probcons.stanford.edu/)
 - [MSAProbs](http://msaprobs.sourceforge.net/homepage.htm)
 - [GlobPlot](http://globplot.embl.de/)
 - [DisEMBL](http://dis.embl.de/)
 - JRonn (Java implementation of [RONN](https://www.bioinformatics.nl/~berndb/ronn.html))
 - [JPred](https://www.compbio.dundee.ac.uk/jpred/index_up.html)

Quick Install with Conda
========================
The easiest way to install slivka-bio with all the tools and dependencies
is by using pre-defined conda environment available from our anaconda channel.
If you don't have conda installed on your system, follow the miniconda installation
from [conda user guide](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html).
Then, run
```
conda install anaconda-client -n base
conda env create mmwarowny/compbio-services
conda activate compbio-services
```
It will automatically fetch the exported environemnt file and re-create this environment
on your local machine. After activating the new environment *compbio-services*
slivka-bio will be ready to use.
Follow to the [configuration](#configuration) section if you need to customise
settings.

Slivka Installation
===================

The recommended way to install slivka and its dependencies is through
conda package manager. If you don't have conda installed on your system
yet, follow the miniconda installation instructions from
[conda user guide](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html).
Once the conda installation completes, create a new conda environment
that will use python version 3.7 and activate it. Substitute the
environment name of your choice for `slivka` if needed.

```
$ conda create -n slivka python=3.7
$ conda activate slivka
```

Next, you may verify that python commands is pointing to the binary in the new environment.
The output of `which` command should be the path in the miniconda envs directory as in the following example.

```
$ which python
/home/<username>/miniconda3/envs/slivka/bin/python
```

Next, you need to download and install Slivka python package as well as slivka-bio configuration files from our github repository.
For the time being, we recommend using the version from the dev branch until the first stable version is released.

```
$ git clone --branch dev --single-branch https://github.com/warownia1/Slivka.git
$ (cd Slivka; python setup.py install)
$ git clone --branch dev --single-branch https://github.com/warownia1/slivka-bio.git
```

Slivka-bio also comes with some dependencies which are listed in the *environment.yml* file.
They can be automatically installed using conda.
```
$ cd slivka-bio
$ conda env update -f environment.yml
```

### MongoDB ###

Slivka depends on [MongoDB](https://www.mongodb.com) for exchanging and storing data.
Ask your system administrator for installation and access to the mongo database on your system or, if you need user installation only, mongodb is available through conda in *anaconda* channel.
Once installed, MongoDB process can be started using `mongod` command.
More information on available command line parameters and configuration can be found in the [mongod documentation](https://docs.mongodb.com/manual/reference/program/mongod/).

### WSGI server ###

Web Service Gateway Interface is a convention for web servers to forward HTTP requests to python application.
Recommeded middleware supported by Slivka include [Gunicorn](https://gunicorn.org/) and [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/).
You need to install one of those (both available as conda packages) to use slivka server.
If you want to use other software the wsgi application is located in the *wsgi.py* module file and is named *application*.

Bioinformatic Tools Installation
================================

Most of the bioinformatic tools that slivka uses are available from bioconda channel or have their sources or binaries shipped with slivka-bio.

Bioconda
--------
Tools ClustalO, ClustalW, MUSCLE, T-Coffee, MSAProbs, Probcons and MAFFT are available from bioconda channel in the conda package manager, which you should already have installed if you followed this guide.

You can install each tool running the following commands from the slivka-bio directory (remember to have *slivka* environment activated)

```
$ make clustalo
$ make clustalw
$ make muscle
$ make probcons
$ make tcoffee
$ make msaprobs
$ make probcons
$ make mafft
```

If you prefer doing it the hard way you can add bioconda and conda-forge channels

```
$ conda config --add channels defaults
$ conda config --add channels bioconda
$ conda config --add channels conda-forge
```

and then install tools of your choice using

```
$ conda install clustalo clustalw \
    muscle t_coffee msaprobs probcons mafft
```

Java
----
Tools AACon and JRonn are shipped as a compiled Java executables and require Java 1.8 or later to be installed on your system. Most system provide Java Runtime Environment out-of-the-box but if it's not the case you can install it using conda.
```
$ conda install openjdk
```

Compiling sources
-----------------
Tools DisEMBL, GlobPlot and IUPred need to be compiled for your system architecture from the sources for best compatibility and performance.

Due to legal limitations IUPred sources could not be included in the slivka-bio package.
If you wish to use it, you can download it from [iupred website](http://iupred.enzim.hu/Downloads.php).
Once you obtain the archive extract it and place the sources in the *bin/iupred* directory.

The tools for building C, C++ and Fortran software are part of the GNU toolchain.
Make sure that `make`, `gcc` and `g++` are available on you system.

On Debian/Ubuntu/Mint they can be installed with
```
$ apt-get install make gcc g++ gfortran
```

On CentOS/Redhat/Fedora they are available as part of the Development Tools
```
$ yum group install "Development Tools"
```

For other operating system refer to you package manager repositories.
The compilers may also be available as conda packages.
Check out [anaconda cloud](https://anaconda.org/search) for the packages matching your operatig system and CPU architecture.

Once the compiler tools are installed you can build the tools you want to use.
```
$ make disembl
$ make globplot
$ make iupred
```


Configuration
=============

Slivka-bio configuration is organised into multiple files.
Basic configuration is located in the *settings.yaml* file
in the repository root directory
The configurations for each service is located in its respective file
in services folder.
If slivka-bio was installed with conda package manager, the configuration
files are located at ``$CONDA_PREFIX/var/slivka-bio``

General configuration
---------------------
The basic configuration is stored in the *settings.yaml* file and it defines
constants and parameters used by all Slivka components.
Some of the parameter listed below may need to be modified to make sure
that the Slivka server will work properly.
It's recommended to leave remaining parameters unchanged.

| parameter | description |
|:----------|:------------|
| `ACCEPTED_MEDIA_TYPES` | The list of media types that can be uploaded to the server. This feature is deprecated and will be removed in future versions. |
| `SECRET_KEY` | A random string of characters used for signing sensitive data and hashes. Change to the random sequence of characters (at least 24 characters long) |
| `SERVER_HOST` | The address which the server can accept the connections from. Use `127.0.0.1` if you want to restrict access to the local machine only or `0.0.0.0` to make is publicly visible. Restricting access and using reverse proxy is highly recommended for public servers. |
| `SERVER_PORT` | The port number which the server will be listening on for incoming connections. Make sure you have permission to listen on the port specified. |
| `SLIVKA_QUEUE_ADDR` | The address which the local queue will use to communicate with the scheduler. Can be either *tcp* or *unix* socket e.g. `tcp://127.0.0.1:4444` or `unix:///tmp/slivka.sock`. This settings only applies if you use local slivka queueing system. |
| `MONGODB` | The address used to connect to the MontoDB following [MonogDB URI format](https://docs.mongodb.com/manual/reference/connection-string) Default is `mongodb://127.0.0.1:27017/slivka` |

Enabled services
----------------
For each configuration file in the *services* directory, Slivka will attempt
to create a new service. The filename must follow the *<name>.service.yaml*
pattern in order to be recognised.
In order to disable one or more services, simply remove their configuration
files from *services* directory or change the filename to one not matching
the pattern i.e. append *.disabled* to the file extension

Advanced configuration
----------------------
This guide will not cover service configuration. Refer to the
[slivka documentation](http://warownia1.github.io/Slivka/getting_started.html#services-configuration)
if you need to adjust command line parameters or customise runners.

Launching
=========

Once you finished the configuration step, you can deploy your own slivka server.
First, navigate to the slivka configuration directory (the one having
*settings.yaml* in it). Alternatively, you can set *SLIVKA_HOME* environment
variable poitning to that directory.
For slivka to operate properly, you need to start its three processes:
http server which manager incoming connections, scheduler which collects
and dispatches incoming job requests, local-queue which stacks and runs
incoming jobs on the local machine.

The three processes are launched using `slivka` command created during
slivka installation. Alternatively, you can use *manage.py* script
located in the project directory which automatically sets *SLIVKA_HOME*
variable when started.
If you had slivka-bio installed as a conda package, use `slivka-bio`
command instead.
All other command line parameters
remain the same.

### Server ###
```
slivka start server [-t TYPE] [-d -p PID_FILE] [-w WORKERS]
```
Starts the HTTP server using WSGI application specified by *TYPE*.
Allowed values are `devel`, `uwsgi` or `gunicorn`. The specified
application must be installed and available in the *PATH*.
The development server is always available, but it can't serve more
than one client at the time therefore it's not recommended for production.

If you want to make your server publicly accessible, we recommend running
it behind a reverse proxy server. Refer to your wsgi application
documentation for more details.

Providing `-d` flag along with `-p PID_FILE` starts the process in
background as a daemon and writes its pid to the file.

You can also specify the number of worker processes explicitly.
Defaults to twice the cpu-count.

### Scheduler ###
```
slivka start scheduler [-d -p PID_FILE]
```
Starts the scheduler that collects and dispatches new jobs and monitors their states.
Providing `-d` flag starts the scheduler as a daemon and `-p PID_FILE`
specifies the pid file location.

### Local queue ###
```
slivka start local-queue [-d -p PID_FILE] [-w WORKERS]
```
This is a default job runner which spawns new jobs as subprocesses on
the local machine. If you specify `-d` and `-p PID_FILE` the process
will run as a daemon and write its pid to the specified file.

Additionally, you may specify the number of workers i.e. the number
of jobs which can be run simultaneously. Defaults to 2.

