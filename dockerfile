FROM python:3.12-slim
WORKDIR /treinos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x ./uvicorn.sh
ENV PYTHONPATH=/treinos/app
CMD ["./uvicorn.sh"]
