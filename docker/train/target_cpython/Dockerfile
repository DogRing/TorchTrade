FROM gcc:latest
WORKDIR /app
COPY target.c .
RUN gcc -shared -o libtarget.so -fPIC target.c

FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /source
COPY --from=0 /app/libtarget.so .
COPY requirements.txt .
RUN pip --no-cache-dir install -r ./requirements.txt
COPY app.py .
CMD ["python","app.py"]