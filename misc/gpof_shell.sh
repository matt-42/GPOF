#! /bin/sh

file=`mktemp`
cat<<EOF > $file
import gpof
EOF


ipython  -i --pylab=qt $file

rm $file
