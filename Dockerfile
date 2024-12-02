# Use a specific Python version as the base image
FROM python

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt requirements.txt

# Copy the log file into the container
COPY LogSource.txt /app/LogSource.txt

# Install dependencies
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app will run on
EXPOSE 5000

# Command to run the app
CMD ["python", "main.py"]