import re
from typing import Dict, List, Optional

class DataIntegration:
    """
    API에서 가져온 데이터를 사업계획서 섹션에 통합하는 클래스
    """
    
    def __init__(self):
        # 데이터 형식 및 섹션별 템플릿 정의
        self.section_templates = {
            "problem": {
                "market_size": "시장 규모: {value} ({year}년 기준, {growth})",
                "market_trend": "시장 트렌드: {value} ({year}년)",
                "market_forecast": "시장 전망: {value}"
            },
            "market": {
                "market_size": "시장 규모: {value} ({year}년 기준, {growth})",
                "market_trend": "시장 트렌드: {value} ({year}년)",
                "market_forecast": "시장 전망: {value}"
            },
            "competition": {
                "competitors": "주요 경쟁사: {companies}",
                "market_share": "시장 점유율: {description}",
                "competition_status": "경쟁 구도: {description}"
            },
            "scale_up": {
                "economic_indicator": "경제 지표: {title} - {value} ({year}년)",
                "growth_forecast": "성장 전망: {value}"
            },
            "financials": {
                "economic_indicator": "경제 지표: {title} - {value} ({year}년)",
                "industry_average": "업종 평균: {value} ({year}년)"
            }
        }
    
    def format_data_item(self, section_id: str, data_item: Dict) -> str:
        """
        데이터 항목을 섹션에 맞는 텍스트 형식으로 변환
        """
        # 데이터 항목 타입 결정
        item_type = self._determine_item_type(data_item)
        
        # 섹션별 템플릿 가져오기
        templates = self.section_templates.get(section_id, {})
        
        # 해당 타입의 템플릿이 있으면 사용
        template = templates.get(item_type)
        if template:
            try:
                # 데이터에 따라 다른 형식의 포맷팅 사용
                if item_type == "competitors" and "companies" in data_item:
                    companies_str = ", ".join(data_item.get("companies", []))
                    return template.format(companies=companies_str)
                elif item_type == "market_share" and "market_share" in data_item:
                    companies = data_item.get("companies", [])
                    shares = data_item.get("market_share", [])
                    
                    if len(companies) == len(shares):
                        share_info = [f"{comp} ({share}%)" for comp, share in zip(companies, shares)]
                        description = ", ".join(share_info)
                        return template.format(description=description)
                    else:
                        return f"시장 점유율: 상세 정보 없음"
                else:
                    # 일반적인 케이스
                    return template.format(**data_item)
            except KeyError:
                # 템플릿에 필요한 키가 없는 경우
                return f"{data_item.get('title', '정보')}: {data_item.get('value', '상세 정보 없음')}"
        
        # 기본 포맷팅
        return f"{data_item.get('title', '정보')}: {data_item.get('value', '상세 정보 없음')}"
    
    def _determine_item_type(self, data_item: Dict) -> str:
        """
        데이터 항목의 타입 결정
        """
        title = data_item.get("title", "").lower()
        
        if "시장 규모" in title:
            return "market_size"
        elif "시장 전망" in title:
            return "market_forecast"
        elif "트렌드" in title:
            return "market_trend"
        elif "경쟁사" in title and "companies" in data_item:
            return "competitors"
        elif "점유율" in title or "market_share" in data_item:
            return "market_share"
        elif "경쟁 구도" in title:
            return "competition_status"
        elif "gdp" in title or "금리" in title:
            return "economic_indicator"
        elif "성장" in title and "forecast" not in title:
            return "growth_indicator"
        elif "업종 평균" in title:
            return "industry_average"
        else:
            # 타입을 결정할 수 없는 경우 기본값
            return "general_info"
    
    def integrate_data_into_section(self, section_content: str, api_data: List[Dict]) -> str:
        """
        API 데이터를 섹션 내용에 통합
        """
        if not api_data:
            return section_content
        
        # 통합할 데이터 텍스트 생성
        data_text = "\n\n참고 데이터:\n"
        for item in api_data:
            data_text += f"- {item.get('title', '정보')}: {item.get('value', '데이터 없음')}"
            if "year" in item:
                data_text += f" ({item['year']}년)"
            if "growth" in item:
                data_text += f", {item['growth']}"
            data_text += "\n"
        
        # 가정 표시 대체
        if "[필요 정보:" in section_content:
            # 가정 표시 패턴 찾기
            assumptions = re.findall(r'\[필요 정보:[^\]]+\]', section_content)
            
            if assumptions:
                # 첫 번째 가정 표시 찾기
                first_assumption = assumptions[0]
                # 데이터로 교체
                return section_content.replace(first_assumption, data_text)
        
        # 가정 표시가 없으면 섹션 끝에 추가
        return section_content + "\n" + data_text
    
    def create_data_summary(self, section_id: str, api_data: List[Dict], sources: List[str]) -> str:
        """
        API 데이터 요약 생성
        """
        if not api_data:
            return "관련 데이터를 찾을 수 없습니다."
        
        summary = f"다음은 {', '.join(sources)}에서 가져온 데이터입니다:\n\n"
        
        for item in api_data:
            formatted_item = self.format_data_item(section_id, item)
            summary += f"- {formatted_item}\n"
        
        return summary 