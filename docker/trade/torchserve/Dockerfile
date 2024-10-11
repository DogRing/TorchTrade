FROM pytorch/torchserve:latest

ENV MODEL_NAME=mymodel
ENV MODEL_VERSION=1.0
ENV EXTRA_FILES=model.json,param.pth

COPY app.py /home/model-server/
WORKDIR /home/model-server

RUN echo '#!/bin/bash\n\
torch-model-archiver --model-name ${MODEL_NAME} \
                     --version ${MODEL_VERSION} \
                     --model-file Model.py \
                     --handler app.py \
                     --extra-files ${EXTRA_FILES} \
                     --export-path model-store\n\
torchserve --start --model-store model-store --models ${MODEL_NAME}=${MODEL_NAME}.mar --disable-token-auth' > /home/model-server/start.sh \
    && chmod +x /home/model-server/start.sh

CMD ["/home/model-server/start.sh"]