"""
OpenAI Agents SDK를 사용한 비즈니스 플랜 작성 시스템
"""
import os
import json
import asyncio
from typing import List, Dict, Any, Optional

from agents import Agent, Runner, function_tool
from utils.api_service import APIService

class BusinessPlanAgentSystem:
    """
    OpenAI Agents SDK를 활용한 비즈니스 플랜 에이전트 시스템
    """
    def __init__(self, config_path="data/prompts/section_config.json"):
        self.api_service = APIService()
        self.config_path = config_path
        self.sections_config = self._load_sections_config()
        
        # 에이전트 초기화
        self.analyzer_agent = self._create_analyzer_agent()
        self.search_agent = self._create_search_agent()
        self.section_agents = self._create_section_agents()
        self.coordinator_agent = self._create_coordinator_agent()
    
    def _load_sections_config(self) -> Dict[str, Any]:
        """섹션 설정 파일 로드"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_prompt_from_file(self, filename: str) -> str:
        """프롬프트 파일 로드"""
        prompt_path = f"data/prompts/{filename}"
        if not os.path.exists(prompt_path):
            if filename.startswith("generation_prompts/"):
                os.makedirs("data/prompts/generation_prompts", exist_ok=True)
            elif filename.startswith("analysis_prompts/"):
                os.makedirs("data/prompts/analysis_prompts", exist_ok=True)
            return ""  # 파일이 없으면 빈 문자열 반환
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _create_analyzer_agent(self) -> Agent:
        """분석 에이전트 생성"""
        instructions = self._load_prompt_from_file("analysis_prompts/analyzer_agent.txt")
        if not instructions:
            instructions = """
            당신은 비즈니스 플랜 분석 전문가입니다.
            사용자가 제공한 비즈니스 플랜 초안을 분석하고, 다음을 수행하세요:
            1. 필수 정보가 누락된 부분 식별
            2. 논리적 오류나 불일치 지적
            3. 개선이 필요한 영역 제안
            4. 각 섹션별 필수 요소가 포함되었는지 확인
            
            분석 결과는 구체적이고 실행 가능한 제안으로 제공하세요.
            """
        
        @function_tool
        def analyze_business_plan(plan_text: str) -> Dict[str, Any]:
            """
            비즈니스 플랜을 분석하여 누락된 정보와 개선점 식별
            """
            analysis = {
                "missing_info": [],
                "improvements": [],
                "section_analysis": {}
            }
            
            # 각 섹션별 키워드 정의
            section_keywords = {
                "problem": ["문제", "고객 페인 포인트", "필요성", "시장 현황"],
                "solution": ["제품", "서비스", "해결 방안", "기술", "특징"],
                "market": ["시장 규모", "TAM", "SAM", "SOM", "성장률", "타겟 시장"],
                "business_model": ["수익 모델", "가격", "비용 구조", "마진", "수익성"],
                "competition": ["경쟁사", "차별점", "경쟁 우위", "진입 장벽"],
                "team": ["팀원", "역량", "경험", "전문성"],
                "financials": ["매출", "비용", "손익", "투자", "ROI"],
                "scale_up": ["성장 전략", "확장성", "로드맵"]
            }
            
            for section in self.sections_config.get("sections", []):
                section_id = section.get("id")
                section_title = section.get("title")
                required_elements = section.get("required_elements", [])
                
                if isinstance(required_elements[0], dict) if required_elements else False:
                    element_names = [element.get('name', '') for element in required_elements]
                else:
                    element_names = required_elements
                
                # 섹션별 키워드 검출 및 점수 계산
                keyword_count = 0
                total_keywords = len(section_keywords.get(section_id, []))
                if total_keywords > 0:
                    for keyword in section_keywords.get(section_id, []):
                        if keyword.lower() in plan_text.lower():
                            keyword_count += 1
                    
                    completeness = min(1.0, keyword_count / total_keywords)
                else:
                    completeness = 0.5  # 기본값
                
                # 누락된 요소 식별
                missing = []
                for element in element_names:
                    element_keywords = element.lower().split()
                    found = False
                    for keyword in element_keywords:
                        if len(keyword) > 3 and keyword in plan_text.lower():
                            found = True
                            break
                    
                    if not found:
                        missing.append(element)
                
                # 섹션 분석 저장
                analysis["section_analysis"][section_id] = {
                    "title": section_title,
                    "completeness": completeness,
                    "missing_elements": missing,
                    "suggestions": [
                        f"{element}에 대한 구체적인 정보 추가 필요" for element in missing
                    ] if missing else ["섹션 완성도 높음"]
                }
                
                # 전체 분석에 추가
                if missing:
                    analysis["missing_info"].append(f"{section_title}에서 {', '.join(missing)}에 대한 정보 필요")
            
            return analysis
        
        return Agent(
            name="비즈니스 플랜 분석가",
            instructions=instructions,
            tools=[analyze_business_plan]
        )
    
    def _create_search_agent(self) -> Agent:
        """검색 에이전트 생성"""
        instructions = self._load_prompt_from_file("analysis_prompts/search_agent.txt")
        if not instructions:
            instructions = """
            당신은 비즈니스 데이터 검색 전문가입니다.
            분석 결과에서 누락된 정보를 식별하고, 관련 데이터를 검색하세요:
            1. 시장 규모, 경쟁사, 산업 동향 등의 정보 검색
            2. 검색 결과를 비즈니스 플랜 컨텍스트에 맞게 요약
            3. 정보의 신뢰성과 관련성 평가
            4. 비즈니스 플랜 개선을 위한 데이터 통합 방법 제안
            
            검색 결과는 출처와 함께 제공하고, 비즈니스 플랜에 직접 통합할 수 있는 형태로 정리하세요.
            """
        
        @function_tool
        def search_market_data(query: str) -> Dict[str, Any]:
            """
            시장 데이터 검색 및 요약
            """
            # 실제 구현에서는 APIService를 사용하여 외부 데이터 검색
            search_results = self.api_service.search_information(query)
            return {
                "query": query,
                "results": search_results,
                "summary": f"{query}에 대한 검색 결과 요약"
            }
        
        return Agent(
            name="비즈니스 데이터 검색가",
            instructions=instructions,
            tools=[search_market_data]
        )
    
    def _create_section_agents(self) -> Dict[str, Agent]:
        """각 섹션별 작성 에이전트 생성"""
        section_agents = {}
        
        for section in self.sections_config.get("sections", []):
            section_id = section.get("id")
            section_title = section.get("title")
            prompt_file = f"generation_prompts/{section_id}_agent.txt"
            instructions = self._load_prompt_from_file(prompt_file)
            
            if not instructions:
                # required_elements가 딕셔너리 목록인 경우 name 필드만 추출
                required_elements = section.get('required_elements', [])
                element_names = []
                
                if required_elements and isinstance(required_elements[0], dict):
                    element_names = [element.get('name', '') for element in required_elements]
                else:
                    element_names = required_elements
                
                instructions = f"""
                당신은 비즈니스 플랜의 {section_title} 섹션 작성 전문가입니다.
                이 섹션에 필요한 모든 요소를 포함하여 고품질 콘텐츠를 작성하세요:
                
                1. 이 섹션에서 다뤄야 할 핵심 요소: {', '.join(element_names)}
                2. 작성 시 고려해야 할 지침: {section.get('guidelines', '지침 없음')}
                3. 이 섹션의 목적: {section.get('purpose', '목적 정보 없음')}
                
                분석 결과와 검색 데이터를 활용하여 완성도 높은 섹션을 작성하세요.
                """
            
            section_agents[section_id] = Agent(
                name=f"{section_title} 작성 전문가",
                instructions=instructions
            )
        
        return section_agents
    
    def _create_coordinator_agent(self) -> Agent:
        """조율 에이전트 생성"""
        instructions = self._load_prompt_from_file("coordinator_agent.txt")
        if not instructions:
            instructions = """
            당신은 비즈니스 플랜 작성 프로세스의 조율자입니다.
            전체 작업 흐름을 관리하고 다음을 수행하세요:
            
            1. 사용자 요청 분석 및 필요한 섹션 결정
            2. 분석 에이전트에 초기 계획 전달 및 결과 수신
            3. 검색 에이전트에 누락 정보 검색 요청
            4. 각 섹션 에이전트에 작업 분배 및 결과 통합
            5. 최종 비즈니스 플랜 구성 및 일관성 확인
            
            각 에이전트의 결과물을 효과적으로 조율하여 통합된 고품질 비즈니스 플랜을 생성하세요.
            """
        
        # 모든 에이전트 핸드오프 리스트 생성
        handoffs = [self.analyzer_agent, self.search_agent]
        handoffs.extend(list(self.section_agents.values()))
        
        return Agent(
            name="비즈니스 플랜 조율자",
            instructions=instructions,
            handoffs=handoffs
        )
    
    async def process_business_plan(self, input_text: str, selected_sections: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        비즈니스 플랜 처리 주 함수
        """
        # 선택된 섹션이 없으면 모든 섹션 사용
        if not selected_sections:
            selected_sections = [section.get("id") for section in self.sections_config.get("sections", [])]
        
        # 조율 에이전트에 초기 요청 전송
        input_message = {
            "business_plan_draft": input_text,
            "selected_sections": selected_sections
        }
        
        # 에이전트 실행
        result = await Runner.run(
            self.coordinator_agent, 
            input=json.dumps(input_message),
            max_turns=20
        )
        
        # 결과 처리 및 반환
        return {
            "final_output": result.final_output,
            "sections": self._extract_sections_from_output(result.final_output)
        }
    
    def _extract_sections_from_output(self, output: str) -> Dict[str, str]:
        """
        최종 출력에서 각 섹션 내용 추출
        """
        sections = {}
        current_section = None
        current_content = []
        
        for line in output.split('\n'):
            # 섹션 제목 식별을 위한 간단한 휴리스틱
            # 실제 구현에서는 더 정교한 파싱 로직 필요
            if line.startswith('# ') or line.startswith('## '):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                    current_content = []
                
                current_section = line.lstrip('#').strip()
            elif current_section:
                current_content.append(line)
        
        # 마지막 섹션 처리
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def run(self, input_text: str, selected_sections: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        동기식 인터페이스 (main.py에서 호출하기 쉽게)
        """
        return asyncio.run(self.process_business_plan(input_text, selected_sections))
    
    def run_with_mode(self, input_text: str, mode: str = "analyze", selected_sections: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        다양한 모드로 입력 처리
        
        Args:
            input_text: 원본 기획서 텍스트
            mode: "raw" (원본 그대로), "summarize" (요약) 또는 "analyze" (분석)
            selected_sections: 처리할 섹션 목록
            
        Returns:
            처리된 결과
        """
        if mode == "raw" or mode == "summarize":
            return asyncio.run(self.process_proposal_content(input_text, mode))
        else:
            return asyncio.run(self.process_business_plan(input_text, selected_sections))
    
    async def process_proposal_content(self, input_text: str, mode: str = "summarize") -> Dict[str, Any]:
        """
        proposals 내용 처리
        
        Args:
            input_text: 원본 기획서 텍스트
            mode: "raw" (원본 그대로) 또는 "summarize" (요약)
        
        Returns:
            처리된 결과
        """
        if mode == "raw":
            # 원본 내용 그대로 반환
            return {
                "final_output": input_text,
                "sections": self._extract_sections_from_output(input_text)
            }
        
        # 요약 모드: Agent를 사용하여 내용 요약
        instructions = """
        당신은 비즈니스 기획서 요약 전문가입니다. 
        제공된 기획서 텍스트를 분석하고, 핵심 내용을 누락 없이 요약해주세요.
        원본의 주요 아이디어, 비즈니스 모델, 시장 분석, 차별점 등 중요 정보를 
        모두 포함해야 합니다.
        요약은 원본의 구조를 유지하되, 간결하게 작성해주세요.
        """
        
        summarizer_agent = Agent(
            name="기획서 요약가",
            instructions=instructions
        )
        
        result = await Runner.run(
            summarizer_agent,
            input=input_text,
            max_turns=3
        )
        
        return {
            "final_output": result.final_output,
            "sections": self._extract_sections_from_output(result.final_output)
        } 