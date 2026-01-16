# RunPod 실행 가이드

RunPod에서 Change-Clothes를 실행하는 방법입니다.

---

## 빠른 시작 (복사해서 붙여넣기)

### 1단계: 백엔드 실행

RunPod 터미널에서 아래 명령어를 **Ctrl+Shift+V**로 붙여넣기:

```bash
cd /workspace && git clone https://github.com/hyunlord/Change-Clothes.git && cd Change-Clothes/backend && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2단계: 접속

RunPod 대시보드 → **Connect** → **Connect to HTTP Service [Port 8000]** 클릭

끝!

---

## 상세 설명

### 1. Pod 생성

1. [RunPod](https://runpod.io) 접속
2. **Pods** → **+ Deploy** 클릭
3. 설정:
   - **Template**: `RunPod Pytorch 2.1`
   - **GPU**: RTX 4090 또는 RTX 3090 (VRAM 24GB)
   - **Volume Disk**: 20GB 이상
   - **Expose HTTP Ports**: `8000` 입력

### 2. 터미널 접속

Pod 시작 후 **Connect** → **Start Web Terminal** 클릭

### 3. 백엔드 설치 및 실행

```bash
# 1. 프로젝트 다운로드
cd /workspace
git clone https://github.com/hyunlord/Change-Clothes.git

# 2. 백엔드 폴더로 이동
cd Change-Clothes/backend

# 3. 필요한 라이브러리 설치 (2~3분 소요)
pip install -r requirements.txt

# 4. 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000
```

서버가 시작되면 아래와 같은 메시지가 나옵니다:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. API 접속

RunPod 대시보드에서:
1. **Connect** 버튼 클릭
2. **Connect to HTTP Service [Port 8000]** 클릭

브라우저에서 새 탭이 열리고 API에 접속됩니다.

URL 형식: `https://{POD_ID}-8000.proxy.runpod.net`

---

## 프론트엔드도 실행하고 싶다면

### 방법 A: 새 터미널에서 실행 (RunPod 내부)

1. RunPod 터미널에서 **새 탭** 열기
2. 아래 명령어 실행:

```bash
# Node.js 설치
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# 프론트엔드 실행
cd /workspace/Change-Clothes/frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```

3. RunPod 대시보드 → **Connect** → **Connect to HTTP Service [Port 3000]**

### 방법 B: 로컬 PC에서 프론트엔드 실행

로컬 PC에서:
```bash
git clone https://github.com/hyunlord/Change-Clothes.git
cd Change-Clothes/frontend
npm install
npm run dev
```

`http://localhost:3000` 접속 후 **API URL**에 RunPod URL 입력:
```
https://{POD_ID}-8000.proxy.runpod.net
```

---

## API 테스트

### 서버 상태 확인

새 터미널에서:
```bash
cd /workspace/Change-Clothes/tests
pip install -r requirements.txt
python test_api.py --check-only
```

### 이미지 분석 테스트

```bash
# 테스트 이미지로 분석 (이미지 파일 필요)
python test_api.py --image /path/to/person.jpg

# 모델 비교 벤치마크
python benchmark_models.py --image /path/to/person.jpg
```

### cURL로 테스트

```bash
# 서버 상태 확인
curl http://localhost:8000/

# 이미지 분석 (b2 모델)
curl -X POST http://localhost:8000/analyze \
  -F "person_image=@/path/to/person.jpg" \
  -F "model_type=b2"
```

---

## 테스트 가능한 기능

| 기능 | API | 모델 옵션 |
|------|-----|-----------|
| 이미지 분석 | `/analyze` | `b2`, `b5`, `sam` |
| 가상 피팅 | `/try-on/image` | `sam3`, `schp` |

### 세그멘테이션 모델 비교

| 모델 | 옵션 | 속도 | 품질 |
|------|------|------|------|
| Segformer B2 | `b2` | 빠름 | 보통 |
| Segformer B5 | `b5` | 보통 | 높음 |
| SAM | `sam` | 느림 | 매우 높음 |

---

## 백그라운드 실행

터미널을 닫아도 서버가 계속 실행되게 하려면:

```bash
# Screen 사용
screen -S server
uvicorn main:app --host 0.0.0.0 --port 8000
# Ctrl+A, D 로 분리

# 다시 접속
screen -r server
```

또는:
```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
tail -f server.log
```

---

## 문제 해결

### "Port 8000 not exposed" 오류

1. RunPod 대시보드 → Pod 클릭 → **Edit Pod**
2. **Expose HTTP Ports**에 `8000` 추가
3. **Save** 후 Pod 재시작

### 모델 다운로드가 오래 걸림

처음 실행 시 AI 모델 다운로드에 1~2분 소요됩니다.
`Segmentation Processor Ready` 메시지가 나올 때까지 기다리세요.

### GPU 확인

```bash
nvidia-smi
```

---

## 권장 GPU

| GPU | 가격 (시간당) | 추천도 |
|-----|---------------|--------|
| RTX 4090 | ~$0.44 | ⭐⭐⭐⭐⭐ |
| RTX 3090 | ~$0.22 | ⭐⭐⭐⭐ |
| A4000 | ~$0.16 | ⭐⭐⭐ |

**팁**: Spot 인스턴스 사용 시 50~80% 저렴!
