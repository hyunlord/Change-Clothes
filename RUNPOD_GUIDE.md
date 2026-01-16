# RunPod 실행 가이드

RunPod GPU 클라우드에서 Change-Clothes 프로젝트를 실행하는 방법입니다.

## 사전 준비

- [RunPod](https://runpod.io) 계정
- GPU Pod 생성 (RTX 4090 / A4000 등, VRAM 16GB+ 권장)

---

## 방법 1: Docker Compose로 전체 실행 (권장)

백엔드와 프론트엔드를 모두 RunPod에서 실행합니다.

### 1. Pod 생성

1. RunPod 대시보드 → **Pods** → **+ Deploy**
2. 설정:
   - **Template**: `RunPod Pytorch 2.1` 또는 Docker 지원 템플릿
   - **GPU**: RTX 4090 / A4000 (VRAM 16GB+)
   - **Volume Disk**: 30GB 이상
   - **Expose HTTP Ports**: `3000, 8000` 추가

### 2. Pod 접속 및 Docker 설치

Pod 시작 후 **Connect** → **Web Terminal** 또는 **SSH**로 접속:

```bash
# Docker 설치 확인
docker --version

# Docker가 없으면 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose 설치
pip install docker-compose

# 또는 Docker Compose V2 플러그인 설치
mkdir -p ~/.docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose
```

### 3. 프로젝트 클론 및 실행

```bash
# 프로젝트 클론
cd /workspace
git clone https://github.com/hyunlord/Change-Clothes.git
cd Change-Clothes

# Docker Compose 실행 (V1)
docker-compose up --build

# 또는 Docker Compose V2
docker compose up --build
```

### 4. 접속

RunPod 대시보드에서 **Connect** 버튼 클릭:

| 서비스 | 포트 | URL 형식 |
|--------|------|----------|
| 프론트엔드 | 3000 | `https://{POD_ID}-3000.proxy.runpod.net` |
| 백엔드 API | 8000 | `https://{POD_ID}-8000.proxy.runpod.net` |

**프론트엔드 URL (포트 3000)** 로 접속하면 바로 사용할 수 있습니다!

### 5. API URL 설정

프론트엔드 페이지 상단의 **API URL** 입력창에 백엔드 URL 입력:
```
https://{POD_ID}-8000.proxy.runpod.net
```

---

## 방법 2: 백엔드만 RunPod + 로컬 프론트엔드

RunPod에서 백엔드(GPU)만 실행하고, 프론트엔드는 로컬에서 실행합니다.

### RunPod (백엔드)

```bash
cd /workspace
git clone https://github.com/hyunlord/Change-Clothes.git
cd Change-Clothes/backend

# Docker로 백엔드만 실행
docker build -t change-clothes-backend .
docker run --gpus all -p 8000:8000 change-clothes-backend
```

또는 Docker 없이:
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 로컬 (프론트엔드)

```bash
# 로컬 PC에서
cd frontend
npm install
npm run dev
```

`http://localhost:3000` 접속 후, API URL에 RunPod 백엔드 URL 입력:
```
https://{POD_ID}-8000.proxy.runpod.net
```

---

## 백그라운드 실행 (Pod 종료 방지)

터미널을 닫아도 서버가 계속 실행되도록 설정:

```bash
# Screen 사용
screen -S server
docker-compose up --build
# Ctrl+A, D 로 분리 (서버는 계속 실행)

# 다시 접속하려면
screen -r server
```

또는:
```bash
# 백그라운드로 실행
nohup docker-compose up --build > server.log 2>&1 &

# 로그 확인
tail -f server.log
```

---

## 환경 변수 설정 (선택)

`docker-compose.yml`에서 프론트엔드 API URL을 미리 설정할 수 있습니다:

```yaml
frontend:
  environment:
    - NEXT_PUBLIC_API_URL=https://{POD_ID}-8000.proxy.runpod.net
```

---

## 문제 해결

### Docker/Docker Compose가 없는 경우

```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose 설치 (방법 1: pip)
pip install docker-compose

# Docker Compose 설치 (방법 2: 바이너리)
mkdir -p ~/.docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose

# 설치 확인
docker --version
docker-compose --version  # 또는 docker compose version
```

### 포트가 노출되지 않는 경우

1. RunPod 대시보드 → Pod 설정 → **Edit Pod**
2. **Expose HTTP Ports**에 `3000, 8000` 추가
3. Pod 재시작

### GPU 인식 안 됨

```bash
# GPU 확인
nvidia-smi

# Docker에서 GPU 사용 확인
docker run --gpus all nvidia/cuda:11.8-base-ubuntu22.04 nvidia-smi
```

### 모델 다운로드 시간

처음 실행 시 세그멘테이션 모델 다운로드에 1~2분 소요됩니다.
로그에 `Segmentation Processor Ready`가 표시될 때까지 기다려주세요.

---

## 권장 사양

| 항목 | 최소 | 권장 |
|------|------|------|
| GPU | RTX 3090 (24GB) | RTX 4090 (24GB) |
| Volume | 20GB | 30GB+ |
| RAM | 16GB | 32GB |

---

## 비용 절약 팁

- **Spot 인스턴스** 사용 (최대 80% 저렴)
- 사용하지 않을 때 **Stop Pod** (볼륨은 유지)
- 테스트 완료 후 **Terminate** (볼륨 삭제됨, 비용 0)

---

## API 테스트 방법

서버가 실행된 후, 테스트 스크립트를 사용하여 API를 테스트할 수 있습니다.

### 테스트 가능한 기능

| 기능 | API | 비교 옵션 |
|------|-----|-----------|
| 이미지 분석 | `/analyze` | `b2` vs `b5` vs `sam` |
| 가상 피팅 | `/try-on/image` | `sam3` vs `schp` |

### 세그멘테이션 모델 비교

| 모델 | 옵션 | 특징 |
|------|------|------|
| Segformer B2 | `b2` | 빠른 속도 |
| Segformer B5 | `b5` | 높은 품질 |
| Segment Anything | `sam` | 모든 영역 감지 |

### 테스트 실행 방법

#### 1. 새 터미널에서 테스트 (RunPod 내부)

Docker가 실행 중인 상태에서 새 터미널을 열고:

```bash
cd /workspace/Change-Clothes/tests
pip install -r requirements.txt

# 서버 상태 확인
python test_api.py --check-only

# 이미지 분석 테스트 (테스트 이미지 필요)
python test_api.py --image /path/to/person.jpg

# 모델 벤치마크
python benchmark_models.py --image /path/to/person.jpg
```

#### 2. 로컬 PC에서 테스트 (RunPod 서버 대상)

로컬 PC에서 RunPod 서버를 대상으로 테스트:

```bash
cd tests
pip install -r requirements.txt

# RunPod URL로 테스트
python test_api.py --url https://{POD_ID}-8000.proxy.runpod.net --image ./person.jpg

# 벤치마크
python benchmark_models.py --url https://{POD_ID}-8000.proxy.runpod.net --image ./person.jpg
```

#### 3. cURL로 간단 테스트

```bash
# 서버 상태 확인
curl https://{POD_ID}-8000.proxy.runpod.net/

# 이미지 분석 (B5 모델)
curl -X POST https://{POD_ID}-8000.proxy.runpod.net/analyze \
  -F "person_image=@./person.jpg" \
  -F "model_type=b5"
```

### 테스트 출력 예시

```
============================================================
 세그멘테이션 모델 벤치마크
============================================================
모델     시간(초)    신체   의류   상태
------------------------------------------------------------
b2       2.15       4      2      OK
b5       3.42       5      3      OK
sam      5.18       8      0      OK
------------------------------------------------------------
 가장 빠른 모델: B2 (2.15s)
 가장 상세한 모델: SAM (총 8개 영역)
============================================================
```

### 테스트 이미지 준비

테스트용 이미지는 직접 준비해야 합니다.

권장 사양:
- 해상도: 512x768 이상
- 포맷: JPG, PNG
- 조건: 전신, 정면, 단일 인물
