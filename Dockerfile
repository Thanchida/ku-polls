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

EXPOSE 8000
CMD [ "./entrypoint.sh" ]