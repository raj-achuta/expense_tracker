# Use the official Python image as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /code

# Copy the poetry.lock and pyproject.toml files
COPY poetry.lock pyproject.toml ./

# Install Poetry
RUN pip install poetry

# Install project dependencies
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code
COPY . .

# Start the Uvicorn server
CMD ["poetry", "run", "start"]
