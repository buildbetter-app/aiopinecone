#!/bin/zsh

datamodel-codegen --input public/openapi.yaml --input-file-type openapi --openapi-scopes schemas --reuse-model --keep-model-order --target-python-version 3.10 --use-double-quotes --output aiopinecone/schemas/generated.py
