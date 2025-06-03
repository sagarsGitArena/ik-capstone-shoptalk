FROM apache/airflow:2.7.2
USER airflow
# Install additional Python packages, including MLFlow
RUN pip install --no-cache-dir \
    mlflow \
    sentence-transformers \
    urllib3==1.26.17
