FROM python:3.6.9
WORKDIR /image_metadata_app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD python new_server.py 
