sudo docker build -t cco-insights-api .
 docker run --detach -p 8000\
     --env VIRTUAL_HOST=insight.creditcardoffers.lk \
     cco-insights-api
