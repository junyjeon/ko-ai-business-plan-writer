import os
import sys
import glob

# utils 폴더 및 core 폴더를 import 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 새로운 구조의 모듈 import
from utils.prompt_utils import generate_problem_analysis_prompt, generate_problem_section_prompt
from utils.pdf_utils import insert_text_to_pdf, create_docx_with_section, merge_docx_files
from core.business_plan import BusinessPlanService
from core.document_manager import DocumentManager

def read_business_idea(file_path):
    """기획서 파일 읽기"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"기획서 파일 읽기 오류: {str(e)}")
        return None

def process_single_proposal(file_path, output_dir):
    """단일 기획서 처리"""
    file_name = os.path.basename(file_path)
    file_base_name = os.path.splitext(file_name)[0]
    
    print(f"\n===== 기획서 처리 중: {file_name} =====")
    
    # 기획서 읽기
    business_idea = read_business_idea(file_path)
    if not business_idea:
        print(f"{file_path} 파일을 읽을 수 없습니다. 이 파일은 건너뜁니다.")
        return None
    
    print(f"기획서를 성공적으로 읽었습니다. (길이: {len(business_idea)} 자)")
    
    # 1단계: 분석 프롬프트 생성 및 결과 가져오기
    print(f"\n===== 1단계: 기획서 분석 - {file_name} =====")
    analysis = generate_problem_analysis_prompt(business_idea)
    
    # 2단계: 섹션 작성 프롬프트 생성 및 결과 가져오기
    print(f"\n===== 2단계: 문제 인식 섹션 작성 - {file_name} =====")
    problem_section = generate_problem_section_prompt(business_idea, analysis)
    
    # 3단계: 결과 저장
    output_docx = os.path.join(output_dir, f"{file_base_name}_problem_section.docx")
    create_docx_with_section(problem_section, output_docx, title=f"문제 인식 (Problem) - {file_base_name}")
    print(f"Word 문서가 생성되었습니다: {output_docx}")
    
    # PDF 템플릿이 있는 경우 PDF도 생성
    template_pdf = os.path.join("templates", "template.pdf")
    if os.path.exists(template_pdf):
        output_pdf = os.path.join(output_dir, f"{file_base_name}_business_plan.pdf")
        position = (0, 50, 700)  # 첫 번째 페이지, x=50, y=700
        
        try:
            insert_text_to_pdf(template_pdf, output_pdf, problem_section, position)
            print(f"PDF 문서가 생성되었습니다: {output_pdf}")
        except Exception as e:
            print(f"PDF 생성 중 오류 발생: {str(e)}")
    
    return output_docx

def main():
    print("\n===== 예비창업패키지 사업계획서 작성 도우미 =====")
    print("Version 1.0.0 - 단일 책임 원칙 적용된 구조")
    
    # 출력 디렉토리 확인
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 입력 방식 선택
    print("\n기획서 입력 방식을 선택하세요:")
    print("1. 단일 파일")
    print("2. 디렉토리 내 모든 .txt 파일")
    print("3. 여러 파일 지정")
    
    option = input("선택 (기본값: 1): ").strip() or "1"
    
    if option == "1":
        # 단일 파일 처리
        default_path = os.path.join("proposal", "business_idea.txt")
        file_path = input(f"기획서 파일 경로 (기본값: {default_path}): ").strip() or default_path
        
        if not os.path.exists(file_path):
            print(f"오류: {file_path} 파일이 존재하지 않습니다.")
            return
        
        process_single_proposal(file_path, output_dir)
        
    elif option == "2":
        # 디렉토리 내 모든 .txt 파일 처리
        default_dir = "proposal"
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
            output_file = process_single_proposal(file_path, output_dir)
            if output_file:
                output_files.append(output_file)
        
        # 통합 문서 생성 여부
        if len(output_files) > 1 and input("모든 결과를 하나의 문서로 통합하시겠습니까? (y/n): ").strip().lower() == 'y':
            combined_output = os.path.join(output_dir, "combined_problem_sections.docx")
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
            output_file = process_single_proposal(file_path, output_dir)
            if output_file:
                output_files.append(output_file)
        
        # 통합 문서 생성 여부
        if len(output_files) > 1 and input("모든 결과를 하나의 문서로 통합하시겠습니까? (y/n): ").strip().lower() == 'y':
            combined_output = os.path.join(output_dir, "combined_problem_sections.docx")
            merge_docx_files(output_files, combined_output)
            print(f"통합 문서가 생성되었습니다: {combined_output}")
    
    else:
        print("잘못된 옵션입니다.")
        return
    
    print("\n모든 작업이 완료되었습니다!")

if __name__ == "__main__":
    main()