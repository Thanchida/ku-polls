FROM python:3-alpine
# An argument needed to be passed
ARG SECRET_KEY
ARG ALLOWED_HOSTS=127.0.0.1,localhost

WORKDIR /app/polls

ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=True
ENV TIMEZONE=UTC
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS:-127.0.0.1,localhost}

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x ./entrypoint.sh

# Running Django functions in here is not good!
# Apply migrations
#RUN python3 ./manage.py migrate

# Apply fixtures
#RUN python3 ./manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json

EXPOSE 8000
# Run application
#CMD [ "python3", "./manage.py", "runserver", "0.0.0.0:8000" ]
#CMD python3 ./manage.py migrate ; python3 ./manage.py runserver 0.0.0.0:8000
CMD [ "./entrypoint.sh" ]