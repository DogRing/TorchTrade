#!/bin/bash
IFS="|" read -ra FOLDERS <<< "$MODEL_FOLDERS"
IFS="|" read -ra NAMES <<< "$MODEL_NAMES"
IFS="|" read -ra VERSIONS <<< "$MODEL_VERSIONS"
IFS="|" read -ra PARAMS <<< "$PARAM_FILES"

for i in "${!FOLDERS[@]}"; do
  FOLDER="${FOLDERS[i]}"
  MODEL_FILE="${FOLDER}/Model.py"
  EXTRA_FILES=$(find "${FOLDER}" -maxdepth 1 -type f ! -name "Model.py" | tr '\n' ',' | sed 's/,$//')
  torch-model-archiver --model-name "${NAMES[i]}" \
                       --version "${VERSIONS[i]}" \
                       --model-file "${MODEL_FILE}" \
                       --serialized-file "${PARAMS[i]}" \
                       --handler app.py \
                       --extra-files "${EXTRA_FILES}" \
                       --export-path model-store
done

torchserve --start --ts-config $TS_CONFIG_FILE --models all
