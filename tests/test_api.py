#!/usr/bin/env python3
"""
Change-Clothes API 테스트 스크립트

사용법:
    python test_api.py                     # 기본 테스트 (localhost:8000)
    python test_api.py --url http://...    # 커스텀 URL
    python test_api.py --image ./test.jpg  # 커스텀 이미지
"""

import argparse
import requests
import sys
import os
from pathlib import Path


def check_server(api_url: str) -> bool:
    """서버 상태 확인"""
    try:
        response = requests.get(f"{api_url}/", timeout=10)
        data = response.json()
        print(f"[OK] 서버 상태: {data.get('status', 'unknown')}")
        print(f"     메시지: {data.get('message', '')}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] 서버에 연결할 수 없습니다: {api_url}")
        return False
    except Exception as e:
        print(f"[ERROR] 서버 확인 실패: {e}")
        return False


def analyze_image(api_url: str, image_path: str, model_type: str) -> dict:
    """
    이미지 분석 API 테스트

    Args:
        api_url: API 서버 URL
        image_path: 테스트 이미지 경로
        model_type: "b2", "b5", "sam"

    Returns:
        API 응답 결과
    """
    if not os.path.exists(image_path):
        print(f"[ERROR] 이미지 파일을 찾을 수 없습니다: {image_path}")
        return {}

    print(f"\n[TEST] /analyze API (model: {model_type})")
    print(f"       이미지: {image_path}")

    with open(image_path, "rb") as f:
        files = {"person_image": f}
        data = {"model_type": model_type}

        try:
            response = requests.post(
                f"{api_url}/analyze",
                files=files,
                data=data,
                timeout=120
            )
            result = response.json()

            if result.get("status") == "completed":
                body_count = len(result.get("body_parts", []))
                clothing_count = len(result.get("clothing_items", []))
                print(f"[OK] 분석 완료!")
                print(f"     - 신체 부위: {body_count}개")
                print(f"     - 의류 아이템: {clothing_count}개")

                if result.get("body_parts"):
                    labels = [item["label"] for item in result["body_parts"]]
                    print(f"     - 신체 라벨: {', '.join(labels)}")

                if result.get("clothing_items"):
                    labels = [item["label"] for item in result["clothing_items"]]
                    print(f"     - 의류 라벨: {', '.join(labels)}")
            else:
                print(f"[WARN] 예상치 못한 응답: {result}")

            return result

        except requests.exceptions.Timeout:
            print("[ERROR] 요청 시간 초과 (120초)")
            return {}
        except Exception as e:
            print(f"[ERROR] API 호출 실패: {e}")
            return {}


def try_on_image(api_url: str, person_path: str, garment_path: str,
                 category: str = "upper_body", seg_model: str = "sam3") -> dict:
    """
    가상 피팅 API 테스트

    Args:
        api_url: API 서버 URL
        person_path: 사람 이미지 경로
        garment_path: 의류 이미지 경로
        category: "upper_body", "lower_body", "dresses"
        seg_model: "sam3", "schp"

    Returns:
        API 응답 결과
    """
    for path, name in [(person_path, "사람"), (garment_path, "의류")]:
        if not os.path.exists(path):
            print(f"[ERROR] {name} 이미지를 찾을 수 없습니다: {path}")
            return {}

    print(f"\n[TEST] /try-on/image API")
    print(f"       사람: {person_path}")
    print(f"       의류: {garment_path}")
    print(f"       카테고리: {category}, 세그멘테이션: {seg_model}")

    with open(person_path, "rb") as p, open(garment_path, "rb") as g:
        files = {
            "person_image": p,
            "garment_image": g
        }
        data = {
            "category": category,
            "segmentation_model": seg_model
        }

        try:
            response = requests.post(
                f"{api_url}/try-on/image",
                files=files,
                data=data,
                timeout=180
            )
            result = response.json()

            if result.get("status") == "completed":
                print(f"[OK] 가상 피팅 완료!")
                print(f"     - 결과 이미지: {result.get('result_image', 'N/A')}")
                print(f"     - 마스크 이미지: {result.get('mask_image', 'N/A')}")
            else:
                print(f"[WARN] 예상치 못한 응답: {result}")

            return result

        except requests.exceptions.Timeout:
            print("[ERROR] 요청 시간 초과 (180초)")
            return {}
        except Exception as e:
            print(f"[ERROR] API 호출 실패: {e}")
            return {}


def run_all_tests(api_url: str, image_path: str):
    """모든 모델로 분석 테스트 실행"""
    print("=" * 50)
    print("Change-Clothes API 테스트")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"테스트 이미지: {image_path}")
    print("=" * 50)

    # 1. 서버 상태 확인
    if not check_server(api_url):
        print("\n서버가 실행 중인지 확인해주세요.")
        sys.exit(1)

    # 2. 각 모델로 분석 테스트
    models = ["b2", "b5", "sam"]
    results = {}

    for model in models:
        result = analyze_image(api_url, image_path, model)
        results[model] = result

    # 3. 결과 요약
    print("\n" + "=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)
    print(f"{'모델':<10} {'상태':<12} {'신체':<8} {'의류':<8}")
    print("-" * 50)

    for model, result in results.items():
        status = "OK" if result.get("status") == "completed" else "FAIL"
        body = len(result.get("body_parts", []))
        clothing = len(result.get("clothing_items", []))
        print(f"{model:<10} {status:<12} {body:<8} {clothing:<8}")

    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Change-Clothes API 테스트")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API 서버 URL (기본값: http://localhost:8000)"
    )
    parser.add_argument(
        "--image",
        default=None,
        help="테스트할 이미지 경로"
    )
    parser.add_argument(
        "--model",
        choices=["b2", "b5", "sam", "all"],
        default="all",
        help="테스트할 모델 (기본값: all)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="서버 상태만 확인"
    )

    args = parser.parse_args()

    # 서버 상태만 확인
    if args.check_only:
        success = check_server(args.url)
        sys.exit(0 if success else 1)

    # 이미지 없이 실행 시 안내
    if args.image is None:
        print("=" * 50)
        print("Change-Clothes API 테스트")
        print("=" * 50)

        if check_server(args.url):
            print("\n서버가 정상 작동 중입니다!")
            print("\n이미지 분석 테스트를 실행하려면:")
            print(f"  python test_api.py --image <이미지경로>")
            print(f"\n예시:")
            print(f"  python test_api.py --image ./person.jpg")
            print(f"  python test_api.py --image ./person.jpg --model b5")
            print(f"  python test_api.py --url https://xxx-8000.proxy.runpod.net --image ./person.jpg")
        sys.exit(0)

    # 전체 테스트 또는 단일 모델 테스트
    if args.model == "all":
        run_all_tests(args.url, args.image)
    else:
        check_server(args.url)
        analyze_image(args.url, args.image, args.model)


if __name__ == "__main__":
    main()
