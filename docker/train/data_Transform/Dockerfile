FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt ./requirements.txt
RUN pip --no-cache-dir install -r /requirements.txt
COPY ./indicators.py /source/indicators.py
COPY app.py /source/app.py
CMD ["python", "/source/app.py"]