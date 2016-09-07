#! /bin/sh

file=`mktemp`
cat<<EOF > $file
import GPOF.strategies as gs
import GPOF.runset as gr
import GPOF.display as gd
EOF


ipython  -i --pylab=qt $file

rm $file
