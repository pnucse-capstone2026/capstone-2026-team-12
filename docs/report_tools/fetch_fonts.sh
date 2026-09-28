#!/bin/sh
# 최종보고서 조판용 폰트 내려받기 — 원본 초안 PDF에 내장된 폰트와 동일한 Noto CJK JP 3종.
# fonts/ 는 용량(약 68MB) 때문에 git에 넣지 않는다 (.gitignore 참조).
set -e
cd "$(dirname "$0")"
mkdir -p fonts
BASE="https://github.com/notofonts/noto-cjk/raw/main"
for f in Serif/OTF/Japanese/NotoSerifCJKjp-Regular.otf \
         Serif/OTF/Japanese/NotoSerifCJKjp-Bold.otf \
         Sans/OTF/Japanese/NotoSansCJKjp-Black.otf; do
  name="$(basename "$f")"
  if [ ! -s "fonts/$name" ]; then
    echo "downloading $name"
    curl -sSL --max-time 300 -o "fonts/$name" "$BASE/$f"
  fi
done
ls -la fonts
