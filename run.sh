#!/bin/sh

echo "Starting Python tasks..."

cp ../concordance.db concordance.db

python3 export_usfm.py concordance.db 

#for f in ./ght_usfm/*.usfm; do
#  base=$(basename "$f" .usfm)
#  python3 ./u2o/u2o.py GHT "$f" -o "./ght_osis/${base}.osis.xml"
#done

#for f in ./ghtg_usfm/*.usfm; do
#  base=$(basename "$f" .usfm)
#  python3 ./u2o/u2o.py GHTG "$f" -o "./ghtg_osis/${base}.osis.xml"
#done

python3 ./u2o/u2o.py -l en GHT ./ght_usfm/*.usfm -o ./ght.osis.xml
python3 ./u2o/u2o.py -l grc GHTG ./ghtg_usfm/*.usfm -o ./ghtg.osis.xml

python3 convert_usx.py 
python3 eswordexport.py

#Added to watch for any error flags.
osis2mod ../OSIS/ ghtg.conf
osis2mod ../OSIS/ ght.conf

echo "Finished."
