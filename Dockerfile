FROM python:3-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "./flask_target_generator.py", "--host", "0.0.0.0"]