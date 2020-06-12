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


Quick Installation with Conda
=============================

The easiest way to install slivka-bio with all the tools and dependencies
is by using pre-defined conda environment available from our anaconda channel.
If you don't have conda installed on your system, follow the miniconda
installation from [conda user guide](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html).
Then, run

```sh
conda install anaconda-client -n base
conda env create mmwarowny/compbio-services
conda activate compbio-services
```

It will automatically fetch the exported environemnt file and re-create
the environment on your local machine. After activating the new
environment - *compbio-services* slivka-bio will be ready to use.
Follow to the [configuration](#configuration) section if you need to
customise settings.


Manual Installation
===================

Installing slivka
-----------------

The recommended way to manage slivka installation and dependencies
is through conda package manager. If you don't have conda installed
on your system yet, follow the miniconda installation instructions
from [conda user guide](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html).
Once the conda installation completes, create a new conda environment
with python version 3.7 and activate it. Substitute the environment
name of your choice for `slivka` if needed.

```sh
conda create -n slivka python=3.7
conda activate slivka
```

Make sure that ``python`` executable points to the binary located
in the conda environment.
Next, download and install Slivka python package as well
as slivka-bio configuration files from our github repository.
For the time being, we recommend using the version from the dev branch
until the first stable version is released.

```sh
git clone --branch dev --single-branch https://github.com/bartongroup/slivka.git
(cd slivka; python setup.py install)
git clone --branch dev --single-branch https://github.com/bartongroup/slivka-bio.git
```

Keep in mind that slivka-bio does not include any bioinformatic tools.
If you choose this installation route, you need to provide them by yourself.

Installing bioinformatic tools
------------------------------

If you chose to install slivka-bio using conda then all the tools,
except IUPred, have beed installed automatically.
However, if you decided to install them manually, most of the
bioinformatic tools that slivka uses are available from
bioconda, our private conda channel or are shipped with slivka-bio.

### Bioconda ###

Tools: ClustalO, ClustalW, MUSCLE, T-Coffee, MSAProbs, Probcons and
MAFFT can be installed with conda package manager from bioconda channel.

You can install each tool running the following commands
(remember to activate the conda environment first)

```sh
conda config --add channels conda-forge
conda config --add channels bioconda
conda install clustalo clustalw muscle t_coffee msaprobs probcons mafft
```

### Private conda channel ###

Tools: DisEMBL and GlobPlot as well as a more recent version of
T-Coffee for macOS and linux are available from the *mmwarowny* channel.

```sh
conda config --add channels mmwarowny
conda install disembl globplot t_coffee
```

### Java ###

Tools AACon and JRonn are shipped as compiled Java executables and
require Java 1.8 or later to be installed on your system. Most system
provide Java Runtime Environment out-of-the-box but if it's not the
case you can install it using conda.

```sh
conda install openjdk
```

### Building from sources ###

It is highly recommended to install the bioinformatic tools using
the package managers.
However, if you prefer building bioinformtic tools from the sources
and have a full controll over the installation process you are free
to do so.
After the compilation, make sure that the binary location is included
in the PATH variable or set the absolute path to the binary in the
service configuration file.

#### IUPred ####

Due to the legal limitations, IUPred sources could not be included in
the slivka-bio package nor can be provided through conda.
If you wish to use it, you can download the sources from
[iupred website](http://iupred.enzim.hu/Downloads.php).
Then, place them in *bin/iupred* directory and run ``make iupred``.

Compiling IUPred requires C compiler which is a part of the GNU
toolchain to be installed on your system.
Make sure that `make` and `gcc` are available on you system.

On Debian/Ubuntu/Mint they can be installed with
```sh
apt-get install make gcc
```

On CentOS/Redhat/Fedora they are available as part of the Development Tools
```sh
yum group install "Development Tools"
```

Using homebrew on MacOS
```sh
brew install make gcc
```

Using conda package manager
```sh
conda install gcc_linux-64  # linux
conda install clang_osx-64  # MacOS
```

For other operating systems refer to you package manager repositories.

## WSGI server ##

Web Service Gateway Interface is a convention for web servers to
forward HTTP requests to python application.
Recommeded middleware supported by Slivka include
[Gunicorn](https://gunicorn.org/) and
[uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/).
You need to install one of those (both available as conda packages)
to use slivka server.
If you want to use other software the wsgi application is located in
the *wsgi.py* module file and is named *application*.


Configuration
=============

Slivka-bio configuration is organised into multiple files.
Basic configuration is located in the *settings.yaml* file
in the repository root directory
The configurations for each service is located in its respective file
in the *services* folder.
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
For each configuration file in the *services* directory named
*<name>.service.yaml*, where *<name>* should be substituted for the
service name, Slivka will attempt to instantiate a new service.
In order to disable one or more services, simply remove their
configuration files from *services* directory or change the filename
to one not matching the pattern i.e. append *.disabled* to the file
extension.

Advanced configuration
----------------------
This guide will not cover service configuration. Refer to the
[slivka documentation](http://bartongroup.github.io/slivka/getting_started.html#services-configuration)
if you need to adjust command line parameters or customise runners.

Launching
=========

## MongoDB ##

Slivka depends on [MongoDB](https://www.mongodb.com) for exchanging
and storing data.
Ask your system administrator for installation and access to the mongo
database on your system or, if you need user installation only, mongodb
is available through conda in *anaconda* channel.
Once installed, MongoDB process can be started using `mongod` command.
More information on available command line parameters and configuration
can be found in the [mongod documentation](https://docs.mongodb.com/manual/reference/program/mongod/).

## Slivka ##

Once you finished the configuration step, you can deploy your own
slivka server.
First, navigate to the slivka configuration directory (the one having
*settings.yaml* in it). Alternatively, you can set *SLIVKA_HOME*
environment variable poitning to that directory.
For slivka to operate properly, you need to start its three processes:
http server which manager incoming connections, scheduler which collects
and dispatches incoming job requests, local-queue which stacks and runs
incoming jobs on the local machine.

The three processes are launched using `slivka` command created during
slivka installation. Alternatively, you can use *manage.py* script
located in the project directory which automatically sets *SLIVKA_HOME*
variable when started.
If you had slivka-bio installed as a conda package, use `slivka-bio`
command instead. All other command line parameters remain the same.

### Server ###
```sh
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
```sh
slivka start scheduler [-d -p PID_FILE]
```
Starts the scheduler that collects and dispatches new jobs and monitors their states.
Providing `-d` flag starts the scheduler as a daemon and `-p PID_FILE`
specifies the pid file location.

### Local queue ###
```sh
slivka start local-queue [-d -p PID_FILE] [-w WORKERS]
```
This is a default job runner which spawns new jobs as subprocesses on
the local machine. If you specify `-d` and `-p PID_FILE` the process
will run as a daemon and write its pid to the specified file.

Additionally, you may specify the number of workers i.e. the number
of jobs which can be run simultaneously. Defaults to 2.

