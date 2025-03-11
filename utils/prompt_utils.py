# prompt_utils.py
import pyperclip
import time
import os
import uuid
import sys
import json

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

# 섹션 설정 로드
def load_section_config():
    """섹션 설정 파일 로드"""
    config_path = os.path.join("data", "section_config.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"경고: 섹션 설정 파일 '{config_path}'을(를) 찾을 수 없습니다.")
        return {"sections": []}
    except Exception as e:
        print(f"섹션 설정 파일 읽기 오류: {str(e)}")
        return {"sections": []}

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

def generate_analysis_prompt(section_id, business_idea):
    """섹션 분석 프롬프트 생성"""
    config = load_section_config()
    section = next((s for s in config["sections"] if s["id"] == section_id), None)
    
    if not section:
        print(f"경고: '{section_id}' 섹션을 설정에서 찾을 수 없습니다.")
        return None
    
    # 분석 프롬프트 템플릿 로드
    analysis_prompt_path = section.get("analysis_prompt")
    if not analysis_prompt_path:
        print(f"경고: '{section_id}' 섹션에 분석 프롬프트 경로가 지정되지 않았습니다.")
        return None
    
    template = load_prompt_template(analysis_prompt_path)
    if not template:
        print(f"경고: '{analysis_prompt_path}' 분석 프롬프트 템플릿을 로드할 수 없습니다.")
        return None
    
    # 프롬프트 생성
    prompt = template.format(business_idea=business_idea)
    
    # 클립보드에 복사
    try:
        pyperclip.copy(prompt)
        print(f"프롬프트가 클립보드에 복사되었습니다.")
    except:
        print("클립보드 복사에 실패했습니다.")
    
    return prompt

def generate_section_prompt(section_id, business_idea, analysis):
    """섹션 생성 프롬프트 생성"""
    config = load_section_config()
    section = next((s for s in config["sections"] if s["id"] == section_id), None)
    
    if not section:
        print(f"경고: '{section_id}' 섹션을 설정에서 찾을 수 없습니다.")
        return None
    
    # 생성 프롬프트 템플릿 로드
    generation_prompt_path = section.get("generation_prompt")
    if not generation_prompt_path:
        print(f"경고: '{section_id}' 섹션에 생성 프롬프트 경로가 지정되지 않았습니다.")
        return None
    
    template = load_prompt_template(generation_prompt_path)
    if not template:
        print(f"경고: '{generation_prompt_path}' 생성 프롬프트 템플릿을 로드할 수 없습니다.")
        return None
    
    # 프롬프트 생성
    prompt = template.format(business_idea=business_idea, analysis=analysis)
    
    # 클립보드에 복사
    try:
        pyperclip.copy(prompt)
        print(f"프롬프트가 클립보드에 복사되었습니다.")
    except:
        print("클립보드 복사에 실패했습니다.")
    
    return prompt

# 레거시 호환성 유지를 위한 함수
def generate_problem_analysis_prompt(business_idea):
    """문제 인식 섹션의 분석 프롬프트 생성 (레거시 호환성)"""
    return generate_analysis_prompt("problem", business_idea)

def generate_problem_section_prompt(business_idea, analysis):
    """문제 인식 섹션의 생성 프롬프트 생성 (레거시 호환성)"""
    return generate_section_prompt("problem", business_idea, analysis) 