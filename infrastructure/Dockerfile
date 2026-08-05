FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# --index-url points pip at PyTorch's CPU-only wheel index FIRST (so torch
# resolves to the small CPU build, not the ~2-3GB CUDA build); --extra-index-url
# falls back to normal PyPI for every other package. Doing this in a single
# install call avoids a version mismatch where a later package's resolver
# reaches back to the default CUDA build to satisfy a newer torch requirement.
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    --extra-index-url https://pypi.org/simple \
    -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
