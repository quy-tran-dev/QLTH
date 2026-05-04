# Dùng bản Python 3.10 (hoặc bản bạn đang xài) bản slim cho nhẹ
FROM python:3.12-slim

# Bật chế độ không tạo file .pyc và in log thẳng ra terminal
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Tạo thư mục làm việc trong container
WORKDIR /app

# Copy file requirements vào trước và cài đặt thư viện
# (Làm bước này trước để Docker cache lại, lần sau build không bị lâu)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào trong container
COPY . /app/