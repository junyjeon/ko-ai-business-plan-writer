# simple_problem_generator.py
import sys
import os
from dotenv import load_dotenv

# grok3-api 디렉토리 경로 추가
sys.path.append(os.path.abspath("grok3-api"))
from grok_client import GrokClient

load_dotenv()

# Grok-3 클라이언트 설정
cookies = {
    "sso": os.getenv("GROK_SSO"),
    "sso-rw": os.getenv("GROK_SSO_RW")
}

# 쿠키 존재 확인
if not cookies["sso"] or not cookies["sso-rw"]:
    print("오류: .env 파일에 'GROK_SSO'와 'GROK_SSO_RW' 값이 없거나 비어 있습니다.")
    sys.exit(1)

# 인스턴스 생성 전 출력
print(f"쿠키 확인: sso={cookies['sso'][:5]}..., sso-rw={cookies['sso-rw'][:5]}...")

client = GrokClient(cookies)

# 텍스트 파일에서 프롬프트 읽기
def load_prompt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"오류: {file_path} 파일을 찾을 수 없습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"파일 읽기 오류: {str(e)}")
        sys.exit(1)

# 텍스트 파일에서 기획서 읽기
def read_business_idea_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"오류: {file_path} 파일을 찾을 수 없습니다."
    except Exception as e:
        return f"파일 읽기 오류: {str(e)}"

# 기획서 분석 및 부족한 내용 체크
def analyze_business_idea(business_idea, analysis_prompt_template):
    # 템플릿에 기획서 내용 삽입
    prompt = analysis_prompt_template.format(business_idea=business_idea)
    
    try:
        print("분석 프롬프트 전송 중...")
        response = client.send_message(prompt)
        print(f"분석 응답 수신 (길이: {len(response) if response else 0})")
        return response
    except Exception as e:
        error_msg = f"분석 중 오류가 발생했습니다: {str(e)}"
        print(error_msg)
        return error_msg

# 문제 인식 섹션 생성
def generate_problem_section(business_idea, analysis_prompt_template, generation_prompt_template):
    # 먼저 기획서 분석
    analysis = analyze_business_idea(business_idea, analysis_prompt_template)
    
    # 문제 인식 섹션 생성
    generation_prompt = generation_prompt_template.format(
        business_idea=business_idea,
        analysis=analysis
    )
    
    try:
        response = client.send_message(generation_prompt)
        return {
            "analysis": analysis,
            "problem_section": response
        }
    except Exception as e:
        return {
            "analysis": analysis,
            "problem_section": f"생성 중 오류가 발생했습니다: {str(e)}"
        }

# 메인 실행 부분
if __name__ == "__main__":
    # API 통신 테스트
    try:
        print("Grok API 통신 테스트 중...")
        test_response = client.send_message("안녕하세요?")
        print(f"API 테스트 성공 (응답 길이: {len(test_response) if test_response else 0})")
    except Exception as e:
        print(f"API 테스트 실패: {str(e)}")
        sys.exit(1)
        
    # 프롬프트 템플릿 로드
    try:
        prompts_dir = "prompts"
        
        # 디렉토리 확인
        if not os.path.exists(prompts_dir):
            os.makedirs(prompts_dir)
            print(f"'{prompts_dir}' 디렉토리를 생성했습니다.")
            
            # 기본 분석 프롬프트 생성
            with open(os.path.join(prompts_dir, "analysis_prompt.txt"), "w", encoding="utf-8") as f:
                f.write("""다음 기획서를 분석하고, 사업계획서 '문제 인식(Problem)' 섹션 작성에 필요하지만 누락된 정보를 찾아주세요:

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
2. ...""")
            
            # 기본 생성 프롬프트 생성
            with open(os.path.join(prompts_dir, "generation_prompt.txt"), "w", encoding="utf-8") as f:
                f.write("""다음 사업 아이디어 기획 메모를 바탕으로 사업계획서의 '문제 인식(Problem)' 섹션을 작성해주세요:

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
- 두 번째 문제점""")
            
            print("기본 프롬프트 파일을 생성했습니다. 필요에 따라 내용을 수정하세요.")
        
        analysis_prompt_path = os.path.join(prompts_dir, "analysis_prompt.txt")
        generation_prompt_path = os.path.join(prompts_dir, "generation_prompt.txt")
        
        print(f"프롬프트 파일 로드 중: {analysis_prompt_path}, {generation_prompt_path}")
        
        analysis_prompt_template = load_prompt(analysis_prompt_path)
        generation_prompt_template = load_prompt(generation_prompt_path)
        
        print("프롬프트 파일이 성공적으로 로드되었습니다.")
    except Exception as e:
        print(f"프롬프트 파일 처리 중 오류: {str(e)}")
        sys.exit(1)
    
    # 파일 경로 입력 (기본값 설정 가능)
    default_file = "business_idea.txt"
    file_path = input(f"기획서 텍스트 파일 경로 (기본값: {default_file}): ").strip()
    
    if not file_path:
        file_path = default_file
    
    # 파일에서 기획서 읽기
    business_idea = read_business_idea_from_file(file_path)
    
    # 파일 읽기 오류 확인
    if business_idea.startswith("오류:") or business_idea.startswith("파일 읽기 오류:"):
        print(business_idea)
        sys.exit(1)
    
    print(f"'{file_path}' 파일을 성공적으로 읽었습니다. (길이: {len(business_idea)} 자)")
    
    # 생성 및 출력
    print("분석 및 생성 중...")
    result = generate_problem_section(
        business_idea, 
        analysis_prompt_template, 
        generation_prompt_template
    )
    
    print("\n===== 기획서 분석 결과 =====\n")
    print(result["analysis"])
    
    print("\n===== 생성된 문제 인식(Problem) 섹션 =====\n")
    print(result["problem_section"])
    
    # 결과 파일 저장
    output_file = "problem_section_result.txt"
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write("===== 기획서 분석 결과 =====\n\n")
            file.write(result["analysis"])
            file.write("\n\n===== 생성된 문제 인식(Problem) 섹션 =====\n\n")
            file.write(result["problem_section"])
        print(f"\n결과가 '{output_file}' 파일에 저장되었습니다.")
    except Exception as e:
        print(f"\n결과 저장 중 오류 발생: {str(e)}")