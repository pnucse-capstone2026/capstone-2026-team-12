#!/usr/bin/env bash
# Render 로그 수집기 — access_dashboard.html에 올릴 파일을 만든다.
#
# 사용법:  ./pull_logs.sh [시간]     (기본 24 = 최근 24시간)
# 출력:   같은 폴더 logs/ 아래 서비스별 .log 파일 (JSON 라인 형식)
#         → access_dashboard.html의 파일 업로드로 그대로 올리면 된다.
#
# 1회 설정: 이 파일 옆에 .render_pull.env 를 만들고 아래 3줄을 채운다.
#   RENDER_API_KEY=rnd_...   # 대시보드 → Account Settings → API Keys
#   OWNER_ID=tea-... 또는 usr-...   # Workspace Settings에 표시되는 ID
#   SERVICES="srv-backend아이디 srv-agent아이디"  # 각 서비스 URL의 srv-... 부분
# 주의: .render_pull.env 는 API 키가 들어가므로 절대 커밋하지 않는다.
set -euo pipefail

cd "$(dirname "$0")"
[ -f .render_pull.env ] && source .render_pull.env

HOURS="${1:-24}"
: "${RENDER_API_KEY:?RENDER_API_KEY가 없습니다. 스크립트 상단의 1회 설정을 참고하세요.}"
: "${OWNER_ID:?OWNER_ID가 없습니다. 스크립트 상단의 1회 설정을 참고하세요.}"
: "${SERVICES:?SERVICES가 없습니다. 스크립트 상단의 1회 설정을 참고하세요.}"

# BSD date(macOS) 기준. UTC ISO 형식으로 시작·끝 시각을 만든다.
START="$(date -u -v-"${HOURS}"H '+%Y-%m-%dT%H:%M:%SZ')"
END="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
STAMP="$(date '+%Y%m%d_%H%M')"
mkdir -p logs

for SRV in $SERVICES; do
  OUT="logs/${SRV}_${STAMP}.log"
  : > "$OUT"
  s="$START"; e="$END"; page=0; total=0
  echo "[$SRV] ${HOURS}시간치 수집 시작 (${START} ~ ${END})"
  while :; do
    RESP="$(curl -sS --get 'https://api.render.com/v1/logs' \
      -H "Authorization: Bearer ${RENDER_API_KEY}" \
      --data-urlencode "ownerId=${OWNER_ID}" \
      --data-urlencode "resource=${SRV}" \
      --data-urlencode "startTime=${s}" \
      --data-urlencode "endTime=${e}" \
      --data-urlencode "limit=100")"
    if ! echo "$RESP" | jq -e '.logs' > /dev/null 2>&1; then
      echo "[$SRV] 응답 오류: $(echo "$RESP" | head -c 300)" >&2
      exit 1
    fi
    n="$(echo "$RESP" | jq '.logs | length')"
    # 대시보드 파서가 읽는 JSON 라인({timestamp, message})으로 저장
    echo "$RESP" | jq -c '.logs[] | {timestamp, message}' >> "$OUT"
    total=$((total + n)); page=$((page + 1))
    if [ "$(echo "$RESP" | jq -r '.hasMore')" != "true" ] || [ "$page" -ge 300 ]; then
      break
    fi
    s="$(echo "$RESP" | jq -r '.nextStartTime')"
    e="$(echo "$RESP" | jq -r '.nextEndTime')"
  done
  echo "[$SRV] 완료: ${total}건 → ${OUT}"
done

echo "끝. access_dashboard.html 을 열어 logs/ 안의 파일을 업로드하세요."
