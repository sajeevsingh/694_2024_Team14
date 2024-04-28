# Final Project - Search Application

### Build and run the stack
You can run the application stack (Flask application and Redis) with Docker, respectively `docker-compose`. 
```docker
docker-compose up -d --build
```

### Inorder to build searchapp separately
```
docker build -t searchapp .
```

### run a new docker container named searchapp
```
docker run --name searchapp \
    -d -p 5000:5000 \
    searchapp
```

### In order to shut-down with docker-compose
```
docker-compose down
```

### Test the application (API)
We can use `curl` to make requests to our API. There is one endpoint `/api/v1/tweets/keyword`, so let's test that out.

```
curl http://localhost:5000/api/v1/tweets/keyword?tweet_text=`corona patient`&lang=en
curl http://localhost:5000/api/v1/tweets/keyword?tweet_text=`covid-19`&lang=en
curl http://localhost:5000/api/v1/tweets/keyword?tweet_text=`Corona virus`&lang=en
```
