FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1
COPY requirements.txt ./requirements.txt
RUN pip --no-cache-dir install -r /requirements.txt
WORKDIR /source
COPY indicators.py /source/indicators.py
COPY app.py /source/app.py
COPY data_transform.py /source/data_transform.py
CMD ["python", "/source/app.py"]