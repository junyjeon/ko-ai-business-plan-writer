"""
문서 처리 및 관리를 위한 서비스
"""
import os
import sys

# utils 폴더를 import 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from utils import pdf_utils
from utils.pdf_utils import merge_docx_files  # merge_docx_files 함수 명시적으로 가져오기


class DocumentManager:
    """
    문서 생성 및 관리를 담당하는 클래스
    """
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_document_from_sections(self, business_plan, output_filename="business_plan.docx"):
        """
        사업계획서 객체로부터 Word 문서를 생성합니다
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        # sections 사전에서 내용 추출
        completed_sections = {}
        for section_name, content in business_plan.sections.items():
            if content:  # 내용이 있는 섹션만 포함
                # 섹션 이름을 더 읽기 쉬운 형식으로 변환
                section_title = section_name.replace('_', ' ').title()
                completed_sections[section_title] = content
        
        # Word 문서 생성
        try:
            pdf_utils.create_docx_with_sections(output_path, completed_sections)
            print(f"문서가 성공적으로 생성되었습니다: {output_path}")
            return output_path
        except Exception as e:
            print(f"문서 생성 중 오류 발생: {str(e)}")
            return None
    
    # create_word_document를 create_document_from_sections의 별칭으로 추가
    def create_word_document(self, business_plan, output_filename="business_plan.docx"):
        """
        사업계획서 객체로부터 Word 문서를 생성합니다 (create_document_from_sections의 별칭)
        """
        return self.create_document_from_sections(business_plan, output_filename)
    
    def create_pdf_from_docx(self, docx_path):
        """
        Word 문서를 PDF로 변환합니다
        """
        try:
            pdf_path = docx_path.replace('.docx', '.pdf')
            pdf_utils.convert_docx_to_pdf(docx_path, pdf_path)
            print(f"PDF가 성공적으로 생성되었습니다: {pdf_path}")
            return pdf_path
        except Exception as e:
            print(f"PDF 변환 중 오류 발생: {str(e)}")
            return None 