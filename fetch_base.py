import os
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE_URL = "https://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrrmRltmUsefulSckbdInfoInqire"
SERVICE_KEY = os.getenv("PUBLIC_DATA_KEY", "Your_Service_Key_Here")

params = {
    "serviceKey": SERVICE_KEY,
    "pageNo": "1",
    "numOfRows": "500"
}

# 원주시 주요 응급의료기관 좌표 및 기본 주소 매핑 테이블
HOSPITAL_GEO = {
    "A2200001": {
        "address": "강원특별자치도 원주시 일산로 20 (일산동)",
        "lat": 37.348633,
        "lon": 127.945207
    },
    "A2200015": {
        "address": "강원특별자치도 원주시 서원대로 387 (개운동)",
        "lat": 37.337775,
        "lon": 127.953689
    }
}

def get_tag_text(item, tag, default=""):
    elem = item.find(tag)
    return elem.text.strip() if elem is not None and elem.text else default

try:
    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        xml_data = response.read().decode("utf-8")

    root = ET.fromstring(xml_data)
    items = root.findall(".//item")

    wonju_hospitals = []
    for item in items:
        duty_name = get_tag_text(item, "dutyName")
        hpid = get_tag_text(item, "hpid")

        if hpid in HOSPITAL_GEO or "원주" in duty_name:
            geo_info = HOSPITAL_GEO.get(hpid, {"address": "", "lat": 0.0, "lon": 0.0})
            
            hospital_info = {
                "hpid": hpid,
                "name": duty_name,
                "address": geo_info["address"],
                "lat": geo_info["lat"],
                "lon": geo_info["lon"],
                "tel": get_tag_text(item, "dutyTel3"),
                "emergencyBeds": int(get_tag_text(item, "hvec", "0")),
                "pediatricBeds": int(get_tag_text(item, "hv28", "0")),
                "ctAvailable": get_tag_text(item, "hvctayn") == "Y",
                "mriAvailable": get_tag_text(item, "hvmriayn") == "Y",
                "ventilatorAvailable": get_tag_text(item, "hvventiayn") == "Y",
                "updatedAt": get_tag_text(item, "hvidate")
            }
            wonju_hospitals.append(hospital_info)

    with open("wonju_hospitals.json", "w", encoding="utf-8") as f:
        json.dump(wonju_hospitals, f, ensure_ascii=False, indent=2)

    print(f"좌표 포함 저장 완료! 총 {len(wonju_hospitals)}곳 -> wonju_hospitals.json")

except Exception as e:
    print(f"오류 발생: {e}")
