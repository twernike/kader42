#!/bin/bash

# 1. RAM in GB ermitteln
total_ram_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
total_ram_gb=$(( (total_ram_kb + 500000) / 1024 / 1024 )) 

echo "Hardware-Check: $total_ram_gb GB RAM found."

# 2. Entscheidung treffen (Schwelle: 4 GB)
# if [ "$total_ram_gb" -le 9 ]; then
#     echo "Mode: Low-RAM. Activate static logo (kader42-minimal)."
#     plymouth-set-default-theme -R kader42-minimal
# else
#     echo "Mode: Performance. Activate animated logo (mello42)."
#     plymouth-set-default-theme -R mello42
# fi

plymouth-set-default-theme -R kader42-mello
