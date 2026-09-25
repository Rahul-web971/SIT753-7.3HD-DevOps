FROM python:3.12-slim
WORKDIR /srv
COPY app/ ./app/
RUN useradd --create-home appuser
USER appuser
ENV PORT=8000
ENV HOST=0.0.0.0
EXPOSE 8000
CMD ["python", "-m", "app.server"]
