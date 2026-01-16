#!/usr/bin/env python3
"""
세그멘테이션 모델 성능 비교 벤치마크

사용법:
    python benchmark_models.py --image ./test.jpg
    python benchmark_models.py --image ./test.jpg --runs 3
    python benchmark_models.py --url https://xxx-8000.proxy.runpod.net --image ./test.jpg
"""

import argparse
import requests
import time
import sys
import os
from statistics import mean, stdev


def benchmark_model(api_url: str, image_path: str, model_type: str, runs: int = 1) -> dict:
    """
    단일 모델 벤치마크

    Returns:
        {
            "model": str,
            "times": list[float],
            "avg_time": float,
            "std_time": float,
            "body_parts": int,
            "clothing_items": int,
            "success": bool
        }
    """
    times = []
    last_result = {}

    for i in range(runs):
        with open(image_path, "rb") as f:
            files = {"person_image": f}
            data = {"model_type": model_type}

            start = time.time()
            try:
                response = requests.post(
                    f"{api_url}/analyze",
                    files=files,
                    data=data,
                    timeout=120
                )
                elapsed = time.time() - start
                times.append(elapsed)
                last_result = response.json()

                if runs > 1:
                    print(f"  Run {i+1}/{runs}: {elapsed:.2f}s")

            except Exception as e:
                print(f"  Run {i+1}/{runs}: FAILED - {e}")
                return {
                    "model": model_type,
                    "times": times,
                    "avg_time": 0,
                    "std_time": 0,
                    "body_parts": 0,
                    "clothing_items": 0,
                    "success": False
                }

    return {
        "model": model_type,
        "times": times,
        "avg_time": mean(times) if times else 0,
        "std_time": stdev(times) if len(times) > 1 else 0,
        "body_parts": len(last_result.get("body_parts", [])),
        "clothing_items": len(last_result.get("clothing_items", [])),
        "body_labels": [item["label"] for item in last_result.get("body_parts", [])],
        "clothing_labels": [item["label"] for item in last_result.get("clothing_items", [])],
        "success": last_result.get("status") == "completed"
    }


def run_benchmark(api_url: str, image_path: str, runs: int = 1):
    """전체 벤치마크 실행"""

    # 파일 존재 확인
    if not os.path.exists(image_path):
        print(f"[ERROR] 이미지 파일을 찾을 수 없습니다: {image_path}")
        sys.exit(1)

    # 서버 확인
    try:
        response = requests.get(f"{api_url}/", timeout=10)
        print(f"[OK] 서버 연결 확인: {api_url}\n")
    except Exception as e:
        print(f"[ERROR] 서버에 연결할 수 없습니다: {e}")
        sys.exit(1)

    print("=" * 60)
    print(" 세그멘테이션 모델 벤치마크")
    print("=" * 60)
    print(f" API URL: {api_url}")
    print(f" 이미지: {image_path}")
    print(f" 반복 횟수: {runs}")
    print("=" * 60)

    models = ["b2", "b5", "sam"]
    results = []

    for model in models:
        print(f"\n[{model.upper()}] 벤치마크 실행 중...")
        result = benchmark_model(api_url, image_path, model, runs)
        results.append(result)

        if result["success"]:
            print(f"  평균 시간: {result['avg_time']:.2f}s")
            if result["std_time"] > 0:
                print(f"  표준편차: {result['std_time']:.2f}s")

    # 결과 출력
    print("\n")
    print("=" * 60)
    print(" 벤치마크 결과")
    print("=" * 60)

    # 테이블 헤더
    if runs > 1:
        print(f"{'모델':<8} {'평균(초)':<10} {'표준편차':<10} {'신체':<6} {'의류':<6} {'상태':<8}")
    else:
        print(f"{'모델':<8} {'시간(초)':<10} {'신체':<6} {'의류':<6} {'상태':<8}")
    print("-" * 60)

    # 테이블 내용
    for r in results:
        status = "OK" if r["success"] else "FAIL"
        if runs > 1:
            print(f"{r['model']:<8} {r['avg_time']:<10.2f} {r['std_time']:<10.2f} {r['body_parts']:<6} {r['clothing_items']:<6} {status:<8}")
        else:
            print(f"{r['model']:<8} {r['avg_time']:<10.2f} {r['body_parts']:<6} {r['clothing_items']:<6} {status:<8}")

    print("-" * 60)

    # 상세 라벨 출력
    print("\n[상세 감지 결과]")
    for r in results:
        if r["success"]:
            print(f"\n{r['model'].upper()}:")
            print(f"  신체: {', '.join(r.get('body_labels', [])) or '(없음)'}")
            print(f"  의류: {', '.join(r.get('clothing_labels', [])) or '(없음)'}")

    # 최고 성능 모델 출력
    successful = [r for r in results if r["success"]]
    if successful:
        fastest = min(successful, key=lambda x: x["avg_time"])
        most_detailed = max(successful, key=lambda x: x["body_parts"] + x["clothing_items"])

        print("\n" + "=" * 60)
        print(" 분석")
        print("=" * 60)
        print(f" 가장 빠른 모델: {fastest['model'].upper()} ({fastest['avg_time']:.2f}s)")
        print(f" 가장 상세한 모델: {most_detailed['model'].upper()} (총 {most_detailed['body_parts'] + most_detailed['clothing_items']}개 영역)")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="세그멘테이션 모델 벤치마크")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API 서버 URL (기본값: http://localhost:8000)"
    )
    parser.add_argument(
        "--image",
        required=True,
        help="테스트할 이미지 경로"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="각 모델당 반복 횟수 (기본값: 1)"
    )

    args = parser.parse_args()
    run_benchmark(args.url, args.image, args.runs)


if __name__ == "__main__":
    main()
