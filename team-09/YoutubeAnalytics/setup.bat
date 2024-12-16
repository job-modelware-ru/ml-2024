docker-compose -f docker-compose-ci.yaml up -d --build
docker cp dump.tar.gz mongo_db:.
docker exec mongo_db tar -xzf dump.tar.gz
docker exec mongo_db mongorestore dump