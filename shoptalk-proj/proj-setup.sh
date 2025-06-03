

mkdir -p ./dags
cp -r ./airflow-dag/* ./dags
mkdir -p ./logs ./plugins ./config ./data/raw ./data/rawimages ./mlruns ./downloads ./vector_database/faiss_db
echo -e "AIRFLOW_UID=$(id -u)" > .env

echo -e "AIRFLOW_GID=0" >> .env
echo -e "REGION_NAME=us-east-1" >> .env
echo -e 'AWS_ACCESS_KEY_ID="AKIA5LIHLU6G4CGEIUXM"' >> .env
echo -e 'AWS_SECRET_ACCESS_KEY="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"' >> .env
echo -e 'OPENAI_API_KEY="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"' >>.env