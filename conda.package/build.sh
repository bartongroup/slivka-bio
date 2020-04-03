mkdir -p $PREFIX/var
mkdir -p $PREFIX/bin  
cp -r slivka-bio $PREFIX/var/
cp slivka-bio/manage.py $PREFIX/bin/slivka-start
chmod u=rwx,g=rx,o=r $PREFIX/bin/slivka-start

