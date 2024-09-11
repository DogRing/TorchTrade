FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt ./requirements.txt
RUN pip install -r /requirements.txt
COPY bitsocket.py /source/bitsocket.py
COPY app.py /source/app.py
COPY candle.py /source/candle.py
CMD ["python", "/source/app.py"]