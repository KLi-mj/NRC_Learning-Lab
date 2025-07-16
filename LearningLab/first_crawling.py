import requests
from bs4 import BeautifulSoup

print("=" * 50)
print("크롤링 환경 테스트 시작!")
print("=" * 50)

# 1단계: 간단한 웹 요청 테스트
print("\n1단계: 웹 요청 테스트")
try:
    url = "https://httpbin.org/html"
    response = requests.get(url)
    print(f"✅ 성공! 응답 코드: {response.status_code}")
except Exception as e:
    print(f"❌ 오류: {e}")

# 2단계: HTML 파싱 테스트
print("\n2단계: HTML 파싱 테스트")
try:
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('h1')
    print(f"✅ 웹페이지 제목: {title.text if title else '제목 없음'}")
except Exception as e:
    print(f"❌ 오류: {e}")

# 3단계: 실제 웹사이트 크롤링 테스트 (간단한 예)
print("\n3단계: 실제 웹사이트 테스트")
try:
    url = "https://quotes.toscrape.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 첫 번째 명언 가져오기
    first_quote = soup.find('span', class_='text')
    first_author = soup.find('small', class_='author')
    
    if first_quote and first_author:
        print(f"✅ 첫 번째 명언: {first_quote.text}")
        print(f"✅ 작가: {first_author.text}")
    else:
        print("❌ 명언을 찾을 수 없습니다")
        
except Exception as e:
    print(f"❌ 오류: {e}")

print("\n" + "=" * 50)
print("크롤링 환경 테스트 완료!")
print("모든 단계가 성공했다면 크롤링 준비 완료입니다! 🎉")
print("=" * 50)
