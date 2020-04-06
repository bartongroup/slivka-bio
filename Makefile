.PHONY : help
help :
	echo usage: make [tool]

.PHONY : probcons
probcons :
	conda install -c bioconda -c conda-forge probcons

.PHONY : mafft
mafft :
	conda install -c bioconda -c conda-forge mafft

.PHONY : tcoffee
tcoffee :
	conda install -c bioconda -c conda-forge t_coffee

.PHONY : muscle
muscle :
	conda install -c bioconda -c conda-forge muscle

.PHONY : clustalw
clustalw :
	conda install -c bioconda -c conda-forge clustalw

.PHONY : clustalo
clustalo :
	conda install -c bioconda -c conda-forge clustalo

.PHONY : msaprobs
msaprobs :
	conda install -c bioconda -c conda-forge msaprobs

.PHONY : disembl
disembl : 
	conda install -c mmwarowny -c conda-forge disembl

.PHONY : globplot
globplot :
	conda install -c mmwarowny -c conda-forge globplot

.PHONY : iupred
iupred :
	(cd bin/iupred && cc iupred.c -o iupred)
