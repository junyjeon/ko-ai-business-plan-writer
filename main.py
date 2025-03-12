import os
import re
import sys
import glob
import json
import pyperclip
import datetime
from typing import List, Dict, Optional

# utils 폴더 및 core 폴더를 import 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 새로운 API 서비스와 데이터 통합 모듈 임포트
from utils.api_service import APIService
from utils.data_integration import DataIntegration
from utils.agent import BusinessPlanAgent
from utils.agent_system import BusinessPlanAgentSystem  # 새로운 에이전트 시스템 추가

# 기존 클래스 임포트
from core.business_plan import BusinessPlan, BusinessPlanService
from core.document_manager import DocumentManager, merge_docx_files

# 버전 설정
VERSION = "3.1.0"  # OpenAI Agents SDK 지원 추가

def generate_analysis_prompt(section_id: str, business_idea: str) -> str:
    """분석 프롬프트 생성"""
    # 프롬프트 파일 경로 결정 - 새 구조와 레거시 구조 모두 지원
    new_path = os.path.join("data", "prompts", "analysis_prompts", f"{section_id}_analysis.txt")
    legacy_path = os.path.join("prompts", f"{section_id}_analysis.txt")
    
    # 파일 경로 결정 (새 구조 우선, 없으면 레거시 경로)
    prompt_path = new_path if os.path.exists(new_path) else legacy_path
    
    if not os.path.exists(prompt_path):
        # 통합 분석 프롬프트 사용 (새 구조 또는 레거시 구조)
        new_fallback_path = os.path.join("data", "prompts", "analysis_prompt.txt")
        legacy_fallback_path = os.path.join("prompts", "analysis_prompt.txt")
        prompt_path = new_fallback_path if os.path.exists(new_fallback_path) else legacy_fallback_path
    
    if not os.path.exists(prompt_path):
        print(f"오류: {section_id} 섹션을 위한 분석 프롬프트 파일을 찾을 수 없습니다.")
        return ""
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        # business_idea 변수 대체
        prompt = template.replace("{business_idea}", business_idea)
        
        # 프롬프트 클립보드에 복사
        pyperclip.copy(prompt)
        return prompt
    except Exception as e:
        print(f"프롬프트 생성 중 오류 발생: {str(e)}")
        return ""

def generate_section_prompt(section_id: str, business_idea: str, analysis_result: str) -> str:
    """섹션 생성 프롬프트 생성"""
    # 프롬프트 파일 경로 결정 - 새 구조와 레거시 구조 모두 지원
    new_path = os.path.join("data", "prompts", "generation_prompts", f"{section_id}_generation.txt")
    legacy_path = os.path.join("prompts", f"{section_id}_generation.txt")
    
    # 파일 경로 결정 (새 구조 우선, 없으면 레거시 경로)
    prompt_path = new_path if os.path.exists(new_path) else legacy_path
    
    if not os.path.exists(prompt_path):
        # 통합 생성 프롬프트 사용 (새 구조 또는 레거시 구조)
        new_fallback_path = os.path.join("data", "prompts", "generation_prompt.txt")
        legacy_fallback_path = os.path.join("prompts", "generation_prompt.txt")
        prompt_path = new_fallback_path if os.path.exists(new_fallback_path) else legacy_fallback_path
    
    if not os.path.exists(prompt_path):
        print(f"오류: {section_id} 섹션을 위한 생성 프롬프트 파일을 찾을 수 없습니다.")
        return ""
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        # 변수 대체
        prompt = template.replace("{business_idea}", business_idea).replace("{analysis}", analysis_result)
        
        # 프롬프트 클립보드에 복사
        pyperclip.copy(prompt)
        return prompt
    except Exception as e:
        print(f"프롬프트 생성 중 오류 발생: {str(e)}")
        return ""

def load_section_config() -> Dict:
    """섹션 설정 로드"""
    # 섹션 설정 파일 경로 결정 - 새 구조와 레거시 구조 모두 지원
    new_path = os.path.join("data", "prompts", "section_config.json")
    legacy_path = os.path.join("config", "section_config.json")
    
    config_path = new_path if os.path.exists(new_path) else legacy_path
    
    if not os.path.exists(config_path):
        print(f"오류: 섹션 설정 파일을 찾을 수 없습니다: {config_path}")
        return {"sections": []}
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        # 섹션 제목에서 번호 제거 (원본 제목은 original_title로 보존)
        for section in config.get("sections", []):
            if "title" in section:
                # 원본 제목 보존
                section["original_title"] = section["title"]
                # 섹션 제목에서 번호 제거
                section["title"] = re.sub(r'^\d+\.\s+', '', section["title"])
        
        return config
    except Exception as e:
        print(f"섹션 설정 로드 중 오류 발생: {str(e)}")
        return {"sections": []}

def process_single_proposal(file_path, output_dir, selected_sections, use_agent_sdk=False):
    """단일 기획서 처리"""
    file_name = os.path.basename(file_path)
    file_base_name = os.path.splitext(file_name)[0]
    
    print(f"\n===== 기획서 처리 중: {file_name} =====")
    
    # 서비스 인스턴스 생성
    bp_service = BusinessPlanService()
    doc_manager = DocumentManager(output_dir)
    
    if use_agent_sdk:
        # OpenAI Agents SDK 기반 에이전트 시스템 사용
        agent_system = BusinessPlanAgentSystem()
        
        # 기획서 읽기
        business_idea = bp_service.load_business_idea(file_path)
        if not business_idea:
            print(f"{file_path} 파일을 읽을 수 없습니다. 이 파일은 건너뜁니다.")
            return None
        
        print(f"기획서를 성공적으로 읽었습니다. (길이: {len(business_idea)} 자)")
        print(f"\n🚀 OpenAI Agents SDK를 사용한 에이전트 시스템이 활성화되었습니다.")
        
        # 에이전트 시스템을 통한 처리
        print("\n🔄 에이전트 시스템이 비즈니스 플랜을 처리하고 있습니다. 이 작업은 몇 분 정도 소요될 수 있습니다...")
        result = agent_system.run(business_idea, selected_sections)
        
        if result:
            # 사업계획서 객체 생성 및 섹션 추가
            business_plan = BusinessPlan(f"{file_base_name}의 사업계획서")
            
            for section_name, content in result["sections"].items():
                section_id = section_name.lower().replace(' ', '_')
                business_plan.add_section(section_id, content)
            
            # 문서 생성
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{file_base_name}_plan_{timestamp}.docx"
            docx_path = doc_manager.create_word_document(business_plan, output_filename)
            
            if docx_path:
                print(f"\n✅ 사업계획서 문서가 생성되었습니다: {docx_path}")
                
                # PDF 변환 확인
                create_pdf = input("\nPDF로 변환하시겠습니까? (y/n): ").strip().lower() == 'y'
                if create_pdf:
                    pdf_path = doc_manager.create_pdf_from_docx(docx_path)
                    if pdf_path:
                        print(f"✅ PDF가 생성되었습니다: {pdf_path}")
            
            return docx_path
        else:
            print("\n❌ 에이전트 시스템 처리 중 오류가 발생했습니다.")
            return None
    else:
        # 기존 에이전트 사용
        agent = BusinessPlanAgent()  # 기존 에이전트 추가
    
    # 기획서 읽기
    business_idea = bp_service.load_business_idea(file_path)
    if not business_idea:
        print(f"{file_path} 파일을 읽을 수 없습니다. 이 파일은 건너뜁니다.")
        return None
    
    print(f"기획서를 성공적으로 읽었습니다. (길이: {len(business_idea)} 자)")
    
    # 사업계획서 객체 생성
    business_plan = bp_service.create_plan(f"{file_base_name}의 사업계획서", business_idea)
    
    # 섹션 설정 로드
    section_config = load_section_config()
    sections = section_config.get("sections", [])
    
    # 선택된 섹션 목록 또는 모든 섹션
    sections_to_process = [s for s in sections if s["id"] in selected_sections or not selected_sections]
    
    if not sections_to_process:
        print("처리할 섹션이 없습니다.")
        return None
    
    # 에이전트 사용 가능 여부 확인
    api_availability = agent.api_service.check_api_availability()
    can_use_api = any(api_availability.values())
    
    if can_use_api:
        print("\n🔍 에이전트가 활성화되었습니다. 외부 데이터를 지능적으로 검색할 수 있습니다.")
    else:
        print("\n⚠️ 경고: API 키가 설정되지 않아 에이전트의 외부 데이터 검색 기능이 제한됩니다.")
        print("API 기능을 사용하려면 config/api_keys.json 파일에 API 키를 설정하세요.")
    
    # 선택된 모든 섹션 처리
    for section in sections_to_process:
        section_id = section["id"]
        section_title = section["title"]
        
        print(f"\n===== {section_title} 섹션 처리 중 =====")
        
        # 1단계: 분석 프롬프트 생성 및 결과 가져오기
        print(f"\n1단계: 기획서 분석 - {section_title}")
        analysis = generate_analysis_prompt(section_id, business_idea)
        
        if not analysis:
            print(f"{section_title} 섹션을 위한 분석 프롬프트를 생성할 수 없습니다.")
            continue
        
        # 클립보드에 복사
        pyperclip.copy(analysis)
        print("분석 프롬프트가 클립보드에 복사되었습니다.")
        copy_again = True
        
        while copy_again:
            print("1. Cursor AI에 붙여넣기 후 실행해주세요")
            print("2. 응답이 생성되면 복사 버튼을 클릭하세요")
            option = input("3. 복사가 완료되면 Enter를 눌러 계속하세요 (다시 복사하려면 'r' 입력): ").strip().lower()
            
            if option == 'r':
                pyperclip.copy(analysis)
                print("분석 프롬프트가 클립보드에 다시 복사되었습니다.")
            else:
                copy_again = False
        
        # 클립보드에서 분석 결과 가져오기
        analysis_result = pyperclip.paste()
        if not analysis_result or analysis_result == analysis:
            print("경고: 클립보드에서 유효한 분석 결과를 가져올 수 없습니다.")
            analysis_result = input("직접 분석 결과를 입력하시겠습니까? (y/n): ").strip().lower()
            if analysis_result == 'y':
                print("분석 결과를 입력하세요. 입력을 마치려면 빈 줄에서 Ctrl+D (Unix) 또는 Ctrl+Z (Windows)를 입력하세요:")
                lines = []
                while True:
                    try:
                        line = input()
                        lines.append(line)
                    except EOFError:
                        break
                analysis_result = "\n".join(lines)
            else:
                analysis_result = "분석 정보 없음"
        
        # 에이전트를 통한 분석 결과 처리
        if "없음" in analysis_result and can_use_api:
            print("\n🔍 에이전트가 분석 결과를 확인하고 부족한 정보를 검색합니다...")
            
            # 부족한 정보 분석
            missing_info, business_context = agent.analyze_missing_info(analysis_result, business_idea, section_id)
            
            if missing_info:
                print(f"\n📋 다음 정보가 부족합니다:")
                for i, item in enumerate(missing_info, 1):
                    print(f"  {i}. {item['item']} - {item['explanation']}")
                
                # 검색 여부 확인
                search_api = input("\n에이전트가 이 정보를 검색하도록 할까요? (y/n): ").strip().lower() == 'y'
                
                if search_api:
                    print("\n🔎 에이전트가 관련 정보를 검색 중입니다...")
                    
                    # 검색 수행
                    search_results = agent.search_and_integrate(missing_info, business_context, section_id)
                    
                    if search_results["success"]:
                        print(f"✅ {search_results['message']}")
                        
                        # 결과 평가
                        evaluation = agent.evaluate_search_results(search_results, missing_info, section_id)
                        
                        # 통합 추천
                        recommendation = agent.create_integration_recommendation(search_results, evaluation, section_id)
                        print("\n" + recommendation)
                        
                        # 통합 여부 확인
                        use_data = input("\n이 데이터를 분석 결과에 통합할까요? (y/n): ").strip().lower() == 'y'
                        
                        if use_data:
                            # 데이터 통합
                            additional_info = f"\n\n### 에이전트가 찾은 추가 정보:\n{recommendation}"
                            enhanced_analysis = analysis_result + additional_info
                            print("✅ 에이전트가 검색한 데이터가 분석 결과에 추가되었습니다.")
                            analysis_result = enhanced_analysis
                    else:
                        print(f"❌ {search_results['message']}")
        
        # 2단계: 사업계획서 섹션 생성 프롬프트 생성
        print(f"\n2단계: 섹션 생성 - {section_title}")
        generation_prompt = generate_section_prompt(section_id, business_idea, analysis_result)
        
        if not generation_prompt:
            print(f"{section_title} 섹션을 위한 생성 프롬프트를 생성할 수 없습니다.")
            continue
        
        # 클립보드에 복사
        pyperclip.copy(generation_prompt)
        print("생성 프롬프트가 클립보드에 복사되었습니다.")
        copy_again = True
        
        while copy_again:
            print("1. Cursor AI에 붙여넣기 후 실행해주세요")
            print("2. 응답이 생성되면 복사 버튼을 클릭하세요")
            option = input("3. 복사가 완료되면 Enter를 눌러 계속하세요 (다시 복사하려면 'r' 입력): ").strip().lower()
            
            if option == 'r':
                pyperclip.copy(generation_prompt)
                print("생성 프롬프트가 클립보드에 다시 복사되었습니다.")
            else:
                copy_again = False
        
        # 클립보드에서 생성 결과 가져오기
        generation_result = pyperclip.paste()
        if not generation_result or generation_result == generation_prompt:
            print("경고: 클립보드에서 유효한 생성 결과를 가져올 수 없습니다.")
            generation_result = input("직접 생성 결과를 입력하시겠습니까? (y/n): ").strip().lower()
            if generation_result == 'y':
                print("생성 결과를 입력하세요. 입력을 마치려면 빈 줄에서 Ctrl+D (Unix) 또는 Ctrl+Z (Windows)를 입력하세요:")
                lines = []
                while True:
                    try:
                        line = input()
                        lines.append(line)
                    except EOFError:
                        break
                generation_result = "\n".join(lines)
            else:
                generation_result = "섹션 내용 없음"
        
        # 생성 결과에 API 데이터 통합
        if can_use_api and "[필요 정보:" in generation_result:
            print("\n🔍 에이전트가 생성된 내용에서 부족한 정보를 검색합니다...")
            
            # 부족한 정보 분석 - 생성 결과에서 "[필요 정보:" 패턴 추출
            missing_info_patterns = re.findall(r'\[필요 정보:[^\]]+\]', generation_result)
            
            if missing_info_patterns:
                # 가상 분석 결과 생성
                fake_analysis = "\n".join([f"항목: 없음 - {pattern[13:-1]}" for pattern in missing_info_patterns])
                
                # 부족한 정보 분석
                missing_info, business_context = agent.analyze_missing_info(fake_analysis, business_idea, section_id)
                
                if missing_info:
                    print(f"\n📋 다음 정보가 부족합니다:")
                    for i, item in enumerate(missing_info, 1):
                        print(f"  {i}. {item['item']} - {item['explanation']}")
                    
                    # 자동 검색 (에이전트 모드에서는 자동으로 검색)
                    print("\n🔎 에이전트가 관련 정보를 검색 중입니다...")
                    
                    # 검색 수행
                    search_results = agent.search_and_integrate(missing_info, business_context, section_id)
                    
                    if search_results["success"]:
                        print(f"✅ {search_results['message']}")
                        
                        # 결과 평가
                        evaluation = agent.evaluate_search_results(search_results, missing_info, section_id)
                        
                        # 생성된 내용에 데이터 통합
                        for pattern in missing_info_patterns:
                            # 데이터 요약 생성
                            data_summary = agent.data_integration.create_data_summary(
                                section_id, search_results["data"], search_results["sources"]
                            )
                            
                            # 패턴 교체
                            replacement = f"[참고 데이터: {data_summary}]"
                            generation_result = generation_result.replace(pattern, replacement)
                        
                        print("✅ 에이전트가 검색한 데이터가 생성 결과에 통합되었습니다.")
        
        # 사업계획서에 섹션 추가
        business_plan.add_section(section_id, section_title, generation_result)
        
        # 섹션 결과 저장 (디버깅용)
        section_output_path = os.path.join(output_dir, f"{section_id}_section_result.txt")
        with open(section_output_path, "w", encoding="utf-8") as f:
            f.write(generation_result)
        
        print(f"✅ {section_title} 섹션이 완료되었습니다.")
    
    # Word 문서 생성
    output_file = os.path.join(output_dir, f"{file_base_name}_business_plan.docx")
    doc_manager.create_word_document(business_plan, output_file)
    print(f"\n📄 사업계획서 Word 문서가 생성되었습니다: {output_file}")
    
    return output_file

def select_sections():
    """처리할 섹션 선택"""
    # 섹션 설정 로드
    section_config = load_section_config()
    sections = section_config.get("sections", [])
    
    if not sections:
        print("오류: 섹션 설정을 로드할 수 없습니다.")
        return []
    
    print("\n처리할 섹션을 선택하세요:")
    for i, section in enumerate(sections, 1):
        # load_section_config에서 이미 번호가 제거된 제목 사용
        print(f"{i}. {section['title']} ({section['id']})")
    print(f"{len(sections) + 1}. 모든 섹션")
    
    try:
        selected = input("번호 선택 (쉼표로 구분, 전체 선택은 '0' 또는 빈칸): ").strip()
        
        if not selected or selected == "0" or selected == str(len(sections) + 1):
            print("모든 섹션을 처리합니다.")
            return [section["id"] for section in sections]
        
        selected_indices = [int(idx.strip()) - 1 for idx in selected.split(",") if idx.strip().isdigit()]
        valid_indices = [idx for idx in selected_indices if 0 <= idx < len(sections)]
        
        if not valid_indices:
            print("유효한 섹션을 선택하지 않았습니다. 모든 섹션을 처리합니다.")
            return [section["id"] for section in sections]
        
        selected_sections = [sections[idx]["id"] for idx in valid_indices]
        print(f"선택한 섹션: {', '.join(selected_sections)}")
        return selected_sections
    
    except Exception as e:
        print(f"섹션 선택 중 오류 발생: {str(e)}")
        print("모든 섹션을 처리합니다.")
        return [section["id"] for section in sections]

def main():
    """메인 함수"""
    print(f"\n==============================")
    print(f"  비즈니스 플랜 작성 도구 v{VERSION}")
    print(f"==============================\n")
    
    # 에이전트 시스템 선택
    print("에이전트 시스템 선택:")
    print("1. 기본 에이전트 시스템 (기존)")
    print("2. OpenAI Agents SDK 기반 에이전트 시스템 (새로운 기능)")
    
    agent_choice = input("사용할 에이전트 시스템을 선택하세요 (1 또는 2): ").strip()
    use_agent_sdk = agent_choice == "2"
    
    # 출력 디렉토리 설정
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 처리할 파일 선택
    print("\n처리할 기획서 선택:")
    print("1. 단일 기획서 파일")
    print("2. 여러 기획서 파일")
    
    option = input("옵션을 선택하세요 (1 또는 2): ").strip()
    
    # 섹션 선택
    selected_sections = select_sections()
    
    if option == "1":
        # 단일 파일 처리 - 기본 경로 제공
        default_new_path = "data/proposals/business_idea.txt"
        default_legacy_path = "proposal/business_idea.txt"
        
        # 기본 경로 결정 (새 구조 우선, 없으면 레거시 경로)
        default_path = default_new_path if os.path.exists(default_new_path) else default_legacy_path
        
        file_path = input(f"\n처리할 기획서 파일 경로를 입력하세요 (기본값: {default_path}): ").strip() or default_path
        
        if not os.path.exists(file_path):
            print(f"오류: 파일을 찾을 수 없습니다: {file_path}")
            # 기본 디렉토리 생성 제안
            create_default_dir = input("기본 디렉토리를 생성할까요? (y/n): ").strip().lower() == 'y'
            if create_default_dir:
                os.makedirs(os.path.dirname(default_new_path), exist_ok=True)
                print(f"기본 디렉토리가 생성되었습니다: {os.path.dirname(default_new_path)}")
            return
        
        docx_path = process_single_proposal(file_path, output_dir, selected_sections, use_agent_sdk)
        if docx_path:
            print(f"\n✅ 사업계획서 작성이 완료되었습니다.")
        
    elif option == "2":
        # 여러 파일 처리 - 기본 디렉토리 제공
        default_new_dir = "data/proposals"
        default_legacy_dir = "proposal"
        
        # 기본 디렉토리 결정 (새 구조 우선, 없으면 레거시 경로)
        default_dir = default_new_dir if os.path.exists(default_new_dir) else default_legacy_dir
        
        directory = input(f"\n기획서 파일이 있는 디렉토리 경로를 입력하세요 (기본값: {default_dir}): ").strip() or default_dir
        
        if not os.path.isdir(directory):
            print(f"오류: 디렉토리를 찾을 수 없습니다: {directory}")
            # 기본 디렉토리 생성 제안
            create_default_dir = input("기본 디렉토리를 생성할까요? (y/n): ").strip().lower() == 'y'
            if create_default_dir:
                os.makedirs(default_new_dir, exist_ok=True)
                print(f"기본 디렉토리가 생성되었습니다: {default_new_dir}")
            return
        
        file_pattern = input("처리할 파일 패턴을 입력하세요 (예: *.txt, 기본값: *.txt): ").strip() or "*.txt"
        file_paths = glob.glob(os.path.join(directory, file_pattern))
        
        if not file_paths:
            print(f"오류: 지정한 패턴과 일치하는 파일을 찾을 수 없습니다: {file_pattern}")
            return
        
        print(f"\n{len(file_paths)}개의 파일을 처리합니다...")
        docx_paths = []
        
        for file_path in file_paths:
            docx_path = process_single_proposal(file_path, output_dir, selected_sections, use_agent_sdk)
            if docx_path:
                docx_paths.append(docx_path)
        
        if docx_paths:
            # 여러 문서 병합 여부 확인
            merge_option = input("\n모든 사업계획서를 하나의 문서로 병합하시겠습니까? (y/n): ").strip().lower()
            
            if merge_option == 'y' and len(docx_paths) > 1:
                # 병합 파일명 설정
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                merged_filename = f"merged_business_plans_{timestamp}.docx"
                merged_path = os.path.join(output_dir, merged_filename)
                
                # 문서 병합
                try:
                    merge_docx_files(docx_paths, merged_path)
                    print(f"\n✅ 병합된 사업계획서가 생성되었습니다: {merged_path}")
                    
                    # PDF 변환 확인
                    doc_manager = DocumentManager(output_dir)
                    create_pdf = input("\n병합된 문서를 PDF로 변환하시겠습니까? (y/n): ").strip().lower() == 'y'
                    if create_pdf:
                        pdf_path = doc_manager.create_pdf_from_docx(merged_path)
                        if pdf_path:
                            print(f"✅ PDF가 생성되었습니다: {pdf_path}")
                except Exception as e:
                    print(f"문서 병합 중 오류 발생: {str(e)}")
            
            print(f"\n✅ 총 {len(docx_paths)}개의 사업계획서 작성이 완료되었습니다.")
    else:
        print("잘못된 옵션입니다. 1 또는 2를 선택하세요.")

if __name__ == "__main__":
    main()