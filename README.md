# Edge TTS - Công Cụ Tạo Giọng Đọc Tự Nhiên Đa Ngôn Ngữ

> **Ngôn ngữ tài liệu / Documentation Language:** [🇻🇳 Tiếng Việt](#-giới-thiệu-dự-án) | [🇬🇧 English](#-edge-tts---multilingual-natural-voice-generator)

---

## 1. Giới Thiệu Dự Án

**Edge TTS** là ứng dụng web hỗ trợ chuyển đổi văn bản thành giọng nói (Text-to-Speech) sử dụng công nghệ giọng đọc (Neural Voices) của Microsoft Edge.

### 🎯 Mục Đích
> **Dự án này nhằm phục vụ các giáo viên ngoại ngữ có thể tạo file âm thanh một cách tự nhiên cho nhiều loại ngôn ngữ.**

Ứng dụng giúp các thầy cô giáo dễ dàng chuẩn bị học liệu nghe, bài giảng phát âm, hội thoại mẫu và từ vựng cho học sinh chỉ trong vài giây mà không cần thu âm thủ công.

---

## 2. Tính Năng Chính

- **Hỗ trợ đa ngôn ngữ & giọng đọc tự nhiên**: Cung cấp hàng trăm giọng đọc Nam/Nữ tự nhiên ở nhiều quốc gia và vùng lãnh thổ (`en-US`, `en-GB`, `vi-VN`, `ja-JP`, `ko-KR`, `zh-CN`, `fr-FR`, `de-DE`,...).
- **Tùy chỉnh tốc độ đọc linh hoạt**: Hỗ trợ 3 mức tốc độ chuẩn phục vụ luyện nghe (`0.5x` chậm, `1x` chuẩn, `1.5x` nhanh).
- **Tự động dịch nghĩa Tiếng Việt**: Tự động dịch văn bản vừa tạo sang Tiếng Việt để giáo viên và học sinh dễ dàng đối chiếu.
- **Xử lý bất đồng bộ (Background Task)**: Tạo file âm thanh và dịch nghĩa chạy ngầm dưới nền, giúp phản hồi tức thì và không bị lỗi timeout khi tạo các đoạn văn dài (tối đa **5000 ký tự**).
- **Quản lý kho học liệu âm thanh**:
  - Tìm kiếm nhanh theo nội dung văn bản và sắp xếp linh hoạt.
  - Nghe trực tiếp (cột **Listen**) hoặc tải xuống file `.mp3` (cột **Download**).
  - Xóa từng bản ghi hoặc chọn nhiều bản ghi để xóa hàng loạt.

---

## 3. Yêu Cầu Hệ Thống

Trước khi khởi chạy dự án, máy tính cần được cài đặt sẵn:
- **Docker** và **Docker Compose**
  - **Windows / macOS**: Cài đặt [Docker Desktop](https://www.docker.com/products/docker-desktop/) (đã bao gồm cả Docker và Docker Compose).
  - **Linux**: Cài đặt [Docker Engine](https://docs.docker.com/engine/install/) và [Docker Compose Plugin](https://docs.docker.com/compose/install/).

---

## 4. Hướng Dẫn Khởi Chạy (Linux, macOS, Windows)

Dự án đi kèm kịch bản [`start.sh`](./start.sh) tương thích với cả 3 hệ điều hành (**Linux**, **macOS**, **Windows**). Script sẽ tự động kiểm tra Docker / Docker Compose trên máy và khởi chạy cả `backend` lẫn `frontend`.

### 🐧 Linux & 🍎 macOS

Mở Terminal tại thư mục gốc của dự án và chạy:

```bash
chmod +x start.sh
./start.sh
```

### 🪟 Windows

Trên Windows, bạn có thể chạy file `start.sh` thông qua **Git Bash** (đi kèm khi cài Git for Windows) hoặc **WSL (Windows Subsystem for Linux)**:

1. Đảm bảo ứng dụng **Docker Desktop** đang mở và đang chạy.
2. Mở **Git Bash** (hoặc **WSL Terminal**) tại thư mục gốc của dự án và chạy:

```bash
bash start.sh
```

---

## 5. Cổng Dịch Vụ Mặc Định

Sau khi `start.sh` chạy hoàn tất, bạn có thể truy cập ứng dụng tại:

| Dịch vụ | Địa chỉ truy cập | Mô tả |
| :--- | :--- | :--- |
| **Frontend (Giao diện chính)** | http://host.docker.internal:9101 | Trang công cụ tạo và quản lý giọng đọc (`/audio-tools`) |
| **Backend API (Swagger UI)** | http://host.docker.internal:9100/docs | Tài liệu REST API tương tác của Backend |

---

## 6. Cấu Trúc Thư Mục

```text
edge-tts/
├── backend/                # FastAPI + SQLAlchemy (Async SQLite) + edge-tts + googletrans
│   ├── data/               # Thư mục lưu trữ file âm thanh (.mp3) và cơ sở dữ liệu (edge_tts.db)
│   ├── src/                # Mã nguồn Backend (API endpoints, services, models, schemas)
│   ├── Dockerfile          # Dockerfile cho Backend
│   ├── docker-compose.yaml # Cấu hình Docker Compose của Backend (cổng 9100:8000)
│   └── .env.pro            # Biến môi trường Production của Backend
├── frontend/               # React 19 + TypeScript + Vite + Tailwind CSS + Shadcn UI
│   ├── src/                # Mã nguồn giao diện người dùng
│   ├── Dockerfile          # Multi-stage Dockerfile (Node 24 Alpine + Nginx)
│   ├── docker-compose.yaml # Cấu hình Docker Compose của Frontend (cổng 9101:80)
│   └── .env.pro            # Biến môi trường Production của Frontend
├── start.sh                # Script tự động kiểm tra Docker và khởi chạy toàn bộ hệ thống
├── stop.sh                 # Script dừng toàn bộ các container của hệ thống
├── LICENSE                 # Giấy phép mã nguồn mở MIT
└── README.md               # Tài liệu hướng dẫn sử dụng
```

---

## 7. Dừng Hệ Thống

Để dừng toàn bộ các container đang chạy (`frontend` và `backend`), chạy script [`stop.sh`](./stop.sh):

- **Linux / macOS**:
  ```bash
  chmod +x stop.sh
  ./stop.sh
  ```
- **Windows (Git Bash / WSL)**:
  ```bash
  bash stop.sh
  ```

---

## 8. Giấy Phép (License)

Dự án được phân phối dưới giấy phép **MIT License**. Xem chi tiết tại file [`LICENSE`](./LICENSE).

---
---

# 🇬🇧 Edge TTS - Multilingual Natural Voice Generator

---

## 1. Project Overview

**Edge TTS** is a web application for converting text into natural-sounding speech (Text-to-Speech) powered by Microsoft Edge's Neural Voices technology.

### 🎯 Purpose
> **This project is designed to help foreign language teachers generate natural-sounding audio files across multiple languages.**

The application enables teachers to effortlessly prepare listening materials, pronunciation lessons, sample dialogues, and vocabulary audio for students in just seconds without manual recording.

---

## 2. Key Features

- **Multilingual Support & Natural Neural Voices**: Access hundreds of natural Male and Female voices across numerous countries and locales (`en-US`, `en-GB`, `vi-VN`, `ja-JP`, `ko-KR`, `zh-CN`, `fr-FR`, `de-DE`, etc.).
- **Flexible Playback Speed Control**: Supports 3 standard speaking rates tailored for listening practice (`0.5x` slow, `1x` normal, `1.5x` fast).
- **Automatic Vietnamese Translation**: Automatically translates generated text into Vietnamese so teachers and students can easily cross-reference meanings.
- **Asynchronous Background Processing (Background Tasks)**: Audio generation and translation run asynchronously in the background, ensuring instant API responses and preventing gateway timeouts even for long passages (up to **5000 characters**).
- **Audio Library Management**:
  - Fast keyword search by text content and flexible multi-field sorting.
  - Direct in-browser playback (**Listen** column) or `.mp3` file download (**Download** column).
  - Single-item deletion or bulk selection and deletion.

---

## 3. System Requirements

Before starting the project, ensure your machine has the following installed:
- **Docker** and **Docker Compose**
  - **Windows / macOS**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes both Docker Engine and Docker Compose).
  - **Linux**: Install [Docker Engine](https://docs.docker.com/engine/install/) and the [Docker Compose Plugin](https://docs.docker.com/compose/install/).

---

## 4. Quick Start Guide (Linux, macOS, Windows)

The project includes a cross-platform [`start.sh`](./start.sh) script compatible with **Linux**, **macOS**, and **Windows**. It automatically verifies your Docker / Docker Compose installation and launches both `backend` and `frontend` containers.

### 🐧 Linux & 🍎 macOS

Open a Terminal in the project root directory and run:

```bash
chmod +x start.sh
./start.sh
```

### 🪟 Windows

On Windows, you can run `start.sh` using **Git Bash** (included with Git for Windows) or **WSL (Windows Subsystem for Linux)**:

1. Make sure **Docker Desktop** is open and running.
2. Open **Git Bash** (or **WSL Terminal**) in the project root directory and run:

```bash
bash start.sh
```

---

## 5. Default Service Ports

Once `start.sh` finishes starting the containers, you can access the services at:

| Service | URL | Description |
| :--- | :--- | :--- |
| **Frontend (Main UI)** | http://host.docker.internal:9101 | Voice generation and audio management workspace (`/audio-tools`) |
| **Backend API (Swagger UI)** | http://host.docker.internal:9100/docs | Interactive REST API documentation |

---

## 6. Project Structure

```text
edge-tts/
├── backend/                # FastAPI + SQLAlchemy (Async SQLite) + edge-tts + googletrans
│   ├── data/               # Storage directory for generated audio (.mp3) and SQLite DB (edge_tts.db)
│   ├── src/                # Backend source code (API endpoints, services, models, schemas)
│   ├── Dockerfile          # Backend Dockerfile
│   ├── docker-compose.yaml # Backend Docker Compose configuration (port 9100:8000)
│   └── .env.pro            # Backend Production environment variables
├── frontend/               # React 19 + TypeScript + Vite + Tailwind CSS + Shadcn UI
│   ├── src/                # Frontend UI source code
│   ├── Dockerfile          # Multi-stage Dockerfile (Node 24 Alpine + Nginx)
│   ├── docker-compose.yaml # Frontend Docker Compose configuration (port 9101:80)
│   └── .env.pro            # Frontend Production environment variables
├── start.sh                # Automated script to check Docker and start all services
├── stop.sh                 # Script to stop all running project containers
├── LICENSE                 # MIT Open Source License
└── README.md               # Bilingual project documentation (Vietnamese & English)
```

---

## 7. Stopping the System

To stop all running containers (`frontend` and `backend`), run the [`stop.sh`](./stop.sh) script:

- **Linux / macOS**:
  ```bash
  chmod +x stop.sh
  ./stop.sh
  ```
- **Windows (Git Bash / WSL)**:
  ```bash
  bash stop.sh
  ```

---

## 8. License

This project is licensed under the **MIT License**. See the [`LICENSE`](./LICENSE) file for details.


