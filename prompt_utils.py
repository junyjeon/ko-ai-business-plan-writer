# prompt_utils.py
import pyperclip
import time
import os
import uuid

# 기본 템플릿 정의 (코드 상단에 분리)
DEFAULT_ANALYSIS_TEMPLATE = """다음 기획서를 분석하고, 사업계획서 '문제 인식(Problem)' 섹션 작성에 필요하지만 누락된 정보를 찾아주세요:

기획서:
{business_idea}

다음 요소들에 대한 정보가 기획서에 충분히 포함되어 있는지 각각 '있음' 또는 '없음'으로 표시하고,
'없음'의 경우 구체적으로 어떤 정보가 필요한지 설명해주세요:
1. 시장 규모 (국내외 시장의 규모와 성장률 데이터)
2. 시장 트렌드 (최근 3년간 주요 변화)
3. 경쟁 제품 분석 (주요 경쟁사의 제품 특징과 한계점)
4. 고객이 겪는 문제점 (구체적이고 정량화된 자료)
5. 목표 고객 정의 (명확한 타겟 고객층)
6. 통계 자료 (객관적인 수치 데이터)

응답 형식:
요소1: [있음/없음] - 설명
요소2: [있음/없음] - 설명
...

추가 필요한 정보:
1. ...
2. ..."""

DEFAULT_GENERATION_TEMPLATE = """다음 사업 아이디어 기획 메모를 바탕으로 사업계획서의 '문제 인식(Problem)' 섹션을 작성해주세요:

### 기획 메모:
{business_idea}

### 기획서 분석 결과:
{analysis}

### 요청사항:
1. '1. 문제 인식 (Problem)_창업 아이템의 필요성' 섹션을 작성하세요.
2. 시장 현황 및 문제점을 객관적 데이터와 함께 제시하세요.
3. 해결해야 할 핵심 문제점 2-3가지를 구체적으로 설명하세요.
4. 기획서에 없는 정보는 합리적으로 가정하되, 가정한 내용은 "[필요 정보: 실제 시장 데이터로 교체 필요]"와 같은 형식으로 표시해주세요.
5. 총 500자 내외로 작성하세요.

### 형식:
1. 문제 인식 (Problem)_창업 아이템의 필요성
◦ [시장 현황 및 트렌드 분석]
- 첫 번째 핵심 포인트
- 두 번째 핵심 포인트
◦ [현재 시장의 문제점 및 한계]
- 첫 번째 문제점
- 두 번째 문제점"""


def load_prompt_template(file_path):
    """프롬프트 템플릿 파일 읽기"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"경고: 프롬프트 파일 '{file_path}'을(를) 찾을 수 없습니다.")
        # 프롬프트 디렉토리 확인 및 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return None
    except Exception as e:
        print(f"프롬프트 파일 읽기 오류: {str(e)}")
        return None

def format_prompt_safely(template, **kwargs):
    """템플릿에 변수를 안전하게 삽입"""
    if not template:
        return None
    
    try:
        # 모든 키워드 인수를 템플릿에 적용
        return template.format(**kwargs)
    except KeyError as e:
        # 템플릿에 정의되지 않은 변수가 있을 경우
        print(f"템플릿에 필요한 변수가 누락되었습니다: {e}")
        # 부분적으로 포맷 적용 (가능한 변수만)
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            if placeholder in template:
                template = template.replace(placeholder, str(value))
        return template
    except Exception as e:
        print(f"템플릿 형식 오류: {str(e)}")
        return template  # 원본 템플릿 반환

def generate_problem_analysis_prompt(business_idea):
    """분석 프롬프트 생성 및 클립보드에 복사"""
    # 프롬프트 템플릿 로드
    template_path = os.path.join("prompts", "analysis_prompt.txt")
    template = load_prompt_template(template_path)
    
    if not template:
        print("프롬프트 파일이 없습니다. 기본 템플릿을 생성하고 계속 진행합니다.")
        # 기본 템플릿 사용 - 상단에 정의된 변수 활용
        template = DEFAULT_ANALYSIS_TEMPLATE
        
        # 기본 템플릿 파일 생성
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"'{template_path}' 파일이 생성되었습니다.")
        except Exception as e:
            print(f"기본 템플릿 파일 생성 오류: {str(e)}")

    # 안전하게 변수 삽입
    prompt = format_prompt_safely(template, business_idea=business_idea)
    
    # 클립보드에 복사
    pyperclip.copy(prompt)
    print("\n===== 분석 프롬프트가 클립보드에 복사되었습니다 =====")
    print("1. Cursor AI에 붙여넣기 후 실행해주세요")
    print("2. 응답이 생성되면 복사 버튼을 클릭하세요")
    print("3. 복사가 완료되면 Enter를 눌러 계속하세요...")
    input()  # 사용자 입력 대기
    
    # 클립보드에서 응답 읽기
    analysis = pyperclip.paste()
    print(f"\n분석 결과를 성공적으로 가져왔습니다. (길이: {len(analysis)} 자)")
    
    # 임시 ID 생성하여 파일명 충돌 방지
    temp_id = str(uuid.uuid4())[:8]
    
    # 임시 파일로 저장
    temp_path = os.path.join("output", f"analysis_result_{temp_id}.txt")
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(analysis)
    
    return analysis

def generate_problem_section_prompt(business_idea, analysis):
    """섹션 작성 프롬프트 생성 및 클립보드에 복사"""
    # 프롬프트 템플릿 로드
    template_path = os.path.join("prompts", "generation_prompt.txt")
    template = load_prompt_template(template_path)
    
    if not template:
        print("프롬프트 파일이 없습니다. 기본 템플릿을 생성하고 계속 진행합니다.")
        # 기본 템플릿 사용 - 상단에 정의된 변수 활용
        template = DEFAULT_GENERATION_TEMPLATE
        
        # 기본 템플릿 파일 생성
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"'{template_path}' 파일이 생성되었습니다.")
        except Exception as e:
            print(f"기본 템플릿 파일 생성 오류: {str(e)}")
    
    # 안전하게 변수 삽입
    prompt = format_prompt_safely(template, business_idea=business_idea, analysis=analysis)
    
    # 클립보드에 복사
    pyperclip.copy(prompt)
    print("\n===== 섹션 작성 프롬프트가 클립보드에 복사되었습니다 =====")
    print("1. Cursor AI에 붙여넣기 후 실행해주세요")
    print("2. 응답이 생성되면 복사 버튼을 클릭하세요")
    print("3. 복사가 완료되면 Enter를 눌러 계속하세요...")
    input()  # 사용자 입력 대기
    
    # 클립보드에서 응답 읽기
    section = pyperclip.paste()
    print(f"\n섹션 작성 결과를 성공적으로 가져왔습니다. (길이: {len(section)} 자)")
    
    # 임시 ID 생성
    temp_id = str(uuid.uuid4())[:8]
    
    # 파일로 저장
    temp_path = os.path.join("output", f"problem_section_{temp_id}.txt")
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(section)
    
    return section