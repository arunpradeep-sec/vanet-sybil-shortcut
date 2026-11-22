import subprocess, docx, json, re, sys
sys.path.insert(0,'/home/claude/an')
from trimmap import mapsec
from docx.shared import Emu
def run(c): print(c); subprocess.run(c,shell=True,check=True)
run('python3 trim.py'); run('python3 trim2.py')
f='/mnt/user-data/outputs/Sybil_VANET_manuscript_submission.docx'
d=docx.Document(f)
for sh in d.inline_shapes:
    w=sh.width/914400; r=5.6/w if w>6.0 else (4.1/w if w>4.3 else 1)
    sh.width=Emu(int(sh.width*r)); sh.height=Emu(int(sh.height*r))
a=[p for p in d.paragraphs if p.text.startswith('Every result so far uses a threshold')][0]
b=[p for p in d.paragraphs if p.text.startswith('Fig. S17 gives the confusion')][0]
moved_thr=[a.text,b.text]
a.text='Every result so far uses a threshold chosen on validation data. In-domain the exact threshold is not critical: MCC stays within 84–88% (Extension) and 98.5–98.8% (NextGen) for any τ between 0.2 and 0.8. From Extension to NextGen it matters (MCC 84–92% over the same interval), and from NextGen to Extension even the best threshold in hindsight reaches only 54.7% MCC (Supplementary Figs. S16 and S17).'
b._element.getparent().remove(b._element)
d.save(f)
m=json.load(open('moved.json'))
S=docx.Document('/mnt/user-data/outputs/Sybil_VANET_supplementary.docx')
S.add_page_break(); S.add_heading('Supplementary text',1)
S.add_paragraph('The following passages were shortened in the main article; they are given here in full.')
for title,paras in m:
    S.add_heading(title,2)
    for t in paras: S.add_paragraph(mapsec(t))
S.add_heading('Section 7.15 (submission numbering; full text): threshold sweep and confusion matrices',2)
for t in moved_thr: S.add_paragraph(t)
S.save('/mnt/user-data/outputs/Sybil_VANET_supplementary.docx')
run('python3 svgembed.py')
run('python3 alg/fixalg.py /mnt/user-data/outputs/Sybil_VANET_manuscript_submission.docx /mnt/user-data/outputs/Sybil_VANET_manuscript_final.docx')
