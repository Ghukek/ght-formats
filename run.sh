#!/bin/sh

echo "Starting Python tasks..."

python3 export_usfm.py ../concordance.db 1

#for f in ./ght_usfm/*.usfm; do
#  base=$(basename "$f" .usfm)
#  python3 ./u2o/u2o.py GHT "$f" -o "./ght_osis/${base}.osis.xml"
#done

#for f in ./ghtg_usfm/*.usfm; do
#  base=$(basename "$f" .usfm)
#  python3 ./u2o/u2o.py GHTG "$f" -o "./ghtg_osis/${base}.osis.xml"
#done

python3 ./u2o/u2o.py -l en GHT ./ght_usfm/*.usfm -o ./GHT.osis.xml
python3 ./u2o/u2o.py -l grc GHTG ./ghtg_usfm/*.usfm -o ./GHTG.osis.xml

python3 export_usfm.py ../concordance.db
python3 convert_usx.py 
python3 eswordexport.py

echo "Finished."
