# Use an official Python runtime as a parent image
FROM python:3.12.3

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_ROOT_USER_ACTION=ignore
ENV APP_HOME=/usr/src/app

# Set the working directory
WORKDIR $APP_HOME

# Install GDAL
RUN apt-get update -y
RUN apt-get install binutils libproj-dev gdal-bin -y

# Create a user to run the application
RUN addgroup --system app && adduser --system --group app

# Create the static and media files directories
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles

# Install dependencies
COPY ./apps/api/requirements.txt ./apps/api/requirements.txt
RUN pip install pip --upgrade
RUN pip install -r ./apps/api/requirements.txt

# Copy the project code into the container
COPY ./apps/api/ .

# change the ownership all the files to the app user
# RUN chown -R app:app $APP_HOME

# change to the app user
# USER app

EXPOSE 8000