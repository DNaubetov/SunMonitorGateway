docker build -t sun-monitor-gateway .

docker run -d --env-file .env -p 8888:8888 --restart always sun-monitor-gateway
