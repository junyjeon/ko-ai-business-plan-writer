# 생성 프롬프트 디렉토리

이 디렉토리에는 분석 결과를 바탕으로 사업계획서 각 섹션을 작성하는 데 사용되는 프롬프트가 포함되어 있습니다.

## 파일 목록

- `problem_generation.txt`: 문제 인식 섹션 생성 프롬프트
- `solution_generation.txt`: 솔루션 섹션 생성 프롬프트
- `market_generation.txt`: 시장 분석 섹션 생성 프롬프트
- `business_model_generation.txt`: 비즈니스 모델 섹션 생성 프롬프트
- `team_generation.txt`: 팀 구성 섹션 생성 프롬프트
- `scaleup_generation.txt`: 스케일업 전략 섹션 생성 프롬프트

## 생성 프롬프트 형식

각 생성 프롬프트는 다음과 같은 구조를 갖습니다:

```
주어진 기획서와 분석 정보를 바탕으로 사업계획서의 '[섹션 이름]' 섹션을 작성해주세요.

기획서:
{business_idea}

분석 결과:
{analysis}

다음 요소들을 포함하여 작성해주세요:
1. [포함할 요소1]
2. [포함할 요소2]
...

작성 시 주의사항:
- [주의사항1]
- [주의사항2]
...
- 500자 내외로 작성
- 가정한 내용이 있다면 "[가정: 내용]" 형식으로 표시
```

## 사용자 정의 방법

1. 각 섹션의 특성에 맞는 포함 요소를 정의하세요.
2. 작성 시 주의사항은 문서의 품질과 일관성을 유지하는 데 중요합니다.
3. 문자 수 제한을 명시하여 간결한 내용 작성을 유도하세요.
4. 다음 변수를 반드시 포함해야 합니다:
   - `{business_idea}`: 사용자가 제공한 원본 기획서
   - `{analysis}`: 분석 단계에서 얻은 결과 정보

## 변수 사용법

프롬프트 내에서 다음 변수를 사용할 수 있습니다:
- `{business_idea}`: 사용자가 제공한 사업 기획서
- `{analysis}`: 분석 단계에서 생성된 분석 결과
- `{section_title}`: 섹션 제목

## 사용 지침

프롬프트를 수정할 때는 다음 사항을 고려하세요:
1. 구체적이고 명확한 지시를 제공하세요
2. 예시 형식을 제공하여 AI가 일관된 출력을 생성하도록 유도하세요
3. 부족한 정보를 다루는 방법을 명확히 안내하세요 (예: "[필요 정보: 실제 데이터로 교체 필요]") 