# Use the official Python 3.8 image from Docker Hub
# ARG DEBIAN_FRONTEND=noninteractive

FROM python:3.8

# Install system dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common wget unzip curl

# Install Microsoft Edge beta
# RUN apt-get update && apt-get install -y microsoft-edge-beta
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge-dev.list && \
    apt-get update && \
    apt-get install -y microsoft-edge-dev

# Download and install MSEdgeDriver
RUN wget https://msedgedriver.azureedge.net/114.0.1823.18/edgedriver_linux64.zip && \
    unzip edgedriver_linux64.zip && \
    mv msedgedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/msedgedriver

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Run main.py when the container launches
CMD ["python", "main.py"]

