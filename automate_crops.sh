#!/bin/bash 
crops_loc="/opt/crops"
tr_add_loc="/opttransmission-add-crops"
transmission_loc="/var/ddata/autoget/transmission-user"
crops_out_loc="${transmission_loc}/crops-out"

if [ ! -d "$crops_out_loc" ]; then
    mkdir -p "$crops_out_loc"
fi

. "${crops_loc}/env/bin/activate"
python "${crops_loc}/src/main.py" -i "${transmission_loc}/torrents" -o "$crops_out_loc"
deactivate 

. "${tr_add_loc}/env/bin/activate"
python "${tr_add_loc}/tr-add-crops.py" --remove  "$crops_out_loc"
deactivate 