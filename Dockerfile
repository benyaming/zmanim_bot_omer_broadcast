FROM python:3.11-slim

ENV TZ=Asia/Hebron
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install poetry
WORKDIR /home/app
COPY . .
WORKDIR /home/app/broadcast
RUN poetry update
ENV PYTHONPATH=/home/app
CMD ["poetry", "run", "python", "main.py"]
