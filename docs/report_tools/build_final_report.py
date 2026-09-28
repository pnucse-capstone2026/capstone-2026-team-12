# 졸업과제 최종보고서 재조판 — 수정 반영판 (입니다체·공약→계획·§2.1 평문화·오류 정정)
from pathlib import Path

CSS = """@page { size: A4; margin: 20mm 18mm; }
body { font-family: 'Apple SD Gothic Neo','Noto Sans KR',serif; font-size: 10pt; line-height: 1.66; color:#111; }
.cover { text-align:center; page-break-after: always; padding-top: 30mm; }
.cover .aff { text-align:right; font-weight:700; font-size:10.5pt; line-height:1.5; }
.cover h1 { font-size:17pt; line-height:1.5; margin-top:38mm; }
.cover .en { font-size:11pt; margin-top:4mm; color:#222; }
.cover .authors { margin-top:40mm; font-size:11pt; line-height:2; }
.cover .dept { margin-top:45mm; font-size:10pt; }
.toc { page-break-after: always; }
.toc h2 { text-align:center; font-size:14pt; letter-spacing:8px; }
.toc ol { line-height:1.9; font-size:10pt; }
.toc .sub { margin-left:16px; color:#333; }
h2 { font-size:12.5pt; margin:16px 0 6px; border-top:2px solid #111; padding-top:10px; }
h3 { font-size:11pt; margin:12px 0 4px; }
h4 { font-size:10.2pt; margin:10px 0 3px; }
p { margin:5px 0; text-align: justify; }
table { border-collapse:collapse; width:100%; margin:8px 0 12px; break-inside:avoid; font-size:9.3pt; }
caption { font-weight:700; font-size:9.3pt; margin-bottom:4px; }
th, td { border-top:1px solid #333; border-bottom:1px solid #333; padding:4px 8px; text-align:left; vertical-align:top; }
thead th { border-bottom:1.2px solid #111; background:#fff; }
.obs { border:1.2px solid #555; background:#f4f4f4; padding:7px 11px; margin:10px 0; break-inside:avoid; }
.obs b.t { display:block; background:#555; color:#fff; margin:-7px -11px 6px; padding:3px 11px; font-size:9.3pt; }
.fig { text-align:center; margin:12px 0; break-inside:avoid; }
.fig .row { display:flex; justify-content:center; gap:10px; margin:6px 0; }
.fig .bx { border:1.2px solid #333; border-radius:6px; padding:6px 12px; font-size:9pt; }
.fig .cap { font-weight:700; font-size:9.3pt; margin-top:6px; }
ul { margin:4px 0 8px 18px; padding:0; } li { margin:3px 0; }
.refs li { margin:5px 0; }
"""

S = []
S.append("""<div class="cover">
<div class="aff">Pusan National University<br>Computer Science and<br>Engineering Technical Report<br>2026-09</div>
<h1>금융 취약계층을 위한 사용자 맞춤형<br>계약 문서 단순화 및 위험 안내 에이전트</h1>
<div class="en">A Personalized LLM Agent for Contract Simplification<br>and Risk Notification for Financially Vulnerable Users</div>
<div class="authors">202155528&nbsp; 김민찬&nbsp; kimmc3423@naver.com<br>
202155600&nbsp; 전동훈&nbsp; wjsehdgnsdl2@pusan.ac.kr<br>
202155618&nbsp; 최민제&nbsp; kqmdmsow@pusan.ac.kr<br><br>지도교수&nbsp; 최동희</div>
<div class="dept">부산대학교 정보컴퓨터공학부 · A. 소프트웨어/인공지능 분과</div>
</div>""")

S.append("""<div class="toc"><h2>목 차</h2><ol>
<li>서론 <div class="sub">1.1 연구 배경 · 1.2 기존 문제점 · 1.3 연구 목표</div></li>
<li>요구조건 및 설계 변경 사항 <div class="sub">2.1 파이프라인(4→5단계) · 2.2 평가 데이터셋(211행) · 2.3 평가 방법론 재설계 · 2.4 RAG 보류 · 2.5 전문가 자문의견 반영</div></li>
<li>시스템 설계 및 구현 <div class="sub">3.1 아키텍처 · 3.2 분석 파이프라인 · 3.3 조항 단위 4종 출력 · 3.4 평가 Rubric · 3.5 사용자 인터페이스 · 3.6 보안·개인정보</div></li>
<li>연구 결과 분석 및 평가 <div class="sub">4.1 골든데이터셋 · 4.2 관찰 1 확정 · 4.3 위험 판정 성능 · 4.4 관찰 2 확정 · 4.5 보조 결과 · 4.6 관찰 3 대응 · 4.7 사람 평가 · 4.8 주요 의사결정</div></li>
<li>구성원별 역할 및 개발 일정</li>
<li>현실적 제약 사항 및 대책</li>
<li>결론 및 향후 연구 방향 <div class="sub">부록 A. 프롬프트 설계 요약</div></li>
<li>참고 문헌</li>
</ol></div>""")

S.append("""<h2>1. 서론</h2>
<h3>1.1. 연구 배경</h3>
<p>전세사기, 금융 상품 불완전판매, 위임 계약을 악용한 피해 등 계약 문서를 정확히 이해하지 못해 발생하는 피해가 지속적으로 증가하고 있습니다. 금융·생활 계약(대출·보험·임대차·가맹 등)은 조항이 길고 전문 용어가 많아, 일반 이용자, 특히 고령층·외국인·사회초년생 등 금융 취약계층은 자신에게 불리한 조항을 스스로 인지하기 어렵습니다. 국내 실증 연구에서도 전세보증 45.3만 건을 분석한 결과 계약 특성이 사고를 예측함이 확인된 바 있습니다.</p>
<p>계약 문서의 위험은 대부분 "이미 늦게 발견된 기록"으로 남습니다. 본 과제가 구축한 골든데이터셋 전체가 분쟁조정례와 판결문이라는 사실 자체가, 위험이 분쟁이 되고 나서야 발견되었음을 보여 줍니다. 본 연구는 그 발견 시점을 서명 이후의 분쟁이 아니라 <b>서명 이전의 질문</b>으로 앞당기는 것을 지향합니다.</p>
<h3>1.2. 기존 문제점</h3>
<p>2026년 현재 대규모 언어모델(LLM)의 문서 이해 능력은 크게 향상되었으나, 이를 계약 해석에 그대로 적용할 경우 다음 네 가지 한계가 남습니다.</p>
<ul><li><b>출력의 비일관성</b>: 동일한 위험 조항에 대해 호출 시점마다 상이한 판단을 내립니다.</li>
<li><b>사용자 적응 부재</b>: 모든 사용자에게 동일한 난이도·어조로 응답합니다.</li>
<li><b>행동 지침의 부재</b>: "무엇을 추가로 확인해야 하는가"에 대한 구조적 안내가 없습니다.</li>
<li><b>환각(Hallucination)</b>: 존재하지 않는 조항·법령을 인용합니다.</li></ul>
<p>이러한 한계는 단순히 더 큰 모델을 사용한다고 해소되지 않습니다. 착수보고 단계에서는 이것이 가설이었으나, 본 과제의 Baseline 실험(Ⅳ장 3절)으로 실증되었습니다. 상위 모델(fable-5)을 단일 호출로 사용해도 A등급 정확도가 0.59에 그친 반면, 동급 모델(haiku)에 절차적 파이프라인 구조를 적용하자 0.70으로 향상되었습니다. 따라서 LLM 출력을 절차적으로 분해하고 각 단계의 품질을 정량적으로 측정·검증하는 체계가 필요합니다.</p>
<h3>1.3. 연구 목표</h3>
<p>본 연구의 목표는 사용자가 계약 내용을 이해하고 위험을 인지하며 필요한 행동을 수행할 수 있도록 지원하는 설명 중심 계약 해석 에이전트를 개발하는 것입니다. 각 조항마다 (1) 쉬운 설명, (2) 위험 여부·유형, (3) 위험 근거, (4) 확인 질문의 4종 출력을 제공하고, 사용자 페르소나(일반 성인·고령층·외국인)에 맞춰 설명 난이도를 조정합니다. 핵심 전략은 역할 분리형 파이프라인과 LLM-as-a-Judge 기반 정량 평가 및 사람 평가 검증입니다. 표 1은 착수보고서의 4대 목표와 최종 달성 현황입니다.</p>
<table><caption>표 1. 착수보고서 4대 목표 대비 최종 달성 현황</caption>
<thead><tr><th>핵심 목표</th><th>달성</th><th>비고</th></tr></thead>
<tr><td>① 조항 단위 4종 출력</td><td>완료</td><td>설명·위험여부/유형(10종)·근거·확인질문</td></tr>
<tr><td>② 페르소나 적응형 설명</td><td>완료</td><td>일반/고령층/외국인 3종</td></tr>
<tr><td>③ LLM-Judge 정량평가 + 사람 검증</td><td>완료</td><td>4-Aspect + 4모델 교차 + 사람 30명</td></tr>
<tr><td>④ 역할 분리형 파이프라인</td><td>완료</td><td>4단계 계획 → 5단계 구현(Domain 추가)</td></tr></table>
<p>중간보고 시점의 MVP(4단계·4종 출력·페르소나 2종·데모)에서, 최종보고 단계에서는 (i) 골든셋을 211행으로 확충하고, (ii) 중간보고에서 얻은 세 가지 관찰(Ⅳ장)을 본격 검증으로 확정하였으며, (iii) Domain 노드 추가·사람 평가·웹 서비스 배포를 완료하였습니다.</p>""")

Path('/tmp/report_part1.html').write_text("".join(S), encoding='utf-8')
print("1부 저장", sum(len(s) for s in S))
