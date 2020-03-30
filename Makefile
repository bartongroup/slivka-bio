.PHONY : help
help :
	echo usage: make [tool]

.PHONY : probcons
probcons :
	conda install -c bioconda probcons

.PHONY : mafft
mafft :
	conda install -c bioconda mafft

.PHONY : tcoffee
tcoffee :
	conda install -c bioconda t_coffee

.PHONY : muscle
muscle :
	conda install -c bioconda muscle

.PHONY : clustalw
clustalw :
	conda install -c bioconda clustalw

.PHONY : clustalo
clustalo :
	conda install -c bioconda clustalo

.PHONY : msaprobs
msaprobs :
	conda install -c mmwarowny msaprobs 

.PHONY : disembl
disembl : 
	conda install -c mmwarowny disembl 

.PHONY : globplot
globplot :
	conda install -c mmwarowny globplot 

.PHONY : iupred
iupred :
	(cd bin/iupred && cc iupred.c -o iupred)
