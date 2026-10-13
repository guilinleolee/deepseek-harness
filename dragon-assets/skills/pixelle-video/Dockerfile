# Pixelle-Video ComfyUI Docker
# GPU-enabled ComfyUI for Pixelle-Video workflows

FROM nvidia/cuda:12.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    git \
    wget \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install ComfyUI
WORKDIR /workspace
RUN git clone https://github.com/comfyanonymous/ComfyUI.git && \
    cd ComfyUI && \
    pip3 install -r requirements.txt

# Install Pixelle-Video dependencies
RUN pip3 install \
    opencv-python \
    Pillow \
    numpy \
    torch \
    torchvision \
    transformers \
    accelerate

# Download models (WAN 2.1, ChatTTS, VAE)
RUN mkdir -p /workspace/ComfyUI/models/{checkpoints,vae,clip,loras}
RUN mkdir -p /workspace/ComfyUI/models/audio
RUN mkdir -p /workspace/ComfyUI/models/motion

# Environment
ENV COMFYUI_PORT=8188
ENV PIXELLE_WORKFLOWS=/workspace/pixelle-workflows

# Copy workflows
COPY workflows /workspace/pixelle-workflows

# Expose port
EXPOSE 8188

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8188/api/system_stats || exit 1

# Start ComfyUI
CMD ["python3", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
