FROM python:3.9-slim

RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential \
        python3.10 \
        python3-pip && \
        apt clean && rm -rf /var/lib/apt/lists/*

RUN pip3 --no-cache-dir install torch \
--index-url https://download.pytorch.org/whl/cpu

ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt /requirements.txt
RUN pip --no-cache-dir install -r /requirements.txt
COPY app.py /source/app.py
CMD ["python", "/source/app.py"]