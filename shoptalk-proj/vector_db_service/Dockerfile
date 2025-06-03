FROM nvidia/cuda:12.6.3-cudnn-devel-ubuntu22.04
# Install dependencies
RUN apt-get update && apt-get install -y \
    libopenblas-dev \
    libomp-dev \
    python3-pip \
    python3-dev && \
    pip3 install --no-cache-dir faiss-gpu flask \
    sentence-transformers
     

# RUN pip install --no-cache-dir numpy faiss-gpu flask


# # Install Python and system dependencies
# RUN apt-get update && apt-get install -y \
#     python3.9 python3.9-distutils wget curl && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# Install pip
#RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9

# Install specific versions of NumPy and FAISS
RUN pip install --no-cache-dir \
                pandas \
                "numpy<2" \
                faiss-gpu \
                flask \
                "cupy-cuda12x" \
                boto3 \
                mlflow rouge-score sacrebleu scikit-learn


# Copy application files
WORKDIR /app
COPY . /app

# Expose FAISS service
EXPOSE 8000

# Run the FAISS server
CMD ["python3", "-u", "app.py"]



# # Install Python and system dependencies
# RUN apt-get update && apt-get install -y \
#     python3.9 python3.9-distutils wget curl && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# # Install pip
# RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9

# # Install Python libraries, including FAISS and numpy
# RUN pip install --no-cache-dir numpy faiss-gpu flask

# # Set work directory
# WORKDIR /app

# # Copy application files
# COPY app.py .

# # Expose the FAISS service
# EXPOSE 8000

# # Run the FAISS server
# CMD ["python3", "app.py"]