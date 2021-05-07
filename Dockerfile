FROM python:3.8.5-alpine3.12
ENV PYTHONPATH="/kubecepops:$PYTHONPATH"
RUN mkdir /kubecepops
COPY . /kubecepops
WORKDIR /kubecepops
EXPOSE 80
