# 시스템 아키텍처 → draw.io(.drawio). v2: 상자 여백 제거, 단일 로고 상자는 정사각형, 화살표는 전부 상자에 연결.
import base64, re, pathlib, html
LOGOS = pathlib.Path('../img/logos')
cells = []; _id = [1]
def nid():
    _id[0] += 1; return f'c{_id[0]}'
def esc(v): return html.escape(v, quote=True)
def vertex(value, x, y, w, h, style):
    i = nid()
    cells.append(f'<mxCell id="{i}" value="{esc(value)}" style="{style}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return i
def edge(value, src, tgt, ex, ey, nx, ny, points=(), color='#4b5563', dashed=False, lcolor='#374151', fsize=13, offset=None):
    i = nid()
    st = (f'edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;strokeColor={color};strokeWidth=2;endArrow=block;endFill=1;'
          f'exitX={ex};exitY={ey};exitDx=0;exitDy=0;entryX={nx};entryY={ny};entryDx=0;entryDy=0;'
          f'fontSize={fsize};fontColor={lcolor};labelBackgroundColor=#ffffff;fontFamily=Pretendard;' + ('dashed=1;dashPattern=7 6;' if dashed else ''))
    pts = ''.join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in points)
    arr = f'<Array as="points">{pts}</Array>' if pts else ''
    if offset: arr += f'<mxPoint x="{offset[0]}" y="{offset[1]}" as="offset"/>'
    cells.append(f'<mxCell id="{i}" value="{esc(value)}" style="{st}" edge="1" parent="1" source="{src}" target="{tgt}"><mxGeometry relative="1" as="geometry">{arr}</mxGeometry></mxCell>')
    return i
def svg_data(name):
    s = re.sub(r'<title>.*?</title>', '', LOGOS.joinpath(f'{name}.svg').read_text())
    return 'data:image/svg+xml,' + base64.b64encode(s.encode()).decode()
def img(name, cx, y, size):
    return vertex('', cx-size/2, y, size, size, f'shape=image;imageAspect=1;image={svg_data(name)};')
def text(value, x, y, w, h, fsize=14, bold=False, color='#1f2328', align='center'):
    return vertex(value, x, y, w, h, f'text;html=0;strokeColor=none;fillColor=none;align={align};verticalAlign=middle;fontSize={fsize};fontStyle={1 if bold else 0};fontColor={color};fontFamily=Pretendard;')
CARD = 'rounded=1;arcSize=12;fillColor=#ffffff;strokeColor=#e6e8ec;strokeWidth=1.5;shadow=1;html=0;'
SQ   = 'rounded=1;arcSize=14;fillColor=#ffffff;strokeColor=#e6e8ec;strokeWidth=1.5;shadow=1;html=0;'
ZONE = 'rounded=1;arcSize=6;fillColor=#f7f8fa;strokeColor=#e3e6eb;strokeWidth=1.5;html=0;'
GRP  = 'rounded=1;arcSize=10;fillColor=none;strokeColor=#cfd4db;strokeWidth=1.5;dashed=1;html=0;fontSize=12;fontStyle=1;fontColor=#6b7280;align=left;verticalAlign=top;spacingLeft=10;spacingTop=-8;labelBackgroundColor=#ffffff;fontFamily=Pretendard;'
def square(x, y, s, name, label, logo=52, label2=None):
    """정사각형 상자: 로고 + 이름 (여백 최소)"""
    b = vertex('', x, y, s, s, SQ)
    if name: img(name, x+s/2, y+s*0.18, logo)
    ly = y + s*0.18 + logo + 6
    text(label, x, ly, s, 20, 12, True, '#374151')
    if label2: text(label2, x, ly+18, s, 18, 11.5, False, '#6b7280')
    return b
def badge_square(x, y, s, text_, color, label, label2=None):
    b = vertex('', x, y, s, s, SQ)
    vertex(text_, x+s/2-26, y+s*0.18, 52, 44, f'rounded=1;arcSize=25;fillColor={color};strokeColor=none;fontColor=#ffffff;fontSize=17;fontStyle=1;html=0;fontFamily=Pretendard;')
    ly = y + s*0.18 + 44 + 6
    text(label, x, ly, s, 20, 13, True, '#374151')
    if label2: text(label2, x, ly+18, s, 18, 11.5, False, '#6b7280')
    return b
def node(x, y, title, sub, w=148, kind=''):
    fill, stroke, extra = '#ffffff', '#dfe3e8', ''
    if kind == 'pre': fill, extra = '#fbfbfc', 'dashed=1;'
    if kind == 'gate': fill, stroke = '#fff8f2', '#EE8A3C'
    if kind == 'out': fill, stroke = '#f0f7ff', '#bcd6f5'
    b = vertex('', x, y, w, 84, f'rounded=1;arcSize=18;fillColor={fill};strokeColor={stroke};strokeWidth=1.5;html=0;shadow=1;{extra}')
    text(title, x, y+14, w, 24, 15, True, '#1f2328')
    text(sub, x+4, y+40, w-8, 32, 11, False, '#6b7280')
    return b
def fr(v, lo, hi): return round((v-lo)/(hi-lo), 3)

# ── 제목 (REPORT=1 이면 생략: 보고서에는 캡션이 따로 있음)
import os
REPORT = os.environ.get('REPORT') == '1'
if not REPORT:
    vertex('', 0, 0, 520, 12, 'fillColor=#EE8A3C;strokeColor=none;')
    vertex('', 28, 50, 14, 14, 'ellipse;fillColor=#EE8A3C;strokeColor=none;')
    text('시스템 아키텍처', 52, 34, 400, 46, 34, True, align='left')

# ── 사용자 (정사각형)
US = 130; ux, uy = 40, 200
user = vertex('', ux, uy, US, US, SQ)
vertex('', ux+33, uy+28, 64, 44, 'rounded=1;arcSize=15;fillColor=#ffffff;strokeColor=#374151;strokeWidth=3;')
vertex('', ux+47, uy+74, 36, 6, 'rounded=1;fillColor=#374151;strokeColor=none;')
text('사용자', ux, uy+90, US, 24, 17, True)

# ── Render 영역
ZX, ZY, ZW, ZH = 220, 120, 1030, 745
zone = vertex('', ZX, ZY, ZW, ZH, ZONE)
img('render', ZX+34, ZY+16, 20)
text('Render', ZX+46, ZY+10, 120, 30, 17, True, align='left')

# ── 상단: 프론트(정사각형 3개 묶음) / Spring Boot / PostgreSQL
S = 100
FX, FY = 250, 170
FW, FH = 3*S+4*12, S+24
front = vertex('', FX, FY, FW, FH, CARD)
for i,(n,l) in enumerate([('react','React'),('typescript','TypeScript'),('tailwindcss','Tailwind CSS')]):
    square(FX+12+i*(S+12), FY+12, S, n, l, 40)
BX, BY = 700, FY+12
back = square(BX, BY, S, 'springboot', 'Spring Boot', 44)
DX, DY = 930, FY+12
db = square(DX, DY, S, 'postgresql', 'PostgreSQL', 44)

# ── 에이전트 카드
AX, AY, AW, AH = 250, 350, 980, 485
agent = vertex('', AX, AY, AW, AH, CARD)
text('AI 에이전트', AX+18, AY+10, 130, 32, 20, True, align='left')
for n,l,cx in [('python','Python',AX+160),('fastapi','FastAPI',AX+245),('langchain','LangGraph',AX+335)]:
    img(n, cx, AY+16, 20); text(l, cx+12, AY+14, 120, 24, 12.5, True, '#4b5563', 'left')
NW, GAP = 118, 48
R1, R2 = AY+100, AY+300
xs = [AX+16 + i*(NW+GAP) for i in range(6)]
vertex('전처리 (LLM 호출 전)', xs[0]-10, R1-28, NW*2+GAP+20, 140, GRP)
vertex('분석 단계', xs[2]-10, R1-28, NW*4+GAP*3+20, 140, GRP)
vertex('품질 게이트', xs[3]-10, R2-28, NW*3+GAP*2+20, 140, GRP)
n_mask = node(xs[0],R1,'개인정보 마스킹','정규식 5종',kind='pre')
n_inj  = node(xs[1],R1,'인젝션 방어','정규화 · 탐지 · 격리',kind='pre')
n_par  = node(xs[2],R1,'① Parser','규칙 기반 · 별지 구획')
n_dom  = node(xs[3],R1,'② Domain','문서 유형 13종 · Haiku')
n_ana  = node(xs[4],R1,'③ Analysis','위험 유형 10종 · Haiku')
n_cit  = node(xs[5],R1,'인용 대조','코드 · 원문 실재 검사')
n_per  = node(xs[5],R2,'④ Persona','설명만 재작성 · Haiku')
n_jud  = node(xs[4],R2,'⑤ Judge','4-Aspect 채점 · Sonnet')
n_gate = node(xs[3],R2,'게이트','평균 3.5 · Faithfulness 3.0',kind='gate')
n_out  = node(xs[0],R2,'출력 조립','4종 출력 · 사례 각주 · 번역',w=NW*2+GAP,kind='out')

# ── 외부 API (세로 한 열, 정사각형)
EX, ES = 1300, 110
ext = []
for i,(kind,args) in enumerate([('sq',('claude','Claude Haiku 4.5')),('sq',('anthropic','Claude Sonnet 4.6')),('bd',('UP','#805AD5','Upstage','Document Parse')),('sq',('googlegemini','Gemini','STT'))]):
    y = AY + i*(ES+14)
    if kind=='sq':
        n,l = args[0],args[1]; l2 = args[2] if len(args)>2 else None
        ext.append(square(EX, y, ES, n, l, 40, l2))
    else:
        ext.append(badge_square(EX, y, ES, args[0], args[1], args[2], args[3]))

# ── 화살표
edge('HTTPS', user, front, 1, fr(uy+45,uy,uy+US), 0, fr(uy+45,FY,FY+FH))
edge('분석 결과', front, user, 0, fr(uy+85,FY,FY+FH), 1, fr(uy+85,uy,uy+US))
edge('계약서 · 페르소나', front, back, 1, fr(BY+30,FY,FY+FH), 0, 0.3)
edge('조항별 결과', back, front, 0, 0.7, 1, fr(BY+70,FY,FY+FH))
edge('암호문 저장', back, db, 1, 0.3, 0, 0.3)
edge('기록 조회', db, back, 0, 0.7, 1, 0.7)
edge('원문 · 페르소나 (서비스 토큰)', back, agent, 0.3, 1, fr(BX+S*0.3,AX,AX+AW), 0, offset=(-95,0))
edge('조항별 결과 스트림', agent, back, fr(BX+S*0.7,AX,AX+AW), 0, 0.7, 1, offset=(62,0))
for a,b,l in [(n_mask,n_inj,'마스킹'),(n_inj,n_par,'정제'),(n_par,n_dom,'조항'),(n_dom,n_ana,'유형'),(n_ana,n_cit,'출력')]:
    edge(l, a, b, 1, 0.5, 0, 0.5, fsize=10.5, lcolor='#6b7280', offset=(0,-13))
edge('검증된 출력', n_cit, n_per, 0.5, 1, 0.5, 0, fsize=11, lcolor='#6b7280')
for a,b,l in [(n_per,n_jud,'재작성'),(n_jud,n_gate,'점수'),(n_gate,n_out,'통과')]:
    edge(l, a, b, 0, 0.5, 1, 0.5, fsize=10.5, lcolor='#6b7280', offset=(0,-13))
for i,l in enumerate(['생성','채점','OCR','STT']):
    yc = AY + i*(ES+14) + ES/2
    edge(l, agent, ext[i], 1, fr(yc,AY,AY+AH), 0, 0.5, fsize=12)
O = '#EE8A3C'
edge('원문에 없는 인용 → 재시도, 소진 시 주의 강등', n_cit, n_ana, 0.5, 0, 0.5, 0, [(xs[5]+NW/2, R1-50), (xs[4]+NW/2, R1-50)], O, True, '#c96a1e', 11)
edge('Faithfulness · Risk Coverage 미달', n_gate, n_ana, 0.5, 0, 0.5, 1, [(xs[3]+NW/2, R2-54), (xs[4]+NW/2, R2-54)], O, True, '#c96a1e', 11)
edge('Clarity만 미달 (최대 2회, 소진 시 재검토 플래그)', n_gate, n_per, 0.5, 1, 0.5, 1, [(xs[3]+NW/2, R2+124), (xs[5]+NW/2, R2+124)], O, True, '#c96a1e', 11)

W, H = 1460, 900
xml = (f'<mxfile host="app.diagrams.net" agent="half-fifty build_drawio.py">'
       f'<diagram id="arch" name="시스템 아키텍처"><mxGraphModel dx="{W}" dy="{H}" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{W}" pageHeight="{H}" background="#ffffff" math="0" shadow="0">'
       '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + ''.join(cells) + '</root></mxGraphModel></diagram></mxfile>')
pathlib.Path('시스템_아키텍처_보고서용.drawio' if REPORT else '시스템_아키텍처.drawio').write_text(xml, encoding='utf-8')
print('cells', len(cells))
