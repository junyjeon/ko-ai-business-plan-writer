#!/usr/bin/env python
"""
사업계획서 작성 워크플로우 테스트 스크립트
"""
import os
import sys
import unittest
from pathlib import Path

# 상위 디렉토리를 import 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from core.business_plan import BusinessPlanService, BusinessPlan
from core.document_manager import DocumentManager
from utils.prompt_utils import load_prompt_template


class TestBusinessPlanFlow(unittest.TestCase):
    """사업계획서 작성 워크플로우 테스트"""
    
    def setUp(self):
        """테스트 환경 설정"""
        self.test_output_dir = os.path.join(current_dir, "test_output")
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # 테스트용 기획서 경로
        self.test_proposal_path = os.path.join(parent_dir, "data", "proposals", "business_idea.txt")
        if not os.path.exists(self.test_proposal_path):
            self.test_proposal_path = os.path.join(parent_dir, "proposal", "business_idea.txt")
    
    def test_business_plan_creation(self):
        """사업계획서 모델 생성 테스트"""
        bp = BusinessPlan("테스트 사업계획서", "테스트 내용")
        self.assertEqual(bp.title, "테스트 사업계획서")
        self.assertEqual(bp.business_idea, "테스트 내용")
        self.assertEqual(len(bp.sections), 8)  # 8개 섹션 확인
    
    def test_prompt_templates(self):
        """프롬프트 템플릿 로드 테스트"""
        # 분석 프롬프트 템플릿
        analysis_template_path = os.path.join(parent_dir, "data", "prompts", "analysis_prompt.txt")
        if not os.path.exists(analysis_template_path):
            analysis_template_path = os.path.join(parent_dir, "prompts", "analysis_prompt.txt")
        
        template = load_prompt_template(analysis_template_path)
        self.assertIsNotNone(template)
        self.assertIn("{business_idea}", template)
    
    def test_business_idea_loading(self):
        """기획서 로드 테스트"""
        if not os.path.exists(self.test_proposal_path):
            self.skipTest(f"테스트 기획서 파일이 없습니다: {self.test_proposal_path}")
            return
        
        bp_service = BusinessPlanService()
        business_idea = bp_service.load_business_idea(self.test_proposal_path)
        self.assertIsNotNone(business_idea)
        self.assertGreater(len(business_idea), 0)
    
    def test_document_creation(self):
        """문서 생성 테스트"""
        # 비즈니스 플랜 생성
        bp_service = BusinessPlanService()
        business_plan = bp_service.create_plan("테스트 계획", "테스트 아이디어")
        
        # 섹션 내용 추가
        business_plan.add_section_content("problem", "이것은 문제 인식 섹션 테스트입니다.")
        
        # 문서 생성
        doc_manager = DocumentManager(self.test_output_dir)
        output_path = doc_manager.create_document_from_sections(
            business_plan, 
            "test_document.docx"
        )
        
        # 파일 생성 확인
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)


def run_tests():
    """모든 테스트 실행"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBusinessPlanFlow)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    run_tests() 