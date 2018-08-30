#!/bin/bash

docker ps -q | xargs docker stop
docker ps -q --filter "status=exited" | xargs docker rm
docker images -q | xargs docker rmi -f

