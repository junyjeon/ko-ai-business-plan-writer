import re
import logging
from typing import Dict, List, Tuple, Any, Optional
import json

from utils.api_service import APIService
from utils.data_integration import DataIntegration

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BusinessPlanAgent")

class BusinessPlanAgent:
    """
    사업계획서 작성을 지원하는 지능형 에이전트
    기획서 분석, 부족한 정보 식별, API 데이터 검색 및 통합을 처리
    """
    
    def __init__(self):
        self.api_service = APIService()
        self.data_integration = DataIntegration()
        
        # 섹션별 중요 키워드 정의
        self.section_keywords = {
            "problem": ["문제", "필요성", "시장", "현황", "니즈", "문제점", "불편함"],
            "solution": ["해결", "솔루션", "제품", "서비스", "기술", "기능", "특징"],
            "market": ["시장", "규모", "성장률", "경쟁", "타겟", "고객", "세그먼트"],
            "business_model": ["수익", "모델", "가격", "비용", "마진", "매출", "수입"],
            "competition": ["경쟁사", "경쟁자", "차별화", "포지셔닝", "우위", "비교"],
            "team": ["팀", "구성원", "창업자", "역량", "경험", "전문성", "채용"],
            "financials": ["재무", "자금", "투자", "손익", "매출", "비용", "투자금"],
            "scale_up": ["성장", "확장", "전략", "로드맵", "계획", "미래", "비전"]
        }
        
        # 정보 유형별 검색 전략
        self.search_strategies = {
            "시장 규모": self._market_size_strategy,
            "시장 트렌드": self._market_trend_strategy,
            "경쟁사": self._competitors_strategy,
            "성장률": self._growth_rate_strategy,
            "수익 모델": self._revenue_model_strategy
        }
    
    def analyze_missing_info(self, analysis_result: str, business_idea: str, section_id: str) -> Tuple[List[Dict], str]:
        """
        분석 결과에서 부족한 정보를 지능적으로 파악
        
        Args:
            analysis_result: 기획서 분석 결과 텍스트
            business_idea: 원본 기획서 텍스트
            section_id: 현재 처리 중인 섹션 ID
            
        Returns:
            missing_items: 부족한 정보 항목 목록
            context: 기획서에서 추출한 관련 컨텍스트
        """
        missing_items = []
        business_context = self._extract_business_context(business_idea)
        
        # 분석 결과에서 부족한 정보 추출
        for line in analysis_result.split('\n'):
            # "없음" 패턴 찾기
            if ("없음" in line or "부족" in line or "필요" in line) and ":" in line:
                item_name = line.split(':')[0].strip()
                explanation = line.split('-')[1].strip() if '-' in line else ""
                
                # 구체적인 정보 요구사항 추출
                specific_needs = self._extract_specific_needs(explanation)
                
                missing_items.append({
                    "item": item_name,
                    "explanation": explanation,
                    "specific_needs": specific_needs,
                    "priority": self._determine_priority(item_name, section_id)
                })
        
        # 우선순위별 정렬
        missing_items.sort(key=lambda x: x["priority"], reverse=True)
        
        return missing_items, business_context
    
    def search_and_integrate(self, missing_items: List[Dict], business_context: str, section_id: str) -> Dict:
        """
        부족한 정보에 대해 API 검색 수행 및 결과 통합
        
        Args:
            missing_items: 부족한 정보 항목 목록
            business_context: 기획서에서 추출한 컨텍스트
            section_id: 현재 처리 중인 섹션 ID
            
        Returns:
            search_results: 통합된 검색 결과
        """
        if not missing_items:
            return {"success": False, "message": "부족한 정보가 없습니다.", "data": []}
        
        # API 사용 가능 여부 확인
        api_availability = self.api_service.check_api_availability()
        if not any(api_availability.values()):
            return {
                "success": False, 
                "message": "API 키가 설정되지 않아 외부 데이터를 검색할 수 없습니다.",
                "data": []
            }
        
        # 검색 결과 저장
        search_results = {"success": True, "message": "", "data": [], "sources": []}
        
        for item in missing_items:
            # 키워드 생성
            keywords = self._generate_search_keywords(item, business_context, section_id)
            
            if not keywords:
                continue
                
            logger.info(f"'{item['item']}'에 대한 검색 키워드: {', '.join(keywords)}")
            
            # 정보 유형에 맞는 검색 전략 선택
            strategy = self._select_search_strategy(item["item"])
            
            # 검색 수행
            try:
                result = strategy(keywords, section_id, business_context)
                
                # 검색 결과가 있으면 추가
                if result["data"]:
                    search_results["data"].extend(result["data"])
                    for source in result["sources"]:
                        if source not in search_results["sources"]:
                            search_results["sources"].append(source)
            except Exception as e:
                logger.error(f"검색 중 오류 발생: {str(e)}")
                continue
        
        # 중복 데이터 제거 및 최적화
        search_results["data"] = self._optimize_search_results(search_results["data"])
        
        # 메시지 설정
        if search_results["data"]:
            search_results["message"] = f"{len(search_results['data'])}개의 관련 데이터를 찾았습니다."
        else:
            search_results["message"] = "관련 데이터를 찾을 수 없습니다."
            search_results["success"] = False
            
        return search_results
    
    def evaluate_search_results(self, search_results: Dict, missing_items: List[Dict], section_id: str) -> Dict:
        """
        검색 결과의 관련성 및 품질 평가
        
        Args:
            search_results: 검색 결과
            missing_items: 부족한 정보 항목 목록
            section_id: 현재 처리 중인 섹션 ID
            
        Returns:
            evaluation: 평가 결과 (관련성 점수 포함)
        """
        if not search_results["success"] or not search_results["data"]:
            return {"relevance": 0, "quality": 0, "completeness": 0}
        
        # 관련성 평가
        relevance_score = self._calculate_relevance(search_results["data"], missing_items, section_id)
        
        # 품질 평가
        quality_score = self._calculate_quality(search_results["data"])
        
        # 완전성 평가 (누락된 정보 중 얼마나 해결했는지)
        completeness_score = self._calculate_completeness(search_results["data"], missing_items)
        
        return {
            "relevance": relevance_score,
            "quality": quality_score,
            "completeness": completeness_score,
            "overall": (relevance_score + quality_score + completeness_score) / 3
        }
    
    def create_integration_recommendation(self, search_results: Dict, evaluation: Dict, section_id: str) -> str:
        """
        검색 결과를 사업계획서에 통합하는 방법 추천
        
        Args:
            search_results: 검색 결과
            evaluation: 평가 결과
            section_id: 현재 처리 중인 섹션 ID
            
        Returns:
            recommendation: 통합 방법 추천 텍스트
        """
        if not search_results["success"] or not search_results["data"]:
            return "적절한 데이터를 찾지 못했습니다."
        
        # 데이터 요약 생성
        summary = self.data_integration.create_data_summary(section_id, search_results["data"], search_results["sources"])
        
        # 추천 작성
        if evaluation["overall"] > 0.7:
            recommendation = f"높은 관련성(점수: {evaluation['relevance']:.2f})의 데이터를 찾았습니다. 사업계획서에 다음 정보를 통합하는 것을 강력히 권장합니다:\n\n{summary}"
        elif evaluation["overall"] > 0.4:
            recommendation = f"적절한 관련성(점수: {evaluation['relevance']:.2f})의 데이터를 찾았습니다. 다음 정보를 선택적으로 사용하세요:\n\n{summary}"
        else:
            recommendation = f"낮은 관련성(점수: {evaluation['relevance']:.2f})의 데이터만 찾을 수 있었습니다. 참고만 하시고 실제 데이터로 대체하는 것이 좋습니다:\n\n{summary}"
        
        return recommendation
    
    def _extract_business_context(self, business_idea: str) -> str:
        """기획서에서 비즈니스 컨텍스트 추출"""
        # 실제로는 더 정교한 알고리즘 사용 가능
        # 현재는 첫 300자를 가져오는 단순한 방식 사용
        max_length = min(300, len(business_idea))
        return business_idea[:max_length]
    
    def _extract_specific_needs(self, explanation: str) -> List[str]:
        """설명에서 구체적인 필요 정보 추출"""
        needs = []
        
        # "필요합니다", "필요한", "제공해야" 등의 패턴 검색
        patterns = [
            r"([^,\.]+)(필요|제공|포함|추가)[^,\.]*",
            r"([^,\.]+)(데이터|정보|수치|통계)[^,\.]*",
            r"([^,\.]+)(구체적|자세한|명확한)[^,\.]*"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, explanation)
            for match in matches:
                if match[0].strip():
                    needs.append(match[0].strip())
        
        return needs if needs else [explanation]
    
    def _determine_priority(self, item_name: str, section_id: str) -> int:
        """정보 항목의 우선순위 결정"""
        # 섹션별 우선순위 정의
        section_priorities = {
            "problem": ["시장 규모", "시장 트렌드", "고객 니즈"],
            "market": ["시장 규모", "성장률", "목표 시장"],
            "business_model": ["수익 모델", "가격 책정", "비용 구조"],
            "competition": ["경쟁사", "시장 점유율", "경쟁 우위"],
            "financials": ["초기 투자", "예상 매출", "손익 분기점"],
            "scale_up": ["성장 로드맵", "확장 전략", "투자 유치"]
        }
        
        # 해당 섹션의 우선순위 목록
        priorities = section_priorities.get(section_id, [])
        
        # 우선순위 계산
        for i, priority_item in enumerate(priorities):
            if priority_item in item_name:
                return len(priorities) - i
        
        return 0
    
    def _generate_search_keywords(self, item: Dict, business_context: str, section_id: str) -> List[str]:
        """검색 키워드 생성"""
        keywords = []
        
        # 아이템명에서 키워드 추출
        item_keywords = [k for k in re.split(r'[^a-zA-Z가-힣0-9]', item["item"]) if len(k) > 1]
        keywords.extend(item_keywords)
        
        # 섹션별 주요 키워드 추가
        section_kw = self.section_keywords.get(section_id, [])
        for kw in section_kw:
            if kw not in keywords:
                keywords.append(kw)
        
        # 기획서 컨텍스트에서 주요 단어 추출 (간단 구현)
        context_words = [w for w in re.split(r'[^a-zA-Z가-힣0-9]', business_context) if len(w) > 1]
        word_freq = {}
        
        for word in context_words:
            if word not in word_freq:
                word_freq[word] = 1
            else:
                word_freq[word] += 1
        
        # 빈도 기준 상위 단어 추가
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        for word, _ in top_words:
            if word not in keywords and len(word) > 1:
                keywords.append(word)
        
        # 필요한 경우 특정 정보 요구사항에서 키워드 추출
        for need in item["specific_needs"]:
            need_words = [w for w in re.split(r'[^a-zA-Z가-힣0-9]', need) if len(w) > 1]
            for word in need_words:
                if word not in keywords and len(word) > 1:
                    keywords.append(word)
        
        return keywords[:5]  # 너무 많은 키워드는 검색 효과를 떨어뜨릴 수 있음
    
    def _select_search_strategy(self, item_name: str):
        """아이템 이름에 따른 적절한 검색 전략 선택"""
        for key, strategy in self.search_strategies.items():
            if key in item_name:
                return strategy
        
        # 기본 전략
        return self._default_search_strategy
    
    def _default_search_strategy(self, keywords: List[str], section_id: str, context: str) -> Dict:
        """기본 검색 전략"""
        return self.api_service.search_section_data(section_id, keywords)
    
    def _market_size_strategy(self, keywords: List[str], section_id: str, context: str) -> Dict:
        """시장 규모 검색 전략"""
        # 시장 규모에 특화된 검색
        return self.api_service.search_market_data(keywords)
    
    def _market_trend_strategy(self, keywords: List[str], section_id: str, context: str) -> Dict:
        """시장 트렌드 검색 전략"""
        # 트렌드에 특화된 검색
        result = self.api_service.search_market_data(keywords)
        # 추가 소스 검색 가능
        return result
    
    def _competitors_strategy(self, keywords: List[str], section_id: str, context: str) -> Dict:
        """경쟁사 정보 검색 전략"""
        return self.api_service.search_competitors(keywords)
    
    def _growth_rate_strategy(self, keywords: List[str], section_id: str, context: str) -> Dict:
        """성장률 검색 전략"""
        return self.api_service.search_market_data(keywords)
    
    def _revenue_model_strategy(self, keywords: List[str], section_id: str, context: str) -> Dict:
        """수익 모델 검색 전략"""
        # 비즈니스 모델 관련 정보 검색
        result = self._default_search_strategy(keywords, section_id, context)
        return result
    
    def _optimize_search_results(self, data: List[Dict]) -> List[Dict]:
        """검색 결과 최적화 (중복 제거 및 정렬)"""
        if not data:
            return []
            
        # 제목으로 중복 확인
        unique_data = {}
        for item in data:
            title = item.get("title", "")
            if title and title not in unique_data:
                unique_data[title] = item
        
        # 정렬: 데이터가 있는 항목 우선, 최신 년도 우선
        return sorted(
            list(unique_data.values()),
            key=lambda x: (
                1 if x.get("value", "") else 0,
                int(x.get("year", "0")) if x.get("year", "0").isdigit() else 0
            ),
            reverse=True
        )
    
    def _calculate_relevance(self, data: List[Dict], missing_items: List[Dict], section_id: str) -> float:
        """검색 결과의 관련성 점수 계산"""
        # 단순 구현 - 실제로는 더 복잡한 알고리즘 사용 가능
        if not data or not missing_items:
            return 0.0
            
        relevance_score = 0.0
        max_score = len(missing_items)
        
        # 각 검색 결과가 누락된 정보와 얼마나 관련 있는지 확인
        for item in missing_items:
            for result in data:
                # 제목 관련성
                title = result.get("title", "").lower()
                if item["item"].lower() in title:
                    relevance_score += 1.0
                    break
                    
                # 데이터 값 관련성
                value = str(result.get("value", "")).lower()
                if any(need.lower() in value for need in item["specific_needs"]):
                    relevance_score += 0.5
                    break
        
        return relevance_score / max_score if max_score > 0 else 0.0
    
    def _calculate_quality(self, data: List[Dict]) -> float:
        """검색 결과의 품질 점수 계산"""
        if not data:
            return 0.0
            
        quality_score = 0.0
        max_score = len(data)
        
        for item in data:
            # 연도 확인 (최신 데이터일수록 높은 점수)
            year = item.get("year", "")
            if year.isdigit():
                current_year = 2023  # 실제로는 datetime으로 현재 연도 가져오기
                year_diff = current_year - int(year)
                if year_diff == 0:
                    quality_score += 1.0
                elif year_diff <= 2:
                    quality_score += 0.8
                elif year_diff <= 5:
                    quality_score += 0.5
                else:
                    quality_score += 0.3
            else:
                quality_score += 0.1
                
            # 데이터 완성도 확인
            if item.get("value", ""):
                quality_score += 0.5
                
            # 설명/성장률 등 부가 정보 확인
            if item.get("growth", "") or item.get("description", ""):
                quality_score += 0.5
        
        # 최대 점수로 정규화
        max_possible = max_score * 2.0  # 각 항목 최대 2점 가능
        return quality_score / max_possible if max_possible > 0 else 0.0
    
    def _calculate_completeness(self, data: List[Dict], missing_items: List[Dict]) -> float:
        """누락된 정보 중 얼마나 해결했는지 계산"""
        if not data or not missing_items:
            return 0.0
            
        addressed_items = set()
        
        for item in missing_items:
            for result in data:
                title = result.get("title", "").lower()
                if item["item"].lower() in title or any(need.lower() in title for need in item["specific_needs"]):
                    addressed_items.add(item["item"])
                    break
        
        return len(addressed_items) / len(missing_items) 