FROM pytorch/pytorch:2.4.1-cuda11.8-cudnn9-runtime
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt /requirements.txt
RUN pip --no-cache-dir install -r /requirements.txt
COPY app.py /source/app.py
CMD ["python", "/source/app.py"]