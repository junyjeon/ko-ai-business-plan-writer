"""
사업계획서 모델 및 핵심 비즈니스 로직
"""

class BusinessPlan:
    """
    사업계획서를 나타내는 클래스
    """
    def __init__(self, title="", business_idea=""):
        self.title = title
        self.business_idea = business_idea
        self.sections = {
            "problem": "",
            "solution": "",
            "market": "",
            "business_model": "",
            "competition": "",
            "team": "",
            "financials": "",
            "scale_up": ""
        }
    
    def add_section_content(self, section_name, content):
        """
        특정 섹션에 내용을 추가합니다
        """
        if section_name in self.sections:
            self.sections[section_name] = content
            return True
        return False
    
    def add_section(self, section_id, section_title=None, content=""):
        """
        섹션에 내용을 추가합니다 (add_section_content의 별칭)
        section_title 매개변수는 호환성을 위해 존재하지만 사용되지 않습니다
        """
        return self.add_section_content(section_id, content)
    
    def get_section_content(self, section_name):
        """
        특정 섹션의 내용을 반환합니다
        """
        return self.sections.get(section_name, "")
    
    def get_completed_sections(self):
        """
        작성 완료된 섹션 목록을 반환합니다
        """
        return [section for section, content in self.sections.items() if content]
    
    def is_complete(self):
        """
        모든 필수 섹션이 작성되었는지 확인합니다
        """
        essential_sections = ["problem", "solution", "market", "business_model"]
        return all(self.sections[section] for section in essential_sections)


class BusinessPlanService:
    """
    사업계획서 생성 및 관리를 위한 서비스 클래스
    """
    def __init__(self):
        self.current_plan = None
    
    def create_plan(self, title, business_idea):
        """
        새 사업계획서를 생성합니다
        """
        self.current_plan = BusinessPlan(title, business_idea)
        return self.current_plan
    
    def load_business_idea(self, file_path):
        """
        파일에서 사업 아이디어를 로드합니다
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                business_idea = f.read()
            return business_idea
        except Exception as e:
            print(f"사업 아이디어 로드 중 오류 발생: {str(e)}")
            return "" 