import requests
import json
import os
import logging
from typing import Dict, List, Optional, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("APIService")

class APIService:
    """
    다양한 한국 데이터 API를 활용하여 사업계획서에 필요한 정보를 검색하는 서비스
    """
    
    def __init__(self):
        # API 키 로드 (환경 변수 또는 설정 파일에서)
        self.config = self._load_api_config()
        
    def _load_api_config(self) -> Dict:
        """API 설정 파일 로드"""
        config_path = os.path.join("config", "api_keys.json")
        
        # 설정 파일이 없는 경우 기본값 사용
        if not os.path.exists(config_path):
            # 설정 디렉토리 생성
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # 기본 설정 파일 생성
            default_config = {
                "public_data_portal": {
                    "api_key": "",
                    "base_url": "https://www.data.go.kr/api"
                },
                "kisti": {
                    "api_key": "",
                    "base_url": "https://api.kisti.re.kr"
                },
                "kosis": {
                    "api_key": "",
                    "base_url": "https://kosis.kr/openapi"
                },
                "ecos": {
                    "api_key": "",
                    "base_url": "https://ecos.bok.or.kr/api"
                }
            }
            
            # 기본 설정 파일 저장
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            
            logger.warning(f"API 설정 파일이 없습니다. 기본 설정 파일을 생성했습니다: {config_path}")
            logger.warning("API 기능을 사용하려면 API 키를 설정 파일에 입력하세요.")
            
            return default_config
        
        # 설정 파일 로드
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"API 설정 파일 로드 중 오류 발생: {str(e)}")
            return {}
    
    def check_api_availability(self) -> Dict[str, bool]:
        """사용 가능한 API 서비스 확인"""
        availability = {}
        
        for api_name, api_config in self.config.items():
            if api_config.get("api_key"):
                availability[api_name] = True
            else:
                availability[api_name] = False
        
        return availability
    
    def search_market_data(self, keywords: List[str], industry_code: Optional[str] = None) -> Dict:
        """
        시장 데이터 검색 (시장 규모, 성장률 등)
        주로 통계청 KOSIS API 사용
        """
        results = {"data": [], "sources": []}
        
        # API 사용 가능 여부 확인
        availability = self.check_api_availability()
        
        # KOSIS API 사용 (통계청)
        if availability.get("kosis"):
            try:
                kosis_results = self._search_kosis(keywords, industry_code)
                if kosis_results:
                    results["data"].extend(kosis_results["data"])
                    results["sources"].append("통계청 KOSIS")
            except Exception as e:
                logger.error(f"KOSIS API 검색 중 오류 발생: {str(e)}")
        
        # 공공데이터 포털 API 사용
        if availability.get("public_data_portal"):
            try:
                public_data_results = self._search_public_data_portal(keywords, "market")
                if public_data_results:
                    results["data"].extend(public_data_results["data"])
                    results["sources"].append("공공데이터 포털")
            except Exception as e:
                logger.error(f"공공데이터 포털 API 검색 중 오류 발생: {str(e)}")
        
        return results
    
    def search_competitors(self, keywords: List[str], industry_code: Optional[str] = None) -> Dict:
        """
        경쟁사 정보 검색
        주로 KISTI API 활용
        """
        results = {"data": [], "sources": []}
        
        # API 사용 가능 여부 확인
        availability = self.check_api_availability()
        
        # KISTI API 사용
        if availability.get("kisti"):
            try:
                kisti_results = self._search_kisti(keywords, "competitors")
                if kisti_results:
                    results["data"].extend(kisti_results["data"])
                    results["sources"].append("KISTI")
            except Exception as e:
                logger.error(f"KISTI API 검색 중 오류 발생: {str(e)}")
        
        return results
    
    def search_economic_indicators(self, keywords: List[str]) -> Dict:
        """
        경제 지표 검색 (GDP, 물가, 금리 등)
        주로 한국은행 ECOS API 사용
        """
        results = {"data": [], "sources": []}
        
        # API 사용 가능 여부 확인
        availability = self.check_api_availability()
        
        # ECOS API 사용 (한국은행)
        if availability.get("ecos"):
            try:
                ecos_results = self._search_ecos(keywords)
                if ecos_results:
                    results["data"].extend(ecos_results["data"])
                    results["sources"].append("한국은행 ECOS")
            except Exception as e:
                logger.error(f"ECOS API 검색 중 오류 발생: {str(e)}")
        
        return results
    
    def search_section_data(self, section_id: str, keywords: List[str]) -> Dict:
        """
        섹션별 필요 데이터 검색
        섹션 ID에 따라 적합한 API 선택
        """
        results = {"data": [], "sources": []}
        
        # 섹션별 적합한 API 선택
        if section_id in ["problem", "market"]:
            # 시장 분석 관련 데이터
            market_data = self.search_market_data(keywords)
            results["data"].extend(market_data["data"])
            results["sources"].extend(market_data["sources"])
            
        elif section_id == "competition":
            # 경쟁사 분석 관련 데이터
            competitors_data = self.search_competitors(keywords)
            results["data"].extend(competitors_data["data"])
            results["sources"].extend(competitors_data["sources"])
            
        elif section_id in ["scale_up", "financials"]:
            # 경제 지표, 재무 관련 데이터
            economic_data = self.search_economic_indicators(keywords)
            results["data"].extend(economic_data["data"])
            results["sources"].extend(economic_data["sources"])
        
        # API 키가 없는 경우 더미 데이터 제공
        if not results["data"]:
            logger.warning(f"API 키가 설정되지 않아 더미 데이터를 반환합니다. 섹션: {section_id}")
            results["data"] = self._get_dummy_data(section_id, keywords)
            results["sources"] = ["예시 데이터 (API 키 미설정)"]
        
        return results
    
    # 개별 API 검색 메서드
    def _search_kosis(self, keywords: List[str], industry_code: Optional[str] = None) -> Dict:
        """통계청 KOSIS API 검색"""
        # API 키 확인
        api_key = self.config.get("kosis", {}).get("api_key")
        if not api_key:
            return {"data": [], "sources": []}
        
        # 여기에 실제 KOSIS API 호출 코드 구현
        # 지금은 예시 데이터 반환
        return {"data": [
            {"title": "국내 시장 규모", "value": "2023년 기준 약 3.7조원", "year": "2023", "growth": "전년 대비 12% 성장"},
            {"title": "시장 전망", "value": "2025년까지 연평균 8.5% 성장 예상", "year": "2025", "growth": "CAGR 8.5%"}
        ], "sources": ["통계청 KOSIS"]}
    
    def _search_kisti(self, keywords: List[str], search_type: str) -> Dict:
        """KISTI API 검색"""
        # API 키 확인
        api_key = self.config.get("kisti", {}).get("api_key")
        if not api_key:
            return {"data": [], "sources": []}
        
        # 여기에 실제 KISTI API 호출 코드 구현
        # 지금은 예시 데이터 반환
        if search_type == "competitors":
            return {"data": [
                {"title": "주요 경쟁사", "companies": ["A기업", "B기업", "C기업"], "market_share": [35, 25, 15]},
                {"title": "업계 경쟁 구도", "description": "상위 3개 기업이 시장의 75%를 차지하는 과점 형태"}
            ], "sources": ["KISTI"]}
        else:
            return {"data": [], "sources": []}
    
    def _search_ecos(self, keywords: List[str]) -> Dict:
        """한국은행 ECOS API 검색"""
        # API 키 확인
        api_key = self.config.get("ecos", {}).get("api_key")
        if not api_key:
            return {"data": [], "sources": []}
        
        # 여기에 실제 ECOS API 호출 코드 구현
        # 지금은 예시 데이터 반환
        return {"data": [
            {"title": "GDP 성장률", "value": "2.0%", "year": "2023"},
            {"title": "기준금리", "value": "3.5%", "year": "2023"}
        ], "sources": ["한국은행 ECOS"]}
    
    def _search_public_data_portal(self, keywords: List[str], search_type: str) -> Dict:
        """공공데이터 포털 API 검색"""
        # API 키 확인
        api_key = self.config.get("public_data_portal", {}).get("api_key")
        if not api_key:
            return {"data": [], "sources": []}
        
        # 여기에 실제 공공데이터 포털 API 호출 코드 구현
        # 지금은 예시 데이터 반환
        if search_type == "market":
            return {"data": [
                {"title": "국내 산업 동향", "value": "디지털 전환 가속화로 관련 시장 성장세", "year": "2023"},
                {"title": "소비자 트렌드", "value": "친환경, 건강 중시 소비 증가", "year": "2023"}
            ], "sources": ["공공데이터 포털"]}
        else:
            return {"data": [], "sources": []}
    
    def _get_dummy_data(self, section_id: str, keywords: List[str]) -> List:
        """API 키가 없는 경우 제공할 더미 데이터"""
        if section_id in ["problem", "market"]:
            return [
                {"title": "시장 규모 예시", "value": "약 00조원", "year": "2023", "growth": "전년 대비 약 0% 성장"},
                {"title": "시장 전망 예시", "value": "향후 5년간 연평균 0% 성장 예상", "year": "2028"}
            ]
        elif section_id == "competition":
            return [
                {"title": "주요 경쟁사 예시", "companies": ["A사", "B사", "C사"], "market_share": [30, 20, 10]},
                {"title": "경쟁 구도 예시", "description": "상위 3개 기업이 시장의 60%를 차지하는 과점 형태"}
            ]
        elif section_id in ["scale_up", "financials"]:
            return [
                {"title": "경제 지표 예시", "value": "GDP 성장률 0%", "year": "2023"},
                {"title": "재무 지표 예시", "value": "업종 평균 영업이익률 00%", "year": "2023"}
            ]
        else:
            return [
                {"title": "예시 데이터", "value": "실제 API 연동 시 정확한 데이터 제공 가능", "year": "2023"}
            ] 