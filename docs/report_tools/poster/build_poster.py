# 졸업과제 포스터 v6 — v4 템플릿(머리띠·배너·바닥 그림)을 재사용해 Pilltip 우수작 구성으로 재배치
import copy, qrcode
from pptx import Presentation
from pptx.util import Cm, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.dml import MSO_LINE_DASH_STYLE

ORANGE=RGBColor(0xF0,0x8A,0x24); NAVY=RGBColor(0x2F,0x3C,0x5E); GRAY=RGBColor(0x5F,0x5F,0x5F)
DARK=RGBColor(0x22,0x22,0x22); MID=DARK; LIGHT=DARK  # 회색 글씨 없이 전부 검정
CREAM=RGBColor(0xFF,0xF4,0xE8); PANEL=RGBColor(0xF1,0xF1,0xF1); WHITE=RGBColor(0xFF,0xFF,0xFF)
LINE=RGBColor(0xDD,0xDD,0xDD); RED=RGBColor(0xC0,0x39,0x2B); GREEN=RGBColor(0x1E,0x8E,0x3E)
FONT='Pretendard'

prs=Presentation('v4.pptx'); slide=prs.slides[0]
# ── 템플릿 그림 그룹만 남기고 전부 삭제
keep={'그룹 19','그룹 20','그룹 29','그룹 2'}
for sh in list(slide.shapes):
    if sh.name not in keep: sh._element.getparent().remove(sh._element)
groups={sh.name:sh for sh in slide.shapes}
# 배너: 그룹 안 좌표계 문제를 피하려고 그림만 추출해 새 위치에 다시 배치
def banner(group, top_cm, label):
    picshape=[c for c in group.shapes if c.shape_type==13][0]
    fn=f'banner_{label}.jpg'; open(fn,'wb').write(picshape.image.blob)
    group._element.getparent().remove(group._element)
    slide.shapes.add_picture(fn,Cm(0),Cm(top_cm),Cm(59.4),Cm(2.9))
    tb=slide.shapes.add_textbox(Cm(19.7),Cm(top_cm+0.5),Cm(20.0),Cm(1.6)); tf=tb.text_frame
    tf.margin_left=tf.margin_right=0
    pp=tf.paragraphs[0]; pp.alignment=PP_ALIGN.CENTER; r=pp.add_run(); r.text=label
    r.font.name=FONT; r.font.size=Pt(32); r.font.bold=True; r.font.color.rgb=WHITE
# 머리띠 제목: 모든 글자에 템플릿과 같은 그림자 효과(outerShdw) 적용
import copy as _copy
from lxml import etree as _et
_A='{http://schemas.openxmlformats.org/drawingml/2006/main}'
for c in groups['그룹 19'].shapes:
    if c.has_text_frame and c.name in ('TextBox 24','TextBox 25'):
        runs=[r for para in c.text_frame.paragraphs for r in para.runs]
        src=None
        for r in runs:
            rPr=r._r.find(_A+'rPr')
            if rPr is not None and rPr.find(_A+'effectLst') is not None: src=rPr.find(_A+'effectLst'); break
        if src is None:
            src=_et.fromstring('<a:effectLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:outerShdw blurRad="38100" dist="38100" dir="2700000" algn="tl"><a:srgbClr val="000000"><a:alpha val="43137"/></a:srgbClr></a:outerShdw></a:effectLst>')
        for r in runs:
            rPr=r._r.get_or_add_rPr()
            if rPr.find(_A+'effectLst') is None:
                # 스키마 순서: fill/ln → effectLst → latin/ea/cs … 이므로 latin 계열 앞에 삽입
                eff=_copy.deepcopy(src); idx=len(rPr)
                for k,ch in enumerate(rPr):
                    if ch.tag in (_A+'latin',_A+'ea',_A+'cs',_A+'sym',_A+'hlinkClick',_A+'hlinkMouseOver',_A+'rtl',_A+'extLst',_A+'highlight',_A+'uLnTx',_A+'uLn',_A+'uFillTx',_A+'uFill'):
                        idx=k; break
                rPr.insert(idx,eff)
# 머리띠의 포스터 번호 '00' → '12'
for c in groups['그룹 19'].shapes:
    if c.has_text_frame and c.text_frame.text.strip()=='00':
        for pp in c.text_frame.paragraphs:
            for r in pp.runs: r.text=r.text.replace('00','12')
# 머리띠 안 '과제 개요' 상자도 같은 규격으로 맞춤
for c in groups['그룹 19'].shapes:
    if c.has_text_frame and c.text_frame.text.strip()=='과제 개요':
        c.left=Cm(19.7); c.width=Cm(20.0); c.text_frame.margin_left=c.text_frame.margin_right=0
        for pp in c.text_frame.paragraphs:
            pp.alignment=PP_ALIGN.CENTER
            for r in pp.runs: r.font.name=FONT; r.font.size=Pt(32); r.font.bold=True
banner(groups['그룹 20'],34.0,'기술 설명')
banner(groups['그룹 29'],62.0,'연구 결과 및 기대효과')

def rect(x,y,w,h,fill=WHITE,line=None,radius=None,dash=False,shape=MSO_SHAPE.ROUNDED_RECTANGLE,lw=0.75):
    s=slide.shapes.add_shape(shape,Cm(x),Cm(y),Cm(w),Cm(h))
    s.fill.solid(); s.fill.fore_color.rgb=fill
    if line is None: s.line.fill.background()
    else:
        s.line.color.rgb=line; s.line.width=Pt(lw)
        if dash: s.line.dash_style=MSO_LINE_DASH_STYLE.DASH
    s.shadow.inherit=False
    if radius is not None and shape==MSO_SHAPE.ROUNDED_RECTANGLE: s.adjustments[0]=radius
    s.text_frame.text=''
    return s
def text(x,y,w,h,runs,size=10,bold=False,color=DARK,align=PP_ALIGN.LEFT,anchor=MSO_ANCHOR.TOP,spacing=1.15,margin=0.1):
    """runs: str 또는 [[(txt,opts),...] per paragraph]. opts: size,bold,color"""
    tb=slide.shapes.add_textbox(Cm(x),Cm(y),Cm(w),Cm(h)); tf=tb.text_frame; tf.word_wrap=True
    tf.margin_left=tf.margin_right=Cm(margin); tf.margin_top=tf.margin_bottom=Cm(0.05); tf.vertical_anchor=anchor
    paras = [[(runs,{})]] if isinstance(runs,str) else runs
    for i,pr in enumerate(paras):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.alignment=align; p.line_spacing=spacing
        for t,o in pr:
            r=p.add_run(); r.text=t; f=r.font; f.name=FONT; f.size=Pt(o.get('size',size)); f.bold=o.get('bold',bold); f.color.rgb=o.get('color',color)
    return tb
def bullets(x,y,w,h,items,size=10,color=DARK,spacing=1.2):
    paras=[]
    for it in items:
        if isinstance(it,str): paras.append([('•  ',{'color':DARK}),(it,{})])
        else: paras.append([('•  ',{'color':DARK})]+it)
    return text(x,y,w,h,paras,size=size,color=color,spacing=spacing)
def heading(x,y,label,w=30,size=15):
    d=rect(x+0.05,y+0.36,0.3,0.3,fill=ORANGE,shape=MSO_SHAPE.OVAL)   # 글자 세로 중심에 맞춘 작은 점
    text(x+0.5,y,w,1.0,label,size=size,bold=True,anchor=MSO_ANCHOR.MIDDLE)
def badge(x,y,n,d=0.7,fs=9):
    s=rect(x,y,d,d,fill=ORANGE,shape=MSO_SHAPE.OVAL); tf=s.text_frame; tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    p=tf.paragraphs[0]; p.alignment=PP_ALIGN.CENTER; r=p.add_run(); r.text=str(n); r.font.size=Pt(fs); r.font.bold=True; r.font.color.rgb=WHITE; r.font.name=FONT
    tf.vertical_anchor=MSO_ANCHOR.MIDDLE
def pic(path,x,y,w,h=None):
    return slide.shapes.add_picture(path,Cm(x),Cm(y),Cm(w),Cm(h) if h else None)
def browser(path,x,y,w,h):
    rect(x,y,w,h+0.9,fill=PANEL,radius=0.06)
    for i,c in enumerate([RGBColor(0xEF,0x6B,0x5E),RGBColor(0xF5,0xBF,0x4F),RGBColor(0x61,0xC5,0x54)]):
        rect(x+0.35+i*0.5,y+0.28,0.3,0.3,fill=c,shape=MSO_SHAPE.OVAL)
    pic(path,x,y+0.85,w,h)

# ═══════════ 1. 과제 개요 (y 17.6~33.4) ═══════════
box=rect(2.4,17.6,25.8,15.0,fill=CREAM,line=ORANGE,radius=0.05,dash=True)
# 01 통계 막대
text(3.9,18.0,12,1.0,'01   계약 위험, 사람도 LLM도 놓친다',size=13,bold=True,color=NAVY)
text(3.9,18.9,12,0.8,'정부·법원 직접 판정 조항 기준 · 본 과제 실측',size=10.5,color=MID)
bars=[('일반 대중 위험 판정 정답률 (N=33)',61.0,GRAY,'61%'),('상위 LLM 단일 호출 정확도 (Fable 5)',59.0,GRAY,'59%'),
      ('동급 LLM 단일 호출 정확도 (Haiku 4.5)',52.0,GRAY,'52%'),('본 과제 파이프라인 (Haiku 4.5)',70.0,ORANGE,'70%')]
yy=19.85
for lab,v,c,txt in bars:
    text(3.9,yy,12,0.7,lab,size=10.5,bold=(c==ORANGE),color=DARK)
    rect(3.9,yy+0.7,v/100*8.6,0.85,fill=c,radius=0.5)
    text(3.9+v/100*8.6+0.15,yy+0.55,2.5,1.1,txt,size=12.5,bold=True,color=(ORANGE if c==ORANGE else DARK))
    yy+=1.95
# 02 사례 카드 (축소)
text(15.5,18.0,12,1.0,'02   계약 위험은 언제 발견되는가',size=13,bold=True,color=NAVY)
text(15.5,18.9,12,0.8,'골든셋은 분쟁 이후의 판정문으로 구성',size=10.5,color=MID)
cards=[('주택금융연구 · 2025','전세보증 45.3만 건 분석, 부채비율 90% 초과 시 사고 승산 29.9배'),
       ('금융분쟁조정위 · 2017-17 / 2018-8','즉시연금 약관의 불명확한 이자·사업비 조건, 분쟁 후에야 위험 확정'),
       ('한국공정거래조정원 · 2025-03','광고대행 위탁계약의 과도한 위약금 조항, 분쟁조정으로 판정'),
       ('약관규제법 위반 유형 10종','책임 면제 · 과도한 위약금 · 일방적 해지 · 불명확한 수수료 …')]
yy=19.85
for i,(src,body) in enumerate(cards):
    badge(15.6,yy+0.12,i+1,d=0.6,fs=8)
    text(16.4,yy-0.05,10.9,0.7,src,size=9.5,bold=True,color=ORANGE)
    text(16.4,yy+0.55,10.9,1.3,body,size=10,bold=True,color=DARK,spacing=1.05)
    yy+=1.95
text(15.5,27.65,12.2,0.8,'→ 위험 발견 시점을 서명 이후의 분쟁에서 서명 이전의 질문으로',size=10,bold=True,color=NAVY)
# 03 실제 피해 규모 (공식 통계)
text(3.9,28.45,20,1.0,'03   실제 피해 규모',size=13,bold=True,color=NAVY)
stats=[('4만 936건','전세사기 피해자 누적 결정','국토교통부 · 2026.8 기준'),
       ('9조 4,189억 원','HUG 전세보증 대위변제 5년 누적 · 회수율 24%','2020~2024, 4만 3,631건'),
       ('5만 7,359건','상반기 금융민원 · 보험 민원 49%','금융감독원 · 2025 상반기')]
for i,(num,lab,src) in enumerate(stats):
    x=[3.9,11.4,20.6][i]   # 가운데 항목이 상자 중심(15.3cm)에 오도록 배치
    rect(x,29.55,0.18,2.45,fill=ORANGE,shape=MSO_SHAPE.RECTANGLE)          # 왼쪽 강조 막대
    text(x+0.5,29.45,7.4,1.15,num,size=22,bold=True,color=ORANGE,anchor=MSO_ANCHOR.MIDDLE)
    text(x+0.5,30.6,7.4,0.7,lab,size=10,bold=True,color=DARK,spacing=1.0,anchor=MSO_ANCHOR.MIDDLE)
    text(x+0.5,31.3,7.4,0.6,src,size=8,color=DARK,anchor=MSO_ANCHOR.MIDDLE)

# 오른쪽: 배경·목표
heading(29.2,17.7,'과제 선정 배경')
bullets(29.8,18.9,27.4,7.9,[
 '전세사기·금융상품 불완전판매·위임 계약 악용 등 계약 문서를 정확히 이해하지 못해 생기는 피해가 해마다 늘고 있으며, 전세사기 피해자 결정만 누적 4만 건을 넘어섰음',
 '대출·보험·임대차 계약은 조항이 길고 전문용어가 많아 고령층·외국인·사회초년생 등 금융 취약계층은 불리한 조항을 스스로 알아채기 어렵고, 위험은 대부분 분쟁이 생긴 뒤에야 "늦은 기록"으로 발견됨',
 '범용 LLM은 문서 이해력이 높아졌지만 계약 해석에 그대로 쓰면 ① 호출마다 달라지는 판단 ② 누구에게나 같은 난이도의 설명 ③ 무엇을 더 확인해야 하는지 알려주지 않는 행동 지침 부재 ④ 없는 조항·법령을 인용하는 환각의 네 가지 한계가 남음',
 '이 한계는 더 큰 모델로 해소되지 않아 상위 모델의 단일 호출도 정부·법원 판정 조항 27건에서 정확도 0.59에 그쳤으므로, LLM 출력을 절차적으로 분해하고 단계별 품질을 측정·검증하는 체계가 필요',
 [('대상 사용자: ',{'bold':True}),('고령층 · 외국인 · 사회초년생 등 금융 취약계층',{})],
 [('대상 문서: ',{'bold':True}),('임대차 계약서 · 대출 · 보험 · 카드 등 금융 약관',{})]],size=13.5,spacing=1.2)
heading(29.2,26.4,'과제 목표')
bullets(29.8,27.7,27.4,5.8,[
 [('계약서 각 조항마다 ',{}),('쉬운 설명 · 위험 여부/유형 · 위험 근거 · 확인 질문',{'bold':True}),('의 4종 출력을 제공하는 설명 중심 계약 해석 에이전트를 개발하고, 텍스트·PDF·사진 입력을 받는 실제 웹 서비스로 배포',{})],
 '일반 성인 · 고령층 · 외국인(16개 언어) 페르소나에 맞춰 설명 난이도와 언어만 조정하고 위험 판정은 동일하게 유지해, 누가 읽어도 같은 위험을 각자의 눈높이로 이해하도록 함',
 '역할 분리형 5단계 파이프라인(Parser → Domain → Analysis → Persona → Judge)으로 판정의 일관성과 근거 충실성을 확보하고, 근거 인용을 원문과 대조해 환각을 차단',
 '정부·법원 판정 기반 골든데이터셋 211행, 3회 반복 다수결, 4모델 Judge 교차검증, 일반 대중 사람 평가로 "믿을 수 있는 답"인지 다중 검증',
 '확인 질문 · 협상 문구 · 상담기관 연결로 탐지에서 행동까지 잇는 서명 전 점검 도구를 제공해 위험 발견 시점을 서명 이전으로 앞당김'],size=13.5,spacing=1.2)

# ═══════════ 2. 기술 설명 (배너 34.0~36.9) — 아키텍처 + 6블록 / 단계 화살표 / 화면 5장 ═══════════
heading(2.4,37.2,'시스템 아키텍처 · 5단계 파이프라인',w=40)
pic('arch.png',2.4,38.3,25.2)                       # 높이 약 13.95 → 52.25
# 오른쪽 2열×3행 설명 블록
blocks6=[('Parser · 규칙 기반 조항 분리',[
  '"제N조"가 줄 시작에 올 때만 새 조항으로 분리하고, 문장 중간의 조 참조나 "제6조의3" 형태는 조항 시작으로 보지 않음',
  '별지·별표·부칙은 버리지 않고 별도 구획으로 보존하며, 양식 빈칸 조각은 완결 문장 판별로 걸러 조항 오인을 방지',
  'LLM을 호출하지 않는 결정적 전처리로 입력 손실을 차단하고, 조항 커버리지 70% 미만이면 경고 표시']),
 ('Domain · 문서 유형 판별',[
  '주택/상가 임대차·보험·대출·카드 등 13종 유형을 문서 전체에서 1회 판별해 모든 조항 분석에 공유 상태로 주입',
  '같은 "2기 연체 시 해지" 문언도 주택임대차는 안전, 상가임대차는 법정 기준이 3기라 위험으로 판정이 갈림',
  '유형 정보를 "표준적 조항"이라는 관대 신호로 오용하던 회귀를 2×2 어블레이션으로 규명하고 재설계해 정식 반영']),
 ('Analysis · 4종 출력 + 인용 대조',[
  '위험/주의/안전 3단계와 약관규제법 대응 위험 유형 10종으로 판정하고 쉬운 설명·근거·확인 질문을 한 번에 생성',
  '예: 수리비 전가 조항 → 위험·책임 면제, 근거 "민법 제623조 임대인 수선의무 배제", 질문 "큰 수리 비용은 누가 내나요?"',
  '근거 인용이 원문에 실재하는지 코드로 대조해 창작 인용은 재시도하고, 소진 시 \'주의\'로 강등해 사용자 확인 요구']),
 ('Persona · 맞춤 재작성 · 다국어',[
  '판정은 그대로 두고 설명만 일반 성인·고령층·외국인(16개 언어) 눈높이로 재작성하므로 위험 판정이 바뀌지 않음',
  '고령층 모드는 24개 조항 실측에서 문장 길이 −31%, 전문용어 −52%를 보였고 위험 판정은 24/24 조항에서 동일',
  'TTS 낭독·점자단말기 호환 텍스트, 조항별 협상 문구와 상담기관 연결로 탐지에서 행동까지 이어줌']),
 ('Judge · 채점 + 품질 게이트',[
  '별도 채점 모델(Sonnet)이 Clarity·Faithfulness·Risk Coverage·Actionability 4축을 문서 단위로 5점 척도 채점',
  '평균 3.5 또는 Faithfulness 3.0 미만이면 충실성·위험식별 미달은 Analysis, 이해용이성 미달은 Persona로 최대 2회 재실행',
  '채점자 자체를 Claude·Solar·DeepSeek·Gemini 4모델로 교차검증해 정답 앵커 40쌍 기준 97~100% 일치 확인']),
 ('전처리 · 보안 · 외부 API',[
  '주민등록번호·카드·계좌·전화·이메일 5종을 LLM 호출 전 규칙 마스킹, 계약 본문과 파일명은 로그에 남기지 않음',
  '정규화·규칙 탐지·격리·난수 구분자 격리의 다층 인젝션 방어로 적대적 공격 125건에서 화면 관통 0건',
  'Upstage Document Parse(OCR)·Gemini(STT) 연동, 계정 보관은 클라이언트 측 PBKDF2+AES-GCM 암호화로 서버가 복호화 불가'])]
GX=[29.0,43.4]; GY0=38.5; GP=4.7; GW=13.6
for i,(title,items) in enumerate(blocks6):
    x=GX[i%2]; y=GY0+(i//2)*GP
    badge(x,y-0.07,i+1,d=0.4,fs=6.5)
    text(x+0.37,y-0.2,GW-0.4,0.9,'[ '+title+' ]',size=13,bold=True)
    bullets(x+0.35,y+0.7,GW-0.35,3.8,items,size=10.5,spacing=1.02)
# 단계 화살표 띠
CY=53.0; CH=1.35; CW=11.2; ov=0.35
labels=['① Parser   조항 분리','② Domain   유형 판별','③ Analysis   4종 출력 · 인용 대조','④ Persona   맞춤 재작성','⑤ Judge   채점 · 게이트']
for i,lab in enumerate(labels):
    x=2.4+i*(CW-ov)
    sh=slide.shapes.add_shape(MSO_SHAPE.CHEVRON if i>0 else MSO_SHAPE.PENTAGON,Cm(x),Cm(CY),Cm(CW),Cm(CH))
    sh.fill.solid(); sh.fill.fore_color.rgb=(NAVY if i==0 else ORANGE); sh.line.fill.background(); sh.shadow.inherit=False
    tf=sh.text_frame; tf.margin_left=tf.margin_right=Cm(0.4); pp=tf.paragraphs[0]; pp.alignment=PP_ALIGN.CENTER
    a,b=lab.split('   '); r=pp.add_run(); r.text=a+'  '; r.font.name=FONT; r.font.size=Pt(11); r.font.bold=True; r.font.color.rgb=WHITE
    r=pp.add_run(); r.text=b; r.font.name=FONT; r.font.size=Pt(9.5); r.font.color.rgb=WHITE
# 화면 5장
SW=10.6; SH=5.0; gap=0.5; y0=54.9
screens=[('s1.png','[ 계약서 입력 · 텍스트/PDF/사진 ]'),('s2.png','[ 문서 유형 선택 · 자동 판별 ]'),('s3.png','[ 조항별 위험/안전 배지 · 판정 근거 ]'),
         ('s4.png','[ 페르소나 선택 · 접근성 · 다국어 ]'),('s5.png','[ 조항 상세 · AI 검증 리포트 ]')]
for i,(f,cap) in enumerate(screens):
    x=2.4+i*(SW+gap)
    browser(f,x,y0,SW,SH)
    text(x,y0+SH+0.9,SW,0.6,cap,size=9.5,bold=True,align=PP_ALIGN.CENTER)

# ═══════════ 3. 연구 결과 및 기대효과 (배너 62.0~64.9) — 기획서 스타일 표 ═══════════
def table(x,y,colw,rows,rowh=0.8,size=10,header=True,align=None,hfill=ORANGE):
    """직사각형+텍스트로 그리는 표. rows[0]은 머리글. align: 열별 정렬 리스트"""
    align = align or [PP_ALIGN.LEFT]*len(colw)
    for r,row in enumerate(rows):
        cx=x
        for c,val in enumerate(row):
            if r==0 and header:
                fill,fc,bold=hfill,WHITE,True
            else:
                fill=WHITE if r%2==1 else RGBColor(0xFA,0xF5,0xEE); fc=DARK; bold=(c==0)
            rect(cx,y+r*rowh,colw[c],rowh,fill=fill,line=RGBColor(0xE3,0xD9,0xCC),shape=MSO_SHAPE.RECTANGLE,lw=0.5)
            runs = val if isinstance(val,list) else [(val,{})]
            text(cx,y+r*rowh,colw[c],rowh,[runs],size=size,bold=bold,color=fc,align=align[c],anchor=MSO_ANCHOR.MIDDLE,margin=0.18,spacing=1.05)
            cx+=colw[c]
    return y+len(rows)*rowh
RY=65.4
# 3-1 검증 결과 요약 표
heading(2.4,RY,'검증 결과 요약',w=26)
rows=[['검증 항목','결과'],
 ['공식 Test 40건',[('정확도 72.5%',{'bold':True}),(' · Precision 0.71 / Recall 0.91 / F1 0.80',{})]],
 ['A등급 27건',[('리콜 1.00',{'bold':True,'color':ORANGE}),(' · 위험 미탐지 0건 · 정확도 0.70',{})]],
 ['금융 전이 16건',[('정확도 0.75 · 리콜 1.00',{'bold':True}),('',{})]],
 ['정상 표준계약서 5문서 94조항',[('\'위험\' 오탐 0건',{'bold':True,'color':GREEN}),(' · \'주의\' 9건',{})]],
 ['LLM Judge 교차검증',[('Clarity · Risk Coverage · Actionability 100%, Faithfulness 97%',{'bold':True})]],
 ['적대적 벤치마크 125건',[('사용자 화면 기준 공격 성공률 0.0%',{'bold':True}),('',{})]],
 ['페르소나 적응 24조항',[('판정 불변 24/24',{'bold':True}),(' · 문장 길이 −31% · 전문용어 −52%',{})]],
 ['공정위 심결 1,046건 커버리지',[('위험 유형 탐지율 66%',{'bold':True}),('',{})]]]
table(2.4,RY+1.3,[10.4,15.4],rows,rowh=0.93,size=9.5)
# 3-2 혼동행렬 + 사람 평가
heading(29.2,RY,'A등급 27건 혼동행렬',w=14)
table(29.2,RY+1.3,[5.4,4.2,4.2],[['','예측 위험/주의','예측 안전'],['실제 위험 10건','10','0'],['실제 안전 17건','8','9']],rowh=0.78,size=9.5,align=[PP_ALIGN.LEFT,PP_ALIGN.CENTER,PP_ALIGN.CENTER])
text(29.2,RY+3.75,13.8,1.5,'위험 10건은 하나도 놓치지 않았고, 오답 8건은 전부 안전을 주의로 부른 과잉 경보이며, 위험을 놓치는 방향보다 피해가 작아 의도적으로 허용.',size=9,color=MID,spacing=1.08)
heading(29.2,RY+5.4,'사람 평가',w=14)
table(29.2,RY+6.7,[3.2,10.6],[['항목','결과'],['선호 비교',[('고령층 맞춤 설명 57.8%',{'bold':True}),('',{})]],['판정 일치',[('시스템–정답 71.4%',{'bold':True}),(' · 사람–정답 61.0%',{})]],['유용성',[('도움 3.79/5',{'bold':True}),('· 추천 57.6% · 최유용 \'쉬운 설명\' 45%',{})]]],rowh=0.78,size=9.5)
# 3-3 골든데이터셋 구성 표 + 건당 원가 표
heading(44.2,RY,'골든데이터셋 구성',w=13)
table(44.2,RY+1.3,[4.0,1.5,7.7],[['세트','행','출처 · 검수'],['공식 Test','44','hldcc 조정례 · LBox 판례 · AI Hub'],['임대차 확장','34','조정례·판례, 경계 안전 사례 포함'],['금융 전이','32','금감원 분쟁조정 결정례'],['스프린트 확충','101','법제처 OPEN API 수집 + 독립 적대적 검수'],[[('합계',{'bold':True})],[('211',{'bold':True})],'A등급 193 / C등급 18 · 위험 119 / 안전 91']],rowh=0.74,size=9.5,align=[PP_ALIGN.LEFT,PP_ALIGN.CENTER,PP_ALIGN.LEFT])
heading(44.2,RY+5.9,'건당 원가',w=13)
table(44.2,RY+7.15,[6.2,2.2,4.8],[['문서','조항','건당 원가'],['주택임대차표준계약서','16','$0.175 · 약 241원'],['예금거래기본약관','25','$0.242 · 약 333원'],[[('평균 20조항 기준',{'bold':True})],[('20',{'bold':True})],[('$0.204 · 약 282원',{'bold':True,'color':ORANGE})]]],rowh=0.72,size=9.5,align=[PP_ALIGN.LEFT,PP_ALIGN.CENTER,PP_ALIGN.LEFT])
text(44.2,RY+10.05,13.2,0.6,'법률 상담 1회 3~5만원의 100분의 1 이하 · 월 1천 건 약 28만원',size=8.5,color=MID)
# 3-4 기대효과 · 향후 연구 (글머리)
EY=RY+10.45
heading(2.4,EY,'기대효과',w=20)
bullets(2.6,EY+0.95,26.8,2.4,['서명 전에 조항별 위험을 인지하고, 확인 질문 · 협상 문구 · 상담기관 연결로 바로 행동할 수 있는 금융 취약계층의 사전 점검 도구',
 '정부·법원 판정 골든셋 + 반복 다수결 + 4모델 교차검증 + 사람 평가의 다중 검증으로 "그럴듯한 답"이 아닌 "믿을 수 있는 답"을 제공',
 '고령층 모드 · 16개 언어 · TTS · 점자 텍스트로 금융소비자보호법의 설명의무 이행과 고령자 보호 절차를 보조'],size=11,spacing=1.05)
heading(30.3,EY,'향후 연구',w=20)
bullets(30.5,EY+0.95,20.5,2.4,['표준약관 · 판정례 RAG 도입으로 조항 텍스트 밖의 법리 보완',
 '실거래가 · 등기부 등 계약서 밖 위험 신호 통합, 외국인 페르소나 언어별 정량 검증',
 '전문가 · 고령층 평가자 확대로 사람 평가 표본 확장, 신탁 도메인 보강'],size=11,spacing=1.05)
# QR
for i,(url,lab) in enumerate([('https://github.com/kqmdmsow/half-fifty','GitHub'),('https://halffifty.onrender.com','서비스 데모')]):
    img=qrcode.make(url); img.save(f'qr{i}.png')
    x=51.6+i*3.1
    pic(f'qr{i}.png',x,EY+0.35,2.5,2.5); text(x-0.4,EY+2.8,3.3,0.5,lab,size=6.5,color=MID,align=PP_ALIGN.CENTER)

prs.save('poster_v6.pptx'); print('saved poster_v6.pptx')
