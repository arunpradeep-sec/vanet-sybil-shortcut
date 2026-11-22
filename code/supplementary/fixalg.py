import docx, re, copy, sys, zipfile
from lxml import etree
from docx.shared import Pt, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH
eqx=zipfile.ZipFile('/home/claude/an/alg/eq.docx').read('word/document.xml')
eqroot=etree.fromstring(eqx); M='http://schemas.openxmlformats.org/officeDocument/2006/math'
omath=eqroot.find('.//{%s}oMath'%M)
TITLE='Receiver-side feature extraction for one received message'
INPUT=[('Input: ','message m = (p, t, x, y, v, a, θ, σ_{pos}, σ_{v}): pseudonym, time, position, speed, acceleration, heading, position and speed noise; receiver position r; history H[p] of pseudonym p; buffer B of messages received in the last 5 s'),
       ('Output: ','feature vector f ∈ ℝ^{21}')]
L=['d ← ‖(x, y) − r‖',
 'f_{KIN} ← (v, |a|, ‖σ_{pos}‖, ‖σ_{v}‖, d)',
 '**if** H[p] = ∅ **then**   ▷ first message heard from p',
 '>(Δt, jump, e_{pred}, v̇, e_{θ}) ← (−1, −1, −1, −1, −1)   ▷ sentinels: no history',
 '>msg_idx ← 0;  age ← 0;  is_new ← 1;  d_{first} ← d;  t_{first}(p) ← t',
 '**else**',
 '>j ← last message in H[p];  Δt ← t − t_{j}',
 '>jump ← ‖(x, y) − (x_{j}, y_{j})‖;  e_{pred} ← Eq. (1);  v̇ ← |v − v_{j}| / Δt',
 '>e_{θ} ← |θ − bearing of (x − x_{j}, y − y_{j})| **if** jump > 1 m, **else** −1',
 '>msg_idx ← |H[p]|;  age ← t − t_{first}(p);  is_new ← 0;  d_{first} ← d at t_{first}(p)',
 '**end if**',
 'f_{HIST} ← (Δt, jump, e_{pred}, v̇, e_{θ}, msg_idx, age, is_new, d_{first})',
 'B_{1} ← messages in B ∪ {m} received in (t − 1 s, t];  N ← {k ∈ B_{1} : p_{k} ≠ p}',
 'n_{ps} ← number of distinct pseudonyms in B_{1}',
 '**if** N ≠ ∅ **then** d_{k} ← ‖(x_{k}, y_{k}) − (x, y)‖ for k ∈ N;  d_{min} ← min_{k} d_{k}',
 '**else** d_{min} ← 1000 m   ▷ sentinel: no neighbour heard',
 'n_{5} ← |{k ∈ N : d_{k} < 5 m}|;  n_{20} ← |{k ∈ N : d_{k} < 20 m}|',
 'n_{sim} ← |{k ∈ N : d_{k} < 20 m and |v_{k} − v| < 0.5 m/s}|',
 'k_{new} ← number of first messages (is_new = 1) in B ∪ {m}',
 'r_{new} ← k_{new} / max(1, number of distinct pseudonyms in B ∪ {m})',
 'f_{NEIGH} ← (n_{ps}, n_{5}, n_{20}, d_{min}, k_{new}, r_{new}, n_{sim})',
 'append m to H[p] and B;  remove messages older than 5 s from B',
 '**return** f ← (f_{KIN}, f_{HIST}, f_{NEIGH})']
TOK=re.compile(r'(\*\*[^*]+\*\*|_\{[^}]+\}|\^\{[^}]+\}|▷[^▷]*$)')
def addrich(p,s,size=9.5):
    for part in TOK.split(s):
        if not part: continue
        if part.startswith('**'): r=p.add_run(part[2:-2]); r.bold=True
        elif part.startswith('_{'): r=p.add_run(part[2:-1]); r.font.subscript=True
        elif part.startswith('^{'): r=p.add_run(part[2:-1]); r.font.superscript=True
        elif part.startswith('▷'): r=p.add_run('   '+part); r.italic=True
        else: r=p.add_run(part)
        r.font.size=Pt(size); r.font.name='Times New Roman'
def border(cell,top=None,bottom=None):
    tcPr=cell._tc.get_or_add_tcPr(); b=OxmlElement('w:tcBorders')
    for side,val in (('top',top),('bottom',bottom),('left',None),('right',None)):
        e=OxmlElement(f'w:{side}')
        if val: e.set(qn('w:val'),'single'); e.set(qn('w:sz'),str(val)); e.set(qn('w:color'),'000000')
        else: e.set(qn('w:val'),'nil')
        b.append(e)
    tcPr.append(b)
def fix(path):
    d=docx.Document(path); body=d.element.body
    eqp=[p for p in d.paragraphs if p.text.startswith('e_{\\mathrm{pred}}')]
    algp=[p for p in d.paragraphs if p.text.startswith('Algorithm 1. Receiver-side')]
    for p in eqp:
        np_=OxmlElement('w:p'); p._p.addprevious(np_)
        from docx.text.paragraph import Paragraph
        P=Paragraph(np_,p._parent); P.alignment=WD_ALIGN_PARAGRAPH.CENTER
        np_.append(copy.deepcopy(omath)); r=P.add_run('\t\t(1)'); r.font.size=Pt(11)
        # right tab stop
        P.paragraph_format.tab_stops.add_tab_stop(Inches(6.2),alignment=2)
        p._p.getparent().remove(p._p)
    for p in algp:
        t=d.add_table(rows=1,cols=1); t.autofit=True
        c=t.cell(0,0); border(c,top=12,bottom=8)
        h=c.paragraphs[0]; r=h.add_run('Algorithm 1. '); r.bold=True; r.font.size=Pt(10); r.font.name='Times New Roman'
        r=h.add_run(TITLE); r.font.size=Pt(10); r.font.name='Times New Roman'
        c2=t.add_row().cells[0]; border(c2,top=8,bottom=12)
        first=True
        for lab,txt in INPUT:
            q=c2.paragraphs[0] if first else c2.add_paragraph(); first=False
            q.paragraph_format.left_indent=Inches(0.6); q.paragraph_format.first_line_indent=Inches(-0.6)
            rr=q.add_run(lab); rr.bold=True; rr.font.size=Pt(9.5); rr.font.name='Times New Roman'; addrich(q,txt)
        for i,line in enumerate(L,1):
            q=c2.add_paragraph(); ind=0
            while line.startswith('>'): ind+=1; line=line[1:]
            q.paragraph_format.space_after=Pt(0); q.paragraph_format.space_before=Pt(0)
            q.paragraph_format.left_indent=Inches(0.35+0.3*ind); q.paragraph_format.first_line_indent=Inches(-0.35-0.3*ind)
            rn=q.add_run(f'{i:>2}:'+'\t'*0 + ' '*(1) + '    '*ind*1); rn.font.size=Pt(9.5); rn.font.name='Times New Roman'
            addrich(q,line)
        for cp in c.paragraphs+c2.paragraphs: cp.paragraph_format.space_after=Pt(1)
        p._p.addprevious(t._tbl); p._p.getparent().remove(p._p)
    d.save(path); print(path,len(eqp),len(algp))
for f in sys.argv[1:]: fix(f)
