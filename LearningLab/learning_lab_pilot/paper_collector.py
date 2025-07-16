import arxiv
import pandas as pd
import requests
import time
from datetime import datetime
import re
import os

class PaperCollector:
    def __init__(self):
        self.papers = []
        
    def search_arxiv_papers(self, query, max_results=30):
        """arXiv에서 논문 검색 및 메타데이터 수집"""
        print(f"🔍 arXiv에서 '{query}' 키워드로 {max_results}개 논문 검색 중...")
        
        # arXiv 검색 설정
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
            sort_order=arxiv.SortOrder.Descending
        )
        
        papers_data = []
        
        try:
            for i, paper in enumerate(search.results(), 1):
                print(f"📄 {i}/{max_results}: {paper.title[:50]}...")
                
                # 메타데이터 추출
                paper_info = {
                    'id': i,
                    'arxiv_id': paper.get_short_id(),
                    'title': paper.title.strip(),
                    'authors': ', '.join([author.name for author in paper.authors]),
                    'published_date': paper.published.strftime('%Y-%m-%d'),
                    'categories': ', '.join(paper.categories),
                    'primary_category': paper.primary_category,
                    'abstract': paper.summary.strip().replace('\n', ' '),
                    'pdf_url': paper.pdf_url,
                    'arxiv_url': paper.entry_id,
                    'comment': getattr(paper, 'comment', ''),
                    'journal_ref': getattr(paper, 'journal_ref', ''),
                    'doi': getattr(paper, 'doi', ''),
                    'word_count': len(paper.summary.split()),
                    'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                papers_data.append(paper_info)
                
                # API 제한 고려한 딜레이
                time.sleep(0.5)
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            
        self.papers = papers_data
        print(f"✅ 총 {len(papers_data)}개 논문 수집 완료!")
        return papers_data
    
    def classify_papers_by_category(self):
        """논문을 카테고리별로 분류"""
        if not self.papers:
            print("❌ 수집된 논문이 없습니다.")
            return None
            
        df = pd.DataFrame(self.papers)
        
        # 주요 카테고리별 분류
        category_mapping = {
            'cs.AI': 'Artificial Intelligence',
            'cs.LG': 'Machine Learning', 
            'cs.CV': 'Computer Vision',
            'cs.CL': 'Natural Language Processing',
            'cs.RO': 'Robotics',
            'cs.IR': 'Information Retrieval',
            'cs.NE': 'Neural Networks',
            'stat.ML': 'Statistical ML',
            'cs.DC': 'Distributed Computing',
            'cs.CR': 'Cryptography & Security'
        }
        
        def get_main_category(categories):
            for cat in categories.split(', '):
                if cat in category_mapping:
                    return category_mapping[cat]
            return 'Other'
        
        df['main_category'] = df['categories'].apply(get_main_category)
        
        # 카테고리별 통계
        category_stats = df['main_category'].value_counts()
        print("\n📊 카테고리별 논문 분포:")
        for category, count in category_stats.items():
            print(f"  {category}: {count}개")
            
        return df
    
    def save_to_excel(self, df, filename='ai_papers_pilot.xlsx'):
        """엑셀 파일로 저장"""
        try:
            # 열 순서 정리
            columns_order = [
                'id', 'title', 'authors', 'published_date', 'main_category', 
                'primary_category', 'categories', 'abstract', 'word_count',
                'arxiv_id', 'pdf_url', 'arxiv_url', 'journal_ref', 'doi', 
                'comment', 'collected_at'
            ]
            
            df_ordered = df[columns_order]
            
            # 엑셀 저장
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 전체 데이터
                df_ordered.to_excel(writer, sheet_name='전체논문', index=False)
                
                # 카테고리별 시트
                for category in df['main_category'].unique():
                    category_df = df_ordered[df_ordered['main_category'] == category]
                    sheet_name = category.replace('/', '_')[:30]  # 시트명 길이 제한
                    category_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 통계 시트
                stats_df = df['main_category'].value_counts().reset_index()
                stats_df.columns = ['카테고리', '논문수']
                stats_df.to_excel(writer, sheet_name='통계', index=False)
            
            print(f"💾 엑셀 파일 저장 완료: {filename}")
            
        except Exception as e:
            print(f"❌ 엑셀 저장 실패: {e}")
    
    def generate_summary_report(self, df):
        """요약 리포트 생성"""
        print("\n" + "="*60)
        print("📈 AI 논문 수집 파일럿 테스트 결과 리포트")
        print("="*60)
        
        print(f"🔍 검색 키워드: AI technology")
        print(f"📚 총 수집 논문: {len(df)}개")
        print(f"📅 수집 기간: {df['published_date'].min()} ~ {df['published_date'].max()}")
        print(f"📊 평균 초록 길이: {df['word_count'].mean():.0f} 단어")
        
        print(f"\n🏷️ 주요 카테고리:")
        for category, count in df['main_category'].value_counts().head(5).items():
            percentage = (count / len(df)) * 100
            print(f"  • {category}: {count}개 ({percentage:.1f}%)")
        
        print(f"\n📝 최신 논문 5개:")
        latest_papers = df.nlargest(5, 'published_date')
        for _, paper in latest_papers.iterrows():
            print(f"  • {paper['title'][:60]}... ({paper['published_date']})")
        
        print("\n" + "="*60)

def main():
    """메인 실행 함수"""
    print("🚀 AI 논문 자동분류 파일럿 테스트 시작!")
    
    # 1. 논문 수집기 초기화
    collector = PaperCollector()
    
    # 2. AI와 기술 관련 논문 검색
    # arXiv 검색 쿼리 최적화
    query = "artificial intelligence OR machine learning OR deep learning OR AI technology"
    papers = collector.search_arxiv_papers(query, max_results=30)
    
    if not papers:
        print("❌ 논문 수집 실패")
        return
    
    # 3. 논문 분류
    df = collector.classify_papers_by_category()
    
    if df is None:
        return
    
    # 4. 엑셀 파일 저장
    collector.save_to_excel(df)
    
    # 5. 요약 리포트 출력
    collector.generate_summary_report(df)
    
    print("\n✅ 파일럿 테스트 완료! 이제 팀 빌딩에 활용하세요! 🎯")

if __name__ == "__main__":
    main()