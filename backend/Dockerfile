# بەکارهێنانی ئیمەیجی ئامادەکراوی پایتۆن
FROM python:3.11-slim

# دیاریکردنی فۆڵدەری کارکردن لەناو کانتێنەرەکەدا
WORKDIR /app

# کۆپیکردنی requirements.txt بۆ ناو کانتێنەرەکە
COPY requirements.txt .

# دابەزاندنی لایبرەرییەکان (LangChain, LangGraph, FastAPI, ...)
RUN pip install --no-cache-dir -r requirements.txt

# کۆپیکردنی تەواوی کودی باکئەندەکە
COPY . .

# کارپێکردنی سێرڤەری FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]