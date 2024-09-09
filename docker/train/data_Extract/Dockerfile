FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt ./requirements.txt
RUN pip install -r /requirements.txt
COPY app.py /source/app.py
CMD ["python", "/source/app.py"]