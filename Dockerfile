# Use NVIDIA CUDA base image for CUDA 11.6 and cuDNN 8 on Ubuntu 20.04
FROM nvidia/cuda:11.6.2-cudnn8-devel-ubuntu20.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    MPLBACKEND=Agg \
    PATH="/opt/venv/bin:$PATH"

# Install system dependencies
# - Python 3.9 and pip
# - Git (for setuptools-scm or if model script needs it)
# - wget (if model script needs it)
# - Dependencies for pillow_heif (libheif, libde265)
# - Dependencies for matplotlib (freetype, libpng)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.9 \
    python3.9-venv \
    python3.9-dev \
    python3-pip \
    git \
    wget \
    curl \
    libheif-dev \
    libde265-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python3.9 -m venv /opt/venv

# Upgrade pip in the virtual environment
RUN pip install --upgrade pip

# Set working directory
WORKDIR /app

# Install PyTorch 1.13.1 with CUDA 11.6 support
# This specific version is chosen for CUDA 11.6 compatibility.
RUN pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116

# Copy project configuration and source code
# Copy pyproject.toml first to leverage Docker cache for dependencies
COPY pyproject.toml ./
COPY src ./src
COPY README.md ./
COPY ACKNOWLEDGEMENTS.md ./
COPY LICENSE ./
COPY get_pretrained_models.sh ./
COPY data ./data

# If you have an api.py for your FastAPI application, copy it here
# COPY api.py ./

# Install the project and its dependencies from pyproject.toml
# This will install the 'depth_pro' package and dependencies like timm, numpy<2, pillow_heif, matplotlib.
# It should respect the already installed torch/torchvision versions.
RUN pip install .

# Install dependencies for the FastAPI server (if not covered by pyproject.toml)
RUN pip install fastapi uvicorn[standard]

# Download pretrained models
RUN chmod +x get_pretrained_models.sh && \
    ./get_pretrained_models.sh

# Expose the port the API will run on
EXPOSE 8000

# Default command to run the Uvicorn server
# Ensure you have an 'api.py' file with a FastAPI 'app' instance at the root of /app,
# or change "api:app" to the correct path (e.g., "depth_pro.api:app").
# CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]