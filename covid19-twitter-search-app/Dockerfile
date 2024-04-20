FROM python:3.8-alpine

RUN apk update
RUN apk add py-pip
RUN apk add --no-cache python3-dev
#RUN pip install --no-cache-dir pipenv
RUN pip install --upgrade pip

WORKDIR /usr/src/app
#COPY Pipfile Pipfile.lock bootstrap.sh ./
COPY requirements.txt bootstrap.sh ./
COPY searchapp ./searchapp

#RUN pipenv install --system --deploy
RUn pip --no-cache-dir install -r requirements.txt

EXPOSE 5000
ENTRYPOINT ["/usr/src/app/bootstrap.sh"]