REVERSE_STRING_API_ENDPOINT='http://vector-db-service:8000/reverse'
FAISS_VECTOR_DB_SEARCH_ENDPOINT='http://vector-db-service:8000/faiss-search'
CREATE_INDEX_API_ENDPOINT='http://vector-db-service:8000/create_index'



from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from transformers import pipeline

