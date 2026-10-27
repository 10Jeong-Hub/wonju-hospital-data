# wonju-hospital-data

1. **정적 데이터 배치**
   * `wonju_hospitals.json` ➡️ `web/data/wonju_hospitals.json` (또는 `server/data/`)
2. **실시간 병상 파서 교체**
   * `beds.js` ➡️ `web/js/beds.js` (소아병상 `hv28` 등 공식 스키마가 보완된 코드로 덮어쓰기)
