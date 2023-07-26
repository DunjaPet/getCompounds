# Use the official Python base image
FROM python:3.8.3

# Set the working directory inside the container
WORKDIR /app

# Copy the application files into the container
COPY requirements.txt /app
COPY GetCompounds.py /app

# Install the application dependencies
RUN pip install -r requirements.txt

# Define the command to run the application
CMD ["python", "GetCompounds.py"]
