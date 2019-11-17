# shellcheck disable=SC2046
pip install -r req.txt
docker run -d -v $(pwd)/db/sql_scripts/:/docker-entrypoint-initdb.d/ -e MYSQL_ROOT_PASSWORD=admin \
 -e MYSQL_DATABASE=boston_gen --restart unless-stopped -p 3305:3306 --name=mysql mysql
python3 $(pwd)/application/main.py