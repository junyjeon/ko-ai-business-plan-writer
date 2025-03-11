import os
import sys
import glob
import json

# utils 폴더 및 core 폴더를 import 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 새로운 구조의 모듈 import
from utils.prompt_utils import generate_analysis_prompt, generate_section_prompt
from utils.prompt_utils import load_section_config
from utils.pdf_utils import merge_docx_files
from core.business_plan import BusinessPlanService
from core.document_manager import DocumentManager

def process_single_proposal(file_path, output_dir, selected_sections):
    """단일 기획서 처리"""
    file_name = os.path.basename(file_path)
    file_base_name = os.path.splitext(file_name)[0]
    
    print(f"\n===== 기획서 처리 중: {file_name} =====")
    
    # 서비스 인스턴스 생성
    bp_service = BusinessPlanService()
    doc_manager = DocumentManager(output_dir)
    
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
    
    # 선택된 모든 섹션 처리
    for section in sections_to_process:
        section_id = section["id"]
        section_title = section["title"]
        
        print(f"\n===== {section_title} 섹션 처리 중 =====")
        
        # 1단계: 분석 프롬프트 생성 및 결과 가져오기
        print(f"\n1단계: 기획서 분석 - {section_title}")
        analysis = generate_analysis_prompt(section_id, business_idea)
        
        if not analysis:
            print(f"{section_id} 섹션 분석에 실패했습니다. 이 섹션은 건너뜁니다.")
            continue
            
        print(f"\n분석 프롬프트가 클립보드에 복사되었습니다.")
        print("1. Cursor AI에 붙여넣기 후 실행해주세요")
        print("2. 응답이 생성되면 복사 버튼을 클릭하세요")
        print("3. 복사가 완료되면 Enter를 눌러 계속하세요...")
        input()  # 사용자 입력 대기
        
        analysis_result = input("분석 결과를 붙여넣으세요: ")
        print(f"\n분석 결과를 성공적으로 가져왔습니다. (길이: {len(analysis_result)} 자)")
        
        # 2단계: 섹션 작성 프롬프트 생성 및 결과 가져오기
        print(f"\n2단계: {section_title} 섹션 작성")
        section_prompt = generate_section_prompt(section_id, business_idea, analysis_result)
        
        if not section_prompt:
            print(f"{section_id} 섹션 생성에 실패했습니다. 이 섹션은 건너뜁니다.")
            continue
            
        print(f"\n섹션 작성 프롬프트가 클립보드에 복사되었습니다.")
        print("1. Cursor AI에 붙여넣기 후 실행해주세요")
        print("2. 응답이 생성되면 복사 버튼을 클릭하세요")
        print("3. 복사가 완료되면 Enter를 눌러 계속하세요...")
        input()  # 사용자 입력 대기
        
        section_content = input("섹션 작성 결과를 붙여넣으세요: ")
        print(f"\n섹션 작성 결과를 성공적으로 가져왔습니다. (길이: {len(section_content)} 자)")
        
        # 사업계획서 객체에 섹션 내용 추가
        business_plan.add_section_content(section_id, section_content)
    
    # 모든 섹션이 처리된 후 결과 저장
    if not business_plan.get_completed_sections():
        print("처리된 섹션이 없습니다.")
        return None
    
    # 3단계: 결과 저장
    output_docx = os.path.join(output_dir, f"{file_base_name}_business_plan.docx")
    
    # 문서 관리자를 통해 Word 문서 생성
    doc_manager.create_document_from_sections(business_plan, f"{file_base_name}_business_plan.docx")
    print(f"Word 문서가 생성되었습니다: {output_docx}")
    
    # PDF 템플릿이 있는 경우 PDF도 생성
    legacy_template_pdf = os.path.join("templates", "template.pdf")
    new_template_pdf = os.path.join("data", "templates", "template.pdf")
    
    # 템플릿 파일 경로 결정 (새 구조 또는 레거시 경로)
    template_pdf = new_template_pdf if os.path.exists(new_template_pdf) else legacy_template_pdf
    
    if os.path.exists(template_pdf):
        output_pdf = os.path.join(output_dir, f"{file_base_name}_business_plan.pdf")
        try:
            # PDF 변환 시도 (미구현 기능을 위한 안내만 제공)
            doc_manager.create_pdf_from_docx(output_docx)
        except Exception as e:
            print(f"PDF 생성 중 오류 발생: {str(e)}")
    
    return output_docx

def select_sections():
    """처리할 섹션 선택"""
    section_config = load_section_config()
    sections = section_config.get("sections", [])
    
    if not sections:
        print("설정된 섹션이 없습니다.")
        return []
    
    print("\n처리할 섹션을 선택하세요:")
    for i, section in enumerate(sections, 1):
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
    print("\n===== 예비창업패키지 사업계획서 작성 도우미 =====")
    print("Version 2.0.0 - 다중 섹션 지원")
    
    # 출력 디렉토리 확인
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 처리할 섹션 선택
    selected_sections = select_sections()
    
    # 입력 방식 선택
    print("\n기획서 입력 방식을 선택하세요:")
    print("1. 단일 파일")
    print("2. 디렉토리 내 모든 .txt 파일")
    print("3. 여러 파일 지정")
    
    option = input("선택 (기본값: 1): ").strip() or "1"
    
    if option == "1":
        # 단일 파일 처리 - 새 구조(data/proposals)와 레거시 구조(proposal) 모두 지원
        default_new_path = os.path.join("data", "proposals", "business_idea.txt")
        default_legacy_path = os.path.join("proposal", "business_idea.txt")
        
        # 기본 경로 결정 (새 구조 우선, 없으면 레거시 경로)
        default_path = default_new_path if os.path.exists(default_new_path) else default_legacy_path
        
        file_path = input(f"기획서 파일 경로 (기본값: {default_path}): ").strip() or default_path
        
        if not os.path.exists(file_path):
            print(f"오류: {file_path} 파일이 존재하지 않습니다.")
            return
        
        process_single_proposal(file_path, output_dir, selected_sections)
        
    elif option == "2":
        # 디렉토리 내 모든 .txt 파일 처리
        default_new_dir = "data/proposals"
        default_legacy_dir = "proposal"
        
        # 기본 디렉토리 결정 (새 구조 우선, 없으면 레거시 경로)
        default_dir = default_new_dir if os.path.exists(default_new_dir) else default_legacy_dir
        
        dir_path = input(f"기획서 디렉토리 경로 (기본값: {default_dir}): ").strip() or default_dir
        
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            print(f"오류: {dir_path} 디렉토리가 존재하지 않습니다.")
            return
        
        txt_files = glob.glob(os.path.join(dir_path, "*.txt"))
        if not txt_files:
            print(f"오류: {dir_path} 디렉토리에 .txt 파일이 없습니다.")
            return
        
        print(f"{len(txt_files)}개의 기획서 파일을 찾았습니다.")
        
        # 모든 파일 처리
        output_files = []
        for file_path in txt_files:
            output_file = process_single_proposal(file_path, output_dir, selected_sections)
            if output_file:
                output_files.append(output_file)
        
        # 통합 문서 생성 여부
        if len(output_files) > 1 and input("모든 결과를 하나의 문서로 통합하시겠습니까? (y/n): ").strip().lower() == 'y':
            combined_output = os.path.join(output_dir, "combined_business_plan.docx")
            merge_docx_files(output_files, combined_output)
            print(f"통합 문서가 생성되었습니다: {combined_output}")
        
    elif option == "3":
        # 여러 파일 지정
        files_input = input("기획서 파일 경로를 쉼표로 구분하여 입력하세요: ").strip()
        file_paths = [path.strip() for path in files_input.split(",")]
        
        valid_files = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                valid_files.append(file_path)
            else:
                print(f"오류: {file_path} 파일이 존재하지 않습니다.")
        
        if not valid_files:
            print("유효한 파일이 없습니다.")
            return
        
        print(f"{len(valid_files)}개의 유효한 기획서 파일을 찾았습니다.")
        
        # 모든 파일 처리
        output_files = []
        for file_path in valid_files:
            output_file = process_single_proposal(file_path, output_dir, selected_sections)
            if output_file:
                output_files.append(output_file)
        
        # 통합 문서 생성 여부
        if len(output_files) > 1 and input("모든 결과를 하나의 문서로 통합하시겠습니까? (y/n): ").strip().lower() == 'y':
            combined_output = os.path.join(output_dir, "combined_business_plan.docx")
            merge_docx_files(output_files, combined_output)
            print(f"통합 문서가 생성되었습니다: {combined_output}")
    
    else:
        print("잘못된 옵션입니다.")
        return
    
    print("\n모든 작업이 완료되었습니다!")

if __name__ == "__main__":
    main()