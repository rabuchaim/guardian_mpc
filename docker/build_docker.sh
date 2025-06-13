#!/usr/bin/bash -x
set -x

TAG=1.0.0
SERVER=guardian-mpc
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")
LOG_FILE="${SERVER}-${TAG}-${TIMESTAMP}.log"

rm -rvf files

rm -vf guardian-mpc-files.tar.gz

mkdir -p files/server/mpc_database

cp gunicorn.conf.py files/server/

cp ../manage.py files/server/manage.py

cp -rfp ../mpc_core files/server/

cp -rfp ../mpc_contracts files/server/

find . -name __pycache__ -type d -exec rm -rf {} \;

find . -name "000*.py" -type f -exec rm -vf {} \;

chown -R root.root files

cd files 

tar zcvf ../guardian-mpc-files.tar.gz -h --preserve-permissions .

cd ..

sudo docker stop "$SERVER"

sudo docker rm "$SERVER"

sudo docker build -t $SERVER:$TAG --compress --no-cache --force-rm -f Dockerfile.ubuntu . 2>&1 | tee "$LOG_FILE"

sudo docker run -it -d --cpus="1" --memory="1G" --memory-reservation="1G" \
    --dns=8.8.8.8 --dns=1.1.1.1 --dns=8.8.4.4 --dns=9.9.9.9 --hostname=$SERVER \
    --log-driver local --log-opt max-size=10m --log-opt max-file=10 \
    --publish 8000:8000/tcp --name "$SERVER" $SERVER:$TAG 

sleep 1

sudo docker ps -a

sudo docker top "$SERVER"

docker images

sleep 1

sudo docker exec -it "$SERVER" /bin/bash