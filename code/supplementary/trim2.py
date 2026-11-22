import docx,re,json,sys
sys.path.insert(0,'/home/claude/an')
from runsub import sub_par
from docx.text.paragraph import Paragraph
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
f='/mnt/user-data/outputs/Sybil_VANET_manuscript_submission.docx'
d=docx.Document(f); body=d.element.body; kids=list(body.iterchildren())
txt=lambda el: Paragraph(el,d).text if el.tag==W+'p' else ''
def idx(start):
    for i,el in enumerate(kids):
        if txt(el).startswith(start): return i
    raise Exception(start)
moved=[]
i=idx('Nomenclature'); rm=[i,i+1]; assert kids[i+1].tag==W+'tbl'
a=idx('7.14 Is the transfer gap'); b=idx('7.15 Which features')
moved.append(('Is the transfer gap a tuning problem? (hyperparameter analysis, shortened in the main article)',[txt(kids[j]) for j in range(a+1,b) if txt(kids[j])]))
rm+=list(range(a,b))
p=Paragraph(kids[idx('Fig. 13 trains HGB')],d)
p.add_run(' Tuning does not help either: over a grid of 12 HGB configurations (50–600 iterations, learning rate 0.03–0.3), NextGen-to-Extension MCC stays between 36.5% and 40.4%, while every in-domain configuration lies within 1.8 points of the best (Supplementary Fig. S15).')
a=idx('7.18 Robustness to sensor noise'); b=idx('7.19 Combining the remedies')
moved.append(('Section 7.17 (full text): Robustness to sensor noise',[txt(kids[j]) for j in range(a+1,b) if txt(kids[j])]))
Paragraph(kids[a+1],d).text='Perturbing the eleven continuous physical features of test messages with multiplicative Gaussian noise of up to 10% lowers MCC by at most 0.6 points in every setting; at 30% noise, TPR@1%FPR on Extension falls by 12 points (Supplementary Fig. S18). Robustness to sensor noise is therefore not the limiting factor; robustness to a different attack implementation is.'
rm+=list(range(a+2,b))
a=idx('8.5 Threats to validity in more detail'); b=idx('8.6 Placing the detector')
moved.append(('Threats to validity in more detail (moved from the main article)',[txt(kids[j]) for j in range(a+1,b) if txt(kids[j])]))
rm+=list(range(a,b))
for j in sorted(set(rm),reverse=True): body.remove(kids[j])
# full -> submission section numbers (7.14 removed; 8.5 moved to the supplement)
H={'7.15':'7.14','7.16':'7.15','7.17':'7.16','7.18':'7.17','7.19':'7.18','7.20':'7.19','7.21':'7.20','8.6':'8.5','8.7':'8.6'}
PAT=r'(?<![\d.])(7\.1[5-9]|7\.2[01]|8\.[67])(?![\d])'
def mapsec(t): return re.sub(PAT,lambda m:H[m.group(1)],t)
for el in body.iter(W+'p'):
    p=Paragraph(el,d)
    sub_par(p,PAT,lambda m:H[m.group(1)])
    sub_par(p,r'Sections 7\.12–7\.19(?! and)',lambda m:'Sections 7.12–7.19 and the Supplementary material')
d.save(f)
json.dump(moved,open('/home/claude/an/moved.json','w'))
print('ok')
