sudo rm -rf log/log.txt

mkdir -p log
sh -x buildiso.sh >> log/log.txt
