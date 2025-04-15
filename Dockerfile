# Use an official Python runtime as a parent image
FROM python:3.12-slim

RUN apt-get update
RUN apt-get -y install \
    tesseract-ocr \
    tesseract-ocr-ind \
    libgl1-mesa-dev;
RUN apt-get clean

RUN pip install --upgrade pip; \
    pip install \
    pillow \
    pytesseract
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI will run on
EXPOSE 4000

# Expose the debug port for debugpy
EXPOSE 5678

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4000", "--reload"]

