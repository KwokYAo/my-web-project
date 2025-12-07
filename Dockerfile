FROM mybase
#Change our working directory to app folder
WORKDIR /app-docker
COPY requirements.txt requirements.txt
#Install all the packages needed to run our web app
RUN pip3 install -r requirements.txt
# Add every files and folder into the app folder
COPY . .
# Expose port 5000 for http communication
EXPOSE 5000
# Run gunicorn web server and binds it to the port
CMD python3 -m flask run --host=0.0.0.0