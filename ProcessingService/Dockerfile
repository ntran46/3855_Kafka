FROM ubuntu:18.04
LABEL maintainer="utran2@dxc.com"
RUN apt-get update -y && apt-get install -y python3 python3-pip
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
COPY . /app
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
