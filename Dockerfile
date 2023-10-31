FROM python:3.9.17-bullseye
WORKDIR /app

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Get dependencies
COPY . /app
RUN pip install -r /app/requirements.txt

# Run
CMD ["python3", "-u", "/app/main.py"]