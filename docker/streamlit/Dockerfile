FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir streamlit==1.32.0 requests==2.31.0 pandas==2.2.0
COPY src/ui/streamlit_app.py ./app.py
EXPOSE 8501
ENV STREAMLIT_SERVER_HEADLESS=true
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
