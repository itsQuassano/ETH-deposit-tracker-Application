cd ETH Deposit Tracker Application\python-image
docker build -t 1ethapp .
docker run --name 1ethapp --env-file .env -d 1ethapp