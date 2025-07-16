"""
기존 수집된 논문 데이터로 GPT 분석 + 클러스터링만 실행
"""

from config import Config
from paper_analyzer import PaperAnalyzer
import time

def analyze_existing_papers():
    """기존 수집된 논문으로 분석만 실행"""
    
    print("🤖 기존 논문 데이터로 AI 분석 시작!")
    print("=" * 50)
    
    # 1. 설정 검증
    if not Config.validate_api_keys():
        print("❌ API 키 설정이 필요합니다.")
        return
    
    # 2. 분석기 초기화
    analyzer = PaperAnalyzer()
    
    # 3. 기존 데이터 로드
    print("📚 기존 수집 데이터 로드 중...")
    if not analyzer.load_papers('collected_papers.xlsx'):
        print("❌ collected_papers.xlsx 파일이 없습니다.")
        print("💡 먼저 demo_papers.xlsx로 시도해보겠습니다.")
        if not analyzer.load_papers('demo_papers.xlsx'):
            print("❌ 분석할 데이터가 없습니다.")
            return
    
    # 4. GPT 분석 시작
    print("\n🤖 GPT 분석 단계")
    print("-" * 30)
    
    start_time = time.time()
    
    # GPT로 초록 요약
    print("📝 GPT 요약 시작...")
    analyzer.summarize_abstracts_with_gpt()
    summary_time = time.time() - start_time
    
    # 임베딩 생성
    print("\n🔢 임베딩 생성...")
    analyzer.create_embeddings()
    
    # 클러스터링 수행
    print("\n🎯 클러스터링...")
    analyzer.perform_clustering()
    
    # 클러스터 분석
    print("\n🔍 클러스터 분석...")
    analyzer.analyze_clusters()
    
    # 5. 시각화 (텍스트)
    print("\n📊 결과 정리")
    print("-" * 30)
    analyzer.visualize_clusters()
    
    # 6. 결과 저장
    analyzer.save_analysis_results()
    
    # 7. 최종 리포트
    total_time = time.time() - start_time
    
    print("\n" + "=" * 50)
    print("🎉 분석 완료! 결과 리포트")
    print("=" * 50)
    
    print(f"📚 분석된 논문: {len(analyzer.papers_df)}개")
    print(f"🤖 GPT 요약: 완료 ({summary_time:.1f}초)")
    print(f"🎯 생성된 클러스터: {len(analyzer.papers_df['cluster'].unique()) if 'cluster' in analyzer.papers_df.columns else 0}개")
    print(f"💾 결과 파일: {Config.OUTPUT_CONFIG['excel_filename']}")
    print(f"⏱️ 총 소요시간: {total_time:.1f}초")
    
    print("\n🎯 팀 빌딩 데모 완료!")
    print("📁 생성된 파일:")
    print(f"  • {Config.OUTPUT_CONFIG['excel_filename']} (전체 분석 결과)")

if __name__ == "__main__":
    analyze_existing_papers()