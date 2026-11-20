FROM python:3.12-slim
RUN pip install --no-cache-dir "fastmcp>=2.0"
WORKDIR /app
COPY server.py /app/server.py
ENV MCP_TRANSPORT=stdio
ENTRYPOINT ["python", "/app/server.py"]
