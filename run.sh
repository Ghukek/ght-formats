#!/bin/sh

echo "Starting Python tasks..."

python3 export_usfm.py ../concordance.db
python3 convert_usx.py 
python3 eswordexport.py

echo "Finished."
