import json
import xml.etree.ElementTree as ET
import requests

# 1. 공공데이터포털에서 발급받은 일반 인증키 (Decoding 키) 입력
SERVICE_KEY = "Your_Service_Key_Here"

url = (
    "http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEgytListInfoInqire"
)
params = {
    "serviceKey": SERVICE_KEY,
    "Q0": "강원도",
    "Q1": "원주시",  # 원주시로 한정
    "numOfRows": 20,
}

response = requests.get(url, params=params)
root = ET.fromstring(response.content)

hospitals = []
for item in root.findall(".//item"):
  lat = item.findtext("wgs84Lat")
  lon = item.findtext("wgs84Lon")

  # 좌표(위도, 경도)가 정상적으로 존재하는 병원만 유효하게 추출
  if lat and lon:
    hospitals.append({
        "hpid": item.findtext("hpid"),
        "name": item.findtext("dutyName"),
        "address": item.findtext("dutyAddr"),
        "lat": float(lat),
        "lon": float(lon),
        "tel": item.findtext("dutyTel1"),
        "emergencyTel": item.findtext("dutyTel3"),
    })

# 원주시 전용 JSON으로 저장
with open("wonju_hospitals.json", "w", encoding="utf-8") as f:
  json.dump(hospitals, f, ensure_ascii=False, indent=2)

print(
    f"성공! 원주시 응급의료기관 총 {len(hospitals)}곳 추출 완료 ->"
    " wonju_hospitals.json"
)