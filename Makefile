.PHONY : help
help :
	echo usage: make [tool]

.PHONY : probcons
probcons :
	(cd bin/probcons && make all)

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
	(cd bin/MSAProbs && make all)

.PHONY : disembl
disembl: bin/Tisean_3.0.1/source_c/sav_gol
	(cd bin/disembl && gcc -O3 disembl.c -o disembl)
	cp bin/Tisean_3.0.1/source_c/sav_gol bin/disembl/sav_gol

.PHONY : globplot
globplot: bin/Tisean_3.0.1/source_c/sav_gol
	cp bin/Tisean_3.0.1/source_c/sav_gol bin/globplot/sav_gol

bin/Tisean_3.0.1/source_c/sav_gol:
	tar xf bin/TISEAN_3.0.1.tar.gz -C bin
	(cd bin/Tisean_3.0.1 && ./configure)
	(cd bin/Tisean_3.0.1/source_c && make sav_gol)

.PHONY : iupred
iupred :
	(cd bin/iupred && cc iupred.c -o iupred)
