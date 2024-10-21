FROM pytorch/pytorch:2.4.1-cuda11.8-cudnn9-runtime
ENV PYTHONUNBUFFERED=1
WORKDIR /source
COPY ./requirements.txt .
RUN pip --no-cache-dir install -r ./requirements.txt
ENV OMP_NUM_THREADS=2
ENV MKL_NUM_THREADS=2
COPY rl_model.py .
COPY trade_env.py .
COPY app.py .
CMD ["python", "./app.py"]