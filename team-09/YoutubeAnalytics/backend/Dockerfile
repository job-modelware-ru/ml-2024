FROM python:3.9-slim-buster
COPY . .
WORKDIR /backend
RUN python3 -m pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0"]