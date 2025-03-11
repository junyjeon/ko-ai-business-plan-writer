# 예비창업패키지 사업계획서 작성 도우미

예비창업패키지 사업계획서 작성을 돕는 AI 기반 도구입니다. 기획서를 분석하고 사업계획서의 각 섹션을 자동으로 작성해주는 기능을 제공합니다.

## 기능

- 기획서 분석: 여러 측면에서 기획서를 분석하고 누락된 정보를 식별
- 문제 인식(Problem) 섹션 작성: 분석 결과를 바탕으로 사업계획서의 문제 인식 섹션 작성
- 다중 기획서 처리: 여러 기획서를 동시에 처리하고 결과를 하나의 문서로 통합
- Word 및 PDF 문서 생성: 작성된 내용을 Word 문서로 생성, 선택적으로 PDF 템플릿에 내용 추가

## 프로젝트 구조

```
ko-ai-business-plan-writer/
├── main.py                  # 메인 진입점
├── requirements.txt         # 의존성 관리
├── README.md                # 문서
├── MIGRATION_GUIDE.md       # 마이그레이션 가이드
├── cursor.rules.md          # 개발 규칙
├── migrate.py               # 마이그레이션 스크립트
├── cleanup_legacy.py        # 레거시 파일 삭제 스크립트
│
├── core/                    # 핵심 로직
│   ├── business_plan.py     # 사업계획서 모델 및 서비스
│   └── document_manager.py  # 문서 처리 서비스
│
├── utils/                   # 유틸리티
│   ├── prompt_utils.py      # 프롬프트 관련 유틸리티
│   ├── pdf_utils.py         # PDF 관련 유틸리티
│   └── file_utils.py        # 파일 작업 유틸리티
│
├── data/                    # 데이터 파일
│   ├── prompts/             # 프롬프트 파일
│   │   ├── analysis_prompt.txt
│   │   └── generation_prompt.txt
│   ├── proposals/           # 입력 사업 아이디어
│   └── templates/           # 템플릿 파일
│
├── tests/                   # 테스트 코드
│   └── test_business_plan_flow.py
│
└── output/                  # 결과물 저장
```

## 새 구조로 마이그레이션

프로젝트가 단일 책임 원칙(SRP)에 따라 새 구조로 개선되었습니다. 마이그레이션 단계:

1. **파일 마이그레이션 실행**
   ```bash
   python migrate.py
   ```

2. **레거시 파일 정리** (선택사항)
   ```bash
   python cleanup_legacy.py
   ```

자세한 마이그레이션 정보는 [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)를 참조하세요.

## 사용법

1. 환경 설정:
   ```bash
   pip install -r requirements.txt
   ```

2. 실행:
   ```bash
   python main.py
   ```

3. 프로세스:
   - 입력 방식 선택 (단일 파일, 디렉토리 내 모든 .txt 파일, 여러 파일 지정)
   - 입력 파일 경로 지정
   - 자동으로 분석 및 섹션 작성 진행
   - 결과물 output 디렉토리에 저장

## 테스트 실행

기능 테스트를 실행하려면:
```bash
python tests/test_business_plan_flow.py
```

## 의존성

- Python 3.8+
- docx (Python-docx)
- PyPDF2
- reportlab
- pyperclip