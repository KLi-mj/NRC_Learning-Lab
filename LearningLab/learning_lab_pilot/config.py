import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """프로젝트 설정 클래스"""
    
    # API 키들
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    
    # arXiv 검색 설정
    ARXIV_SEARCH_CONFIG = {
        'max_results': 30,
        'sort_by': 'relevance',
        'delay_between_requests': 0.5  # API 제한 고려
    }
    
    # GPT 설정
    GPT_CONFIG = {
        'model': 'gpt-4o-mini',  # 비용 효율적인 모델
        'max_tokens': 150,       # 요약문 길이
        'temperature': 0.3,      # 일관성 있는 요약을 위해 낮게
        'timeout': 30
    }
    
    # 클러스터링 설정
    CLUSTERING_CONFIG = {
        'n_clusters': 5,         # 기본 클러스터 수
        'embedding_model': 'text-embedding-3-small',  # OpenAI 임베딩 모델
        'clustering_method': 'kmeans',  # 'kmeans' or 'hdbscan'
        'min_cluster_size': 2
    }
    
    # 출력 파일 설정
    OUTPUT_CONFIG = {
        'excel_filename': 'ai_papers_analysis.xlsx',
        'charts_filename': 'clustering_visualization.png',
        'summary_filename': 'analysis_summary.txt'
    }
    
    # 카테고리 매핑
    CATEGORY_MAPPING = {
        'cs.AI': 'Artificial Intelligence',
        'cs.LG': 'Machine Learning', 
        'cs.CV': 'Computer Vision',
        'cs.CL': 'Natural Language Processing',
        'cs.RO': 'Robotics',
        'cs.IR': 'Information Retrieval',
        'cs.NE': 'Neural Networks',
        'stat.ML': 'Statistical ML',
        'cs.DC': 'Distributed Computing',
        'cs.CR': 'Cryptography & Security',
        'cs.HC': 'Human-Computer Interaction',
        'cs.IT': 'Information Theory'
    }
    
    @classmethod
    def validate_api_keys(cls):
        """API 키 유효성 검사"""
        missing_keys = []
        
        if not cls.OPENAI_API_KEY:
            missing_keys.append('OPENAI_API_KEY')
        if not cls.CLAUDE_API_KEY:
            missing_keys.append('CLAUDE_API_KEY')
            
        if missing_keys:
            print(f"⚠️  다음 API 키가 누락되었습니다: {', '.join(missing_keys)}")
            print("📝 .env 파일에 API 키를 추가해주세요.")
            return False
        
        print("✅ API 키 설정 완료!")
        return True