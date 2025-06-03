FROM nvidia/cuda:12.6.3-cudnn-devel-ubuntu22.04
# Install dependencies
RUN apt-get update && apt-get install -y \
    net-tools \
    libopenblas-dev \
    libomp-dev \
    python3-pip \
    python3-dev && \
    pip3 install --no-cache-dir faiss-gpu flask \
    sentence-transformers 
    


# Install specific versions of NumPy and FAISS
RUN pip install --no-cache-dir -U \
                pandas \
                "numpy<2" \
                faiss-gpu \
                flask \
                "cupy-cuda12x" \
                boto3 \
                transformers \
                torch \
                langchain \                
                langchain-community \
                langchain-openai \
                openai \
                gradio \
                pillow \
                mlflow rouge-score sacrebleu scikit-learn
#                streamlit 




# Copy application files
WORKDIR /app
COPY . /app

# Expose UI service
EXPOSE 7860

# Run the UI Layer Service
CMD ["python3", "-u", "app.py"]
