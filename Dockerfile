FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirement list and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files (including archipelago.py, office_quotes.py, throw.py, etc.)
COPY . .

# Run the bot script
CMD ["python", "HouseKeeperBot.py"]
