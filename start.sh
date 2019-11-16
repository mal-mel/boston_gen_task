pip install -r req.txt
docker run -d -e MYSQL_ROOT_PASSWORD=admin --restart unless-stopped -p 3305:3306 --name=mysql mysql
# shellcheck disable=SC2046
python3 $(pwd)/application/main.py