# Google Colab Setup Guide (GitHub Version)

이 가이드는 GitHub를 통해 코드를 동기화하고 Google Colab에서 백엔드를 실행하는 방법을 설명합니다.

## 1. GitHub 리포지토리 준비
1. 현재 프로젝트를 GitHub에 올립니다. (Public 혹은 Private)
   - Private 리포지토리라면 Colab에서 접근할 때 [Personal Access Token](https://github.com/settings/tokens)이 필요합니다.

## 2. Google Colab 노트북 설정
1. [Google Colab](https://colab.research.google.com/)에서 새 노트북 생성.
2. **런타임 > 런타임 유형 변경 > T4 GPU** 선택.
3. 아래 코드를 실행합니다.

```python
# 1. GitHub에서 코드 가져오기
import os

# 기존 폴더가 있다면 삭제 (재실행 시 업데이트를 위해)
if os.path.exists('/content/Change-Clothes'):
    !rm -rf /content/Change-Clothes

# 레포지토리 클론 (본인의 GitHub 주소로 변경하세요!)
# Private 레포인 경우: https://<TOKEN>@github.com/username/repo.git 형식 사용
!git clone https://github.com/hyunlord/Change-Clothes.git

# 2. 백엔드 경로로 이동
os.chdir('/content/Change-Clothes/backend')
print(f"Current Directory: {os.getcwd()}")

# 3. 의존성 설치
!pip install -r requirements.txt
!pip install pyngrok uvicorn nest-asyncio

# 4. Ngrok 설정 및 서버 실행
from pyngrok import ngrok
import uvicorn
import nest_asyncio

# Ngrok Authtoken (필수: 끊김 방지)
# !ngrok config add-authtoken <YOUR_TOKEN>

# 기존 터널 정리
ngrok.kill()

# 포트 8000 노출
tunnel = ngrok.connect(8000)
print(f"🚀 Server is running at: {tunnel.public_url}")

# FastAPI 서버 실행
# FastAPI 서버 실행
config = uvicorn.Config("main:app", host="0.0.0.0", port=8000)
server = uvicorn.Server(config)
await server.serve()
```

## 3. 코드 업데이트 시
로컬에서 코드를 수정하고 GitHub에 Push한 뒤, Colab에서 위 셀을 다시 실행하면 최신 코드가 반영됩니다.


## 3. 프론트엔드 연결
1. Colab 실행 결과에 나온 `https://....ngrok-free.app` 주소를 복사합니다.
2. 로컬에서 실행 중인 웹 페이지(`http://localhost:3000`)의 상단 **API URL** 입력창에 붙여넣습니다.
3. 이제 이미지를 업로드하고 Try-On을 테스트합니다!
