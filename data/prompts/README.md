# 프롬프트 파일 디렉토리

이 디렉토리에는 기획서 분석 및 사업계획서 각 섹션 생성에 사용되는 프롬프트 템플릿이 포함되어 있습니다.

## 디렉토리 구조

- `analysis_prompts/`: 각 섹션의 분석 프롬프트
  - `problem_analysis.txt`: 문제 인식 섹션 분석 프롬프트
  - `solution_analysis.txt`: 솔루션 섹션 분석 프롬프트
  - `market_analysis.txt`: 시장 분석 섹션 분석 프롬프트
  - `business_model_analysis.txt`: 비즈니스 모델 섹션 분석 프롬프트
  - `team_analysis.txt`: 팀 구성 섹션 분석 프롬프트
  - `scaleup_analysis.txt`: 스케일업 전략 섹션 분석 프롬프트

- `generation_prompts/`: 각 섹션의 생성 프롬프트
  - `problem_generation.txt`: 문제 인식 섹션 생성 프롬프트
  - `solution_generation.txt`: 솔루션 섹션 생성 프롬프트
  - `market_generation.txt`: 시장 분석 섹션 생성 프롬프트
  - `business_model_generation.txt`: 비즈니스 모델 섹션 생성 프롬프트
  - `team_generation.txt`: 팀 구성 섹션 생성 프롬프트
  - `scaleup_generation.txt`: 스케일업 전략 섹션 생성 프롬프트

- `section_config.json`: 섹션 설정 파일 (섹션 메타데이터 정의)

## 프롬프트 형식

### 분석 프롬프트 형식
분석 프롬프트는 사업 계획서 초안의 누락된 정보를 식별하는 데 사용됩니다.
- 변수: `{business_idea}` - 사용자가 제공한 기획서 내용이 이 변수에 삽입됩니다.

### 생성 프롬프트 형식
생성 프롬프트는 분석 결과를 바탕으로 사업 계획서의 해당 섹션을 작성하는 데 사용됩니다.
- 변수: 
  - `{business_idea}` - 사용자가 제공한 기획서 내용
  - `{analysis}` - 분석 단계에서 생성된 분석 결과

## 프롬프트 사용자 정의
필요에 따라 프롬프트 파일을 수정하여 출력 형식이나 요구사항을 변경할 수 있습니다.
변수 이름(`{business_idea}`, `{analysis}`)은 그대로 유지해야 합니다. 