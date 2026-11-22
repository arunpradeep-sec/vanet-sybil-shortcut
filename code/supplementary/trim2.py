import docx,re
from docx.text.paragraph import Paragraph
from docx.shared import Inches,Pt
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
f='/mnt/user-data/outputs/Sybil_VANET_manuscript_submission.docx'
d=docx.Document(f); body=d.element.body; kids=list(body.iterchildren())
txt=lambda el: Paragraph(el,d).text if el.tag==W+'p' else ''
def idx(start):
    for i,el in enumerate(kids):
        if txt(el).startswith(start): return i
    raise Exception(start)
moved=[]
# 1 nomenclature: paragraph + table
i=idx('Nomenclature'); rm=[i,i+1]; assert kids[i+1].tag==W+'tbl'
# 2 section 7.14 -> one sentence appended to 7.13 paragraph
a=idx('7.14 Is the transfer gap'); b=idx('7.15 Which features')
moved.append(('Section 7.14 (full text): Is the transfer gap a tuning problem?',[txt(kids[j]) for j in range(a+1,b) if txt(kids[j])]))
rm+=list(range(a,b))
p=Paragraph(kids[idx('Fig. 13 trains HGB')],d)
p.add_run(' Tuning does not help either: over a grid of 12 HGB configurations (50–600 iterations, learning rate 0.03–0.3), NextGen-to-Extension MCC stays between 36.0% and 38.7%, while every in-domain configuration lies within 2.1 points of the best (Supplementary Fig. S15).')
# 3 section 7.18 noise -> short paragraph
a=idx('7.18 Robustness to sensor noise'); b=idx('7.19 Summary of findings')
moved.append(('Section 7.18 (full text): Robustness to sensor noise',[txt(kids[j]) for j in range(a+1,b) if txt(kids[j])]))
Paragraph(kids[a+1],d).text='Perturbing the eleven continuous physical features of test messages with multiplicative Gaussian noise of up to 10% lowers MCC by at most 0.5 points in every setting; at 30% noise, TPR@1%FPR on Extension falls by 9 points (Supplementary Fig. S18). Robustness to sensor noise is therefore not the limiting factor; robustness to a different attack implementation is.'
rm+=list(range(a+2,b))
# 4 section 8.5 -> supplement
a=idx('8.5 Threats to validity in more detail'); b=idx('8.6 Placing the detector')
moved.append(('Section 8.5 (full text): Threats to validity in more detail',[txt(kids[j]) for j in range(a+1,b) if txt(kids[j])]))
rm+=list(range(a,b))
for j in sorted(set(rm),reverse=True): body.remove(kids[j])
# renumber headings 7.15->7.14 ... 7.19->7.17 ; 8.6->8.5, 8.7->8.6 and in-text section refs
hmap={'7.15':'7.14','7.16':'7.15','7.17':'7.16','7.18':None,'7.19':'7.17','8.6':'8.5','8.7':'8.6'}
for el in body.iter(W+'p'):
    p=Paragraph(el,d)
    for r in p.runs:
        t=r.text
        t=re.sub(r'Sections 7\.12–7\.18','Sections 7.12–7.16 and the Supplementary material',t)
        t=re.sub(r'\b(7\.1[5-9]|8\.[67])\b',lambda m: hmap[m.group(1)] or m.group(1),t)
        if t!=r.text: r.text=t
d.save(f)
import json; json.dump(moved,open('/home/claude/an/moved.json','w'))
print('ok')
