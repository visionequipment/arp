FROM python:3.9
ADD track_gen.py .
ADD ./entities ./entities
ENV PYTHONUNBUFFERED=1
RUN pip install requests flask numpy loguru
CMD ["python", "./track_gen.py"] 