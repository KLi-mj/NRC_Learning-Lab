import pandas as pd
import numpy as np
from openai import OpenAI
import time
from sklearn.cluster import KMeans
from config import Config

class PaperAnalyzer:
    """논문 분석기: GPT 요약 + 클러스터링 (시각화 제거)"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.papers_df = None
        self.embeddings = None
        self.clusters = None
        
    def load_papers(self, excel_file):
        """엑셀 파일에서 논문 데이터 로드"""
        try:
            self.papers_df = pd.read_excel(excel_file, sheet_name='전체논문')
            print(f"📚 {len(self.papers_df)}개 논문 데이터 로드 완료!")
            return True
        except Exception as e:
            print(f"❌ 파일 로드 실패: {e}")
            return False
    
    def summarize_abstracts_with_gpt(self):
        """GPT를 사용한 초록 요약"""
        if self.papers_df is None:
            print("❌ 논문 데이터가 없습니다. 먼저 load_papers()를 실행하세요.")
            return
        
        print("🤖 GPT로 초록 요약 중...")
        summaries = []
        key_insights = []
        
        for i, row in self.papers_df.iterrows():
            print(f"📝 {i+1}/{len(self.papers_df)}: {row['title'][:40]}...")
            
            try:
                # 요약 프롬프트
                summary_prompt = f"""
다음 논문 초록을 한국어로 간단히 요약해주세요 (2-3문장):

제목: {row['title']}
초록: {row['abstract']}

요약:"""

                # 핵심 인사이트 추출 프롬프트
                insight_prompt = f"""
다음 논문에서 핵심 기술이나 방법론을 1-2개 키워드로 추출해주세요:

제목: {row['title']}
초록: {row['abstract']}

키워드 (쉼표로 구분):"""

                # GPT API 호출
                summary_response = self.client.chat.completions.create(
                    model=Config.GPT_CONFIG['model'],
                    messages=[{"role": "user", "content": summary_prompt}],
                    max_tokens=Config.GPT_CONFIG['max_tokens'],
                    temperature=Config.GPT_CONFIG['temperature']
                )
                
                time.sleep(1)  # API 제한 고려
                
                insight_response = self.client.chat.completions.create(
                    model=Config.GPT_CONFIG['model'],
                    messages=[{"role": "user", "content": insight_prompt}],
                    max_tokens=50,
                    temperature=Config.GPT_CONFIG['temperature']
                )
                
                summary = summary_response.choices[0].message.content.strip()
                insight = insight_response.choices[0].message.content.strip()
                
                summaries.append(summary)
                key_insights.append(insight)
                
                time.sleep(1)  # API 제한 고려
                
            except Exception as e:
                print(f"⚠️ {i+1}번 논문 요약 실패: {e}")
                summaries.append("요약 생성 실패")
                key_insights.append("키워드 추출 실패")
        
        # 결과를 데이터프레임에 추가
        self.papers_df['gpt_summary'] = summaries
        self.papers_df['key_insights'] = key_insights
        
        print("✅ GPT 요약 완료!")
        return self.papers_df
    
    def create_embeddings(self):
        """OpenAI 임베딩 생성"""
        if self.papers_df is None:
            print("❌ 논문 데이터가 없습니다.")
            return
            
        print("🔢 임베딩 생성 중...")
        
        # 제목 + 초록을 결합한 텍스트로 임베딩 생성
        texts = []
        for _, row in self.papers_df.iterrows():
            combined_text = f"{row['title']} {row['abstract']}"
            texts.append(combined_text)
        
        try:
            embeddings = []
            batch_size = 10  # 배치 처리로 API 호출 최적화
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                print(f"📊 임베딩 생성: {i+1}-{min(i+batch_size, len(texts))}/{len(texts)}")
                
                response = self.client.embeddings.create(
                    model=Config.CLUSTERING_CONFIG['embedding_model'],
                    input=batch
                )
                
                for embedding_obj in response.data:
                    embeddings.append(embedding_obj.embedding)
                
                time.sleep(1)  # API 제한 고려
            
            self.embeddings = np.array(embeddings)
            print(f"✅ 임베딩 생성 완료! 차원: {self.embeddings.shape}")
            return self.embeddings
            
        except Exception as e:
            print(f"❌ 임베딩 생성 실패: {e}")
            return None
    
    def perform_clustering(self, n_clusters=None):
        """K-means 클러스터링 수행"""
        if self.embeddings is None:
            print("❌ 임베딩이 없습니다. 먼저 create_embeddings()를 실행하세요.")
            return
        
        if n_clusters is None:
            n_clusters = Config.CLUSTERING_CONFIG['n_clusters']
        
        print(f"🎯 {n_clusters}개 클러스터로 분류 중...")
        
        try:
            # K-means 클러스터링
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(self.embeddings)
            
            # 결과를 데이터프레임에 추가
            self.papers_df['cluster'] = cluster_labels
            self.clusters = cluster_labels
            
            # 클러스터별 통계
            cluster_stats = pd.Series(cluster_labels).value_counts().sort_index()
            print("📊 클러스터별 논문 수:")
            for cluster_id, count in cluster_stats.items():
                print(f"  클러스터 {cluster_id}: {count}개")
            
            print("✅ 클러스터링 완료!")
            return cluster_labels
            
        except Exception as e:
            print(f"❌ 클러스터링 실패: {e}")
            return None
    
    def analyze_clusters(self):
        """클러스터별 주요 특징 분석"""
        if self.papers_df is None or 'cluster' not in self.papers_df.columns:
            print("❌ 클러스터링이 완료되지 않았습니다.")
            return
        
        print("🔍 클러스터별 특징 분석 중...")
        
        cluster_analysis = []
        
        for cluster_id in sorted(self.papers_df['cluster'].unique()):
            cluster_papers = self.papers_df[self.papers_df['cluster'] == cluster_id]
            
            # 클러스터의 주요 특징 추출
            analysis = {
                'cluster_id': cluster_id,
                'paper_count': len(cluster_papers),
                'main_categories': cluster_papers['main_category'].value_counts().head(3).to_dict(),
                'avg_year': cluster_papers['published_date'].apply(lambda x: int(x[:4])).mean(),
                'sample_titles': cluster_papers['title'].head(3).tolist(),
                'common_keywords': self._extract_common_keywords(cluster_papers['key_insights'].tolist())
            }
            
            cluster_analysis.append(analysis)
            
            print(f"\n🎯 클러스터 {cluster_id} ({len(cluster_papers)}개 논문):")
            print(f"  주요 카테고리: {list(analysis['main_categories'].keys())[:2]}")
            print(f"  평균 발행년도: {analysis['avg_year']:.1f}")
            print(f"  공통 키워드: {analysis['common_keywords'][:3]}")
        
        return cluster_analysis
    
    def _extract_common_keywords(self, keyword_lists):
        """공통 키워드 추출"""
        all_keywords = []
        for keywords_str in keyword_lists:
            if isinstance(keywords_str, str):
                keywords = [k.strip().lower() for k in keywords_str.split(',')]
                all_keywords.extend(keywords)
        
        # 빈도수 계산
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # 상위 키워드 반환
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return [kw[0] for kw in sorted_keywords[:5]]
    
    def visualize_clusters(self):
        """클러스터링 결과 텍스트로 표시 (matplotlib 사용 안함)"""
        if self.embeddings is None or self.clusters is None:
            print("❌ 클러스터링 결과가 없습니다.")
            return
        
        print("📊 클러스터링 결과 요약:")
        print("-" * 40)
        
        unique_clusters = np.unique(self.clusters)
        for cluster_id in unique_clusters:
            cluster_papers = self.papers_df[self.papers_df['cluster'] == cluster_id]
            print(f"클러스터 {cluster_id}: {len(cluster_papers)}개 논문")
            print(f"  대표 논문: {cluster_papers.iloc[0]['title'][:50]}...")
        
        print("📊 시각화 차트는 matplotlib 오류로 생략됨")
    
    def save_analysis_results(self):
        """분석 결과를 엑셀로 저장"""
        if self.papers_df is None:
            print("❌ 분석 결과가 없습니다.")
            return
        
        filename = Config.OUTPUT_CONFIG['excel_filename']
        
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 전체 분석 결과
                self.papers_df.to_excel(writer, sheet_name='분석결과', index=False)
                
                # 클러스터별 시트
                if 'cluster' in self.papers_df.columns:
                    for cluster_id in sorted(self.papers_df['cluster'].unique()):
                        cluster_data = self.papers_df[self.papers_df['cluster'] == cluster_id]
                        sheet_name = f'클러스터_{cluster_id}'
                        cluster_data.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 요약 통계
                summary_stats = {
                    '항목': ['총 논문수', '평균 초록 길이', '클러스터 수', '분석 완료 시간'],
                    '값': [
                        len(self.papers_df),
                        self.papers_df['word_count'].mean(),
                        len(self.papers_df['cluster'].unique()) if 'cluster' in self.papers_df.columns else 0,
                        pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                pd.DataFrame(summary_stats).to_excel(writer, sheet_name='요약통계', index=False)
            
            print(f"💾 분석 결과 저장 완료: {filename}")
            
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")