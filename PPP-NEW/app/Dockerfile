FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app/backend
ENV PPP_HOST=0.0.0.0
ENV PPP_PORT=8000

COPY backend ./backend
COPY frontend ./frontend

EXPOSE 8000
CMD ["python", "backend/server.py"]
