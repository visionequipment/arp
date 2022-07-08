FROM python:3.9
ADD simple_track_gen.py .
ADD ./entities ./entities
ENV PYTHONUNBUFFERED=1
RUN pip install requests flask
CMD ["python", "./simple_track_gen.py"]