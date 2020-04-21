FROM python:3.7

ENV TZ=Asia/Hebron
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install pipenv
WORKDIR /home/app
COPY . .
WORKDIR /home/app/broadcast
RUN pipenv install
ENV PYTHONPATH=/home/app
CMD ["pipenv", "run", "python", "main.py"]
