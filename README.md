# Real-time Virtual Try-On Service

## Prerequisites
- Node.js 18+
- Python 3.10+
- NVIDIA GPU (Recommended for inference)

## Setup

### Option 1: Docker (Recommended)
Ensure you have Docker and NVIDIA Container Toolkit installed.
```bash
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

### Option 2: Manual Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend runs on http://localhost:8000

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on http://localhost:3000

## API Endpoints
- `POST /try-on/image`: Upload person and garment images.