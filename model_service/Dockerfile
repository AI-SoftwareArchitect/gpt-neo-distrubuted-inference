FROM python:3.12-slim

WORKDIR /app

COPY main.py ./
COPY ./gpt_neo_125m_finetuned ./gpt_neo_125m_finetuned

RUN pip install --no-cache-dir fastapi uvicorn torch transformers

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
