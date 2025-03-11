# 테스트 문서

이 폴더는 사업계획서 작성 시스템의 테스트 코드를 포함하고 있습니다.

## 테스트 파일 목록

1. `test_business_plan_flow.py` - 사업계획서 작성 워크플로우 테스트

## 테스트 실행 방법

```bash
# 기본 테스트 실행
python tests/test_business_plan_flow.py

# unittest 모듈 직접 사용
python -m unittest tests/test_business_plan_flow.py
```

## 테스트 범위

- **단위 테스트**: 개별 구성 요소의 기능 테스트
  - BusinessPlan 클래스 테스트
  - 프롬프트 템플릿 로드 테스트
  - 기획서 로드 기능 테스트

- **통합 테스트**: 전체 문서 생성 워크플로우 테스트
  - 문서 생성 기능 테스트

## 테스트 결과

테스트 출력 파일은 `tests/test_output/` 디렉토리에 생성됩니다. 