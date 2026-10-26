// [3단계] 병상 조회: 원주시 응급의료기관의 실시간 가용 병상
// 실제 API: 공공데이터포털 "국립중앙의료원_전국 응급의료기관 정보 조회 서비스"
//   오퍼레이션 getEmrrmRltmUsefulSckbdInfoInqire (응급실 실시간 가용병상정보 조회)
import { config } from './config.js';

const ENDPOINT = 'https://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrrmRltmUsefulSckbdInfoInqire';

/** 우리 파이프라인에서 쓰는 자원명 → API 응답 필드. match.js가 이 표로 판단한다. */
export const RESOURCE_FIELDS = {
  응급실: 'hvec',          // 일반 응급실 가용 병상 수
  소아응급실: 'hv28',      // 소아 전용 가용 병상 수 (소아 고열/경련 분류 필수)
  일반중환자실: 'hvicu',   // 일반 중환자실
  신경중환자실: 'hvcc',
  흉부중환자실: 'hvccc',
  신생아중환자실: 'hvncc',
  수술실: 'hvoc',
  CT: 'hvctayn',          // Y/N
  MRI: 'hvmriayn',        // Y/N
  혈관조영: 'hvangioayn',  // Y/N
  인공호흡기: 'hvventiayn', // Y/N
};

const NUMERIC = ['hvec', 'hv28', 'hvicu', 'hvcc', 'hvccc', 'hvncc', 'hvoc', 'hvgc'];

function normalize(item) {
  const h = { ...item };
  for (const k of NUMERIC) {
    if (k in h && h[k] !== undefined && h[k] !== '') {
      h[k] = Number(h[k]);
    }
  }
  return h;
}

/** data.go.kr 기본 응답(XML) → 객체 배열 */
function parseXml(text) {
  const doc = new DOMParser().parseFromString(text, 'application/xml');
  const code = doc.querySelector('resultCode')?.textContent;
  if (code && code !== '00') {
    throw new Error(`병상 API 오류 ${code}: ${doc.querySelector('resultMsg')?.textContent}`);
  }
  return [...doc.querySelectorAll('item')].map((item) =>
    Object.fromEntries([...item.children].map((el) => [el.tagName, el.textContent.trim()])),
  );
}

async function fetchReal() {
  const params = new URLSearchParams({
    STAGE1: '강원도',
    STAGE2: '원주시', // 원주시 타겟 고정
    pageNo: '1',
    numOfRows: '20',
  });
  // serviceKey는 Encoding 인증키 사용 권장
  const res = await fetch(`${ENDPOINT}?serviceKey=${config.bedApiKey}&${params}`);
  if (!res.ok) throw new Error(`병상 API HTTP ${res.status}`);
  return parseXml(await res.text());
}

async function fetchMock() {
  const res = await fetch(config.bedsMockUrl);
  return res.json();
}

/**
 * @returns {Promise<{source: 'api'|'mock', warning?: string, hospitals: object[]}>}
 */
export async function getBeds() {
  if (config.bedApiKey) {
    try {
      return { source: 'api', hospitals: (await fetchReal()).map(normalize) };
    } catch (e) {
      const hospitals = (await fetchMock()).map(normalize);
      return { source: 'mock', warning: `실제 API 호출 실패, 목업 사용: ${e.message}`, hospitals };
    }
  }
  return { source: 'mock', hospitals: (await fetchMock()).map(normalize) };
}