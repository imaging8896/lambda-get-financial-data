FROM python:3.13.1-slim AS base
FROM base AS builder

COPY requirements.txt /requirements.txt
RUN pip install --target /.local -r /requirements.txt

FROM base

WORKDIR /wd

COPY --from=builder /.local /wd
COPY news /wd/data
COPY main.py /wd/main.py

RUN pip install --target /wd awslambdaric
ENTRYPOINT [ "python", "-m", "awslambdaric" ]
CMD [ "main.handler" ]
