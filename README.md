# 예비창업패키지 사업계획서 작성 도우미

AI 기반 사업계획서 작성 도우미 도구입니다. 사용자가 제공한 기획서를 분석하고, 사업계획서의 다양한 섹션을 자동으로 생성합니다.

## 기능

1. **기획서 분석**: 사용자의 기획서를 분석하여 사업계획서 작성에 필요한 요소 중 누락된 정보를 식별합니다.

2. **다중 섹션 지원**: 다음 섹션들을 독립적으로 생성할 수 있습니다:
   - 문제 인식 (Problem)
   - 솔루션 (Solution)
   - 시장 분석 (Market Analysis)
   - 비즈니스 모델 (Business Model)
   - 팀 구성 (Team)
   - 스케일업 전략 (Scale-up Strategy)

3. **섹션 선택**: 필요한 섹션만 선택하여 처리할 수 있습니다.

4. **다중 기획서 처리**: 여러 기획서 파일을 일괄 처리하고 결과를 하나의 문서로 통합할 수 있습니다.

5. **문서 생성**: 결과를 Word 및 PDF 문서로 생성합니다.

6. **외부 프롬프트 관리**: 프롬프트 파일을 외부에서 관리하여 쉽게 수정할 수 있습니다.

7. **API 데이터 통합**: 다양한 한국 데이터 API를 활용하여 기획서에 부족한 정보를 보완합니다:
   - 공공데이터 포털 API: 다양한 공공 데이터 활용
   - KISTI API: 과학기술 정보와 시장/산업 분석 데이터
   - 통계청 KOSIS API: 정확한 인구통계, 경제지표 제공
   - 한국은행 ECOS API: 경제지표, 환율, 금리 등 금융 데이터

## 프로젝트 구조

```
ko-ai-business-plan-writer/
├── main.py                  # 메인 프로그램
├── README.md                # 프로젝트 설명
├── requirements.txt         # 필요 패키지 목록
├── config/                  # 설정 파일
│   └── api_keys.json        # API 키 설정
├── core/                    # 핵심 기능 모듈
│   ├── business_plan.py     # 사업계획서 클래스
│   └── document_manager.py  # 문서 생성 관리
├── data/                    # 데이터 파일
│   ├── prompts/             # 프롬프트 파일
│   │   ├── section_config.json        # 섹션 설정
│   │   ├── README.md                  # 프롬프트 사용 설명
│   │   ├── analysis_prompts/          # 분석 프롬프트
│   │   │   ├── problem_analysis.txt
│   │   │   ├── solution_analysis.txt
│   │   │   └── ...
│   │   └── generation_prompts/        # 생성 프롬프트
│   │       ├── problem_generation.txt
│   │       ├── solution_generation.txt
│   │       └── ...
│   └── proposals/           # 기획서 파일
├── output/                  # 결과 파일 저장
└── utils/                   # 유틸리티 모듈
    ├── api_service.py       # API 서비스
    └── data_integration.py  # 데이터 통합
```

## 설치 방법

1. 저장소 클론:
```bash
git clone https://github.com/username/ko-ai-business-plan-writer.git
cd ko-ai-business-plan-writer
```

2. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 필요 패키지 설치:
```bash
pip install -r requirements.txt
```

## 사용 방법

1. 프로그램 실행:
```bash
python main.py
```

2. 처리할 섹션 선택 (콘솔에서 선택)
3. 입력 방식 선택 (단일 파일, 디렉토리, 여러 파일)
4. 안내에 따라 프롬프트 복사 및 AI 도구에 붙여넣기
5. 결과 확인 및 문서 생성

## API 키 설정

API 데이터 통합 기능을 사용하려면 다음 경로에 API 키를 설정하세요:
```
config/api_keys.json
```

설정 파일은 다음과 같은 형식입니다:
```json
{
  "public_data_portal": {
    "api_key": "YOUR_API_KEY",
    "base_url": "https://www.data.go.kr/api"
  },
  "kisti": {
    "api_key": "YOUR_API_KEY",
    "base_url": "https://api.kisti.re.kr"
  },
  "kosis": {
    "api_key": "YOUR_API_KEY",
    "base_url": "https://kosis.kr/openapi"
  },
  "ecos": {
    "api_key": "YOUR_API_KEY",
    "base_url": "https://ecos.bok.or.kr/api"
  }
}
```

## 새 섹션 추가 방법

1. `data/prompts/section_config.json` 파일에 새 섹션 정보 추가
2. `data/prompts/analysis_prompts/` 디렉토리에 분석 프롬프트 파일 추가 (예: `new_section_analysis.txt`)
3. `data/prompts/generation_prompts/` 디렉토리에 생성 프롬프트 파일 추가 (예: `new_section_generation.txt`)

## 테스트

테스트 실행:
```bash
python -m unittest discover tests
```