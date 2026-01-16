# 테스트 가이드

Change-Clothes API 테스트 스크립트입니다.

## 테스트 가능한 기능

### 1. 이미지 분석 (`/analyze`)

사람 이미지를 업로드하면 신체 부위와 의류를 분리합니다.

| 모델 | 옵션값 | 특징 |
|------|--------|------|
| Segformer B2 | `b2` | 빠른 속도 |
| Segformer B5 | `b5` | 높은 품질 |
| Segment Anything | `sam` | 모든 영역 감지 |

### 2. 가상 피팅 (`/try-on/image`)

사람 이미지 + 의류 이미지로 가상 피팅 결과를 생성합니다.

| 파라미터 | 옵션 |
|----------|------|
| category | `upper_body`, `lower_body`, `dresses` |
| segmentation_model | `sam3`, `schp` |

---

## 설치

```bash
cd tests
pip install -r requirements.txt
```

---

## 사용법

### 서버 상태 확인

```bash
# 로컬 서버
python test_api.py --check-only

# RunPod 서버
python test_api.py --url https://{POD_ID}-8000.proxy.runpod.net --check-only
```

### 이미지 분석 테스트

```bash
# 모든 모델 테스트 (b2, b5, sam)
python test_api.py --image ./person.jpg

# 특정 모델만 테스트
python test_api.py --image ./person.jpg --model b5

# RunPod 서버로 테스트
python test_api.py --url https://{POD_ID}-8000.proxy.runpod.net --image ./person.jpg
```

### 모델 벤치마크

```bash
# 기본 벤치마크 (1회)
python benchmark_models.py --image ./person.jpg

# 정확한 측정 (3회 평균)
python benchmark_models.py --image ./person.jpg --runs 3

# RunPod에서 벤치마크
python benchmark_models.py --url https://{POD_ID}-8000.proxy.runpod.net --image ./person.jpg
```

---

## 출력 예시

### test_api.py

```
==================================================
Change-Clothes API 테스트
==================================================
API URL: http://localhost:8000
테스트 이미지: ./person.jpg
==================================================
[OK] 서버 상태: online
     메시지: Virtual Try-On API is running

[TEST] /analyze API (model: b2)
       이미지: ./person.jpg
[OK] 분석 완료!
     - 신체 부위: 4개
     - 의류 아이템: 2개
     - 신체 라벨: face, hair, left-arm, right-arm
     - 의류 라벨: Upper-clothes, Pants
```

### benchmark_models.py

```
============================================================
 세그멘테이션 모델 벤치마크
============================================================
 API URL: http://localhost:8000
 이미지: ./person.jpg
 반복 횟수: 1
============================================================

[B2] 벤치마크 실행 중...
  평균 시간: 2.15s

[B5] 벤치마크 실행 중...
  평균 시간: 3.42s

[SAM] 벤치마크 실행 중...
  평균 시간: 5.18s

============================================================
 벤치마크 결과
============================================================
모델     시간(초)    신체   의류   상태
------------------------------------------------------------
b2       2.15       4      2      OK
b5       3.42       5      3      OK
sam      5.18       8      0      OK
------------------------------------------------------------

============================================================
 분석
============================================================
 가장 빠른 모델: B2 (2.15s)
 가장 상세한 모델: SAM (총 8개 영역)
============================================================
```

---

## 테스트 이미지 준비

테스트를 위해 전신이 보이는 사람 이미지를 준비하세요.

권장 사양:
- 해상도: 512x768 이상
- 포맷: JPG, PNG
- 조건: 전신, 정면, 단일 인물
