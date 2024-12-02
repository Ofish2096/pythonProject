cd C:\Users\oferk\PycharmProjects\DbServiceApi\pythonProject
docker build -t my-python-microservice .

docker run -d -p 5000:5000 --network my_network my-python-microservice
