docker build -t sun-monitor-gateway .

docker run -d --env-file .env --restart always sun-monitor-gateway
