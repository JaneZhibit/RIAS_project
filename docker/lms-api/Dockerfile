FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic
COPY src/lms_api /app/lms_api
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "lms_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
