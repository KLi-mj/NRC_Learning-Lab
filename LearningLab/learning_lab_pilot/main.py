"""
AI 논문 자동분류 시스템 - 메인 파이프라인
Learning Lab 파일럿 프로젝트
"""

from config import Config
from paper_collector import PaperCollector
from paper_analyzer import PaperAnalyzer
import time

def main():
    """전체 파이프라인 실행"""
    
    print("🚀 AI 논문 자동분류 시스템 시작!")
    print("=" * 60)
    
    # 1. 설정 검증
    if not Config.validate_api_keys():
        print("❌ API 키 설정이 필요합니다. .env 파일을 확인해주세요.")
        return
    
    # 2. 논문 수집 단계
    print("\n📚 1단계: 논문 수집")
    print("-" * 40)
    
    collector = PaperCollector()
    
    # AI 관련 논문 검색
    query = "artificial intelligence OR machine learning OR deep learning OR AI technology"
    papers = collector.search_arxiv_papers(query, max_results=Config.ARXIV_SEARCH_CONFIG['max_results'])
    
    if not papers:
        print("❌ 논문 수집 실패")
        return
    
    # 논문 분류 및 저장
    df = collector.classify_papers_by_category()
    collector.save_to_excel(df, 'collected_papers.xlsx')
    collector.generate_summary_report(df)
    
    # 3. 논문 분석 단계
    print("\n🤖 2단계: AI 분석")
    print("-" * 40)
    
    analyzer = PaperAnalyzer()
    
    # 수집된 논문 로드
    if not analyzer.load_papers('collected_papers.xlsx'):
        return
    
    # GPT로 초록 요약
    print("\n📝 GPT 요약 시작...")
    start_time = time.time()
    analyzer.summarize_abstracts_with_gpt()
    summary_time = time.time() - start_time
    print(f"⏱️ 요약 완료 시간: {summary_time:.1f}초")
    
    # 임베딩 생성
    print("\n🔢 임베딩 생성...")
    analyzer.create_embeddings()
    
    # 클러스터링 수행
    print("\n🎯 클러스터링...")
    analyzer.perform_clustering()
    
    # 클러스터 분석
    print("\n🔍 클러스터 분석...")
    cluster_analysis = analyzer.analyze_clusters()
    
    # 4. 시각화 및 결과 저장
    print("\n📊 3단계: 결과 정리")
    print("-" * 40)
    
    # 시각화 생성
    analyzer.visualize_clusters()
    
    # 최종 결과 저장
    analyzer.save_analysis_results()
    
    # 5. 최종 리포트
    print("\n" + "=" * 60)
    print("🎉 분석 완료! 최종 리포트")
    print("=" * 60)
    
    total_time = time.time() - start_time if 'start_time' in locals() else 0
    
    print(f"📚 수집된 논문: {len(df)}개")
    print(f"🤖 GPT 요약: 완료 ({summary_time:.1f}초)")
    print(f"🎯 클러스터 수: {len(analyzer.papers_df['cluster'].unique()) if analyzer.papers_df is not None and 'cluster' in analyzer.papers_df.columns else 0}개")
    print(f"📊 시각화: {Config.OUTPUT_CONFIG['charts_filename']}")
    print(f"💾 최종 결과: {Config.OUTPUT_CONFIG['excel_filename']}")
    print(f"⏱️ 총 소요시간: {total_time:.1f}초")
    
    print("\n🎯 팀 빌딩 데모 준비 완료!")
    print("📁 다음 파일들을 팀원들에게 보여주세요:")
    print(f"  • {Config.OUTPUT_CONFIG['excel_filename']} (분석 결과)")
    print(f"  • {Config.OUTPUT_CONFIG['charts_filename']} (클러스터 시각화)")
    
    # 향후 계획 제안
    print("\n🚀 다음 단계 제안:")
    print("  1. 더 많은 논문 수집 (100-500개)")
    print("  2. 한국어 논문 DB 연동 (KCI, KISS 등)")
    print("  3. 웹 인터페이스 개발")
    print("  4. 실시간 논문 모니터링 시스템")

def quick_demo():
    """빠른 데모용 (요약 생략)"""
    print("⚡ 빠른 데모 모드")
    
    # 논문 수집만
    collector = PaperCollector()
    query = "artificial intelligence"
    papers = collector.search_arxiv_papers(query, max_results=10)
    
    if papers:
        df = collector.classify_papers_by_category()
        collector.save_to_excel(df, 'demo_papers.xlsx')
        print("✅ 데모용 논문 10개 수집 완료!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        quick_demo()
    else:
        main()