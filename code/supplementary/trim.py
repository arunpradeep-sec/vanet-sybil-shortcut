import docx, re, copy
from docx.shared import Inches, Pt
from docx.text.paragraph import Paragraph
from docx.enum.text import WD_ALIGN_PARAGRAPH
SRC='/mnt/user-data/outputs/Sybil_VANET_manuscript_final.docx'
F='/home/claude/an/f300/'
MAIN={1:1,2:2,3:3,5:4,9:5,10:6,12:7,16:8,17:9,20:10,21:11,25:12,27:13,29:14,31:15,33:16}
SUPP={4:1,6:2,7:3,8:4,11:5,13:6,14:7,15:8,18:9,19:10,22:11,23:12,24:13,26:14,28:15,30:16,32:17,34:18}
def lab(n):
    if n in MAIN: return (0,MAIN[n])
    return (1,SUPP[n])
def fmt(items,suf):
    # items: list of (kind,num); compress
    out=[]
    for kind in (0,1):
        nums=sorted(set(n for k,n in items if k==kind)); pre='' if kind==0 else 'S'
        i=0
        while i<len(nums):
            j=i
            while j+1<len(nums) and nums[j+1]==nums[j]+1: j+=1
            if j>=i+2: out.append(f'{pre}{nums[i]}–{pre}{nums[j]}')
            else: out.extend(f'{pre}{x}' for x in nums[i:j+1])
            i=j+1
    n_items=len(set(items))
    head='Figs. ' if n_items>1 else 'Fig. '
    if len(out)>1: s=', '.join(out[:-1])+(' and ' if len(out)==2 else ', ')+out[-1]
    else: s=out[0]
    return head+s+suf
PAT=re.compile(r'Figs?\.\s?(\d+)((?:\([a-z]\))?)((?:\s*(?:,|–|-|and)\s*\d+(?:\([a-z]\))?)*)')
def repl(m):
    first=int(m.group(1)); suf1=m.group(2); rest=m.group(3)
    nums=[first]; parts=re.findall(r'(,|–|-|and)\s*(\d+)',rest)
    prev=first; rng=False
    for sep,v in parts:
        v=int(v)
        if sep in '–-': nums.extend(range(prev+1,v+1))
        else: nums.append(v)
        prev=v
    items=[lab(n) for n in nums]
    suf=suf1 if len(nums)==1 else ''
    return fmt(items,suf)
def fix_par(p):
    runs=p.runs; text=''.join(r.text for r in runs)
    if not PAT.search(text): return
    # rebuild per match with run-aware splice
    pos=[];acc=0
    for r in runs: pos.append(acc); acc+=len(r.text)
    for m in reversed(list(PAT.finditer(text))):
        s,e=m.start(),m.end(); new=repl(m)
        # find run containing s
        ri=max(i for i,p0 in enumerate(pos) if p0<=s and (len(runs[i].text)>0 or p0<s+1))
        for i,r in enumerate(runs):
            a=pos[i]; b=a+len(r.text)
            if b<=s or a>=e: continue
            t=r.text; ls=max(s,a)-a; le=min(e,b)-a
            if a<=s<b or (i==ri and a==s): r.text=t[:ls]+new+t[le:]; ri=-1
            else: r.text=t[:ls]+t[le:]
        text=''.join(r.text for r in runs); pos=[];acc=0
        for r in runs: pos.append(acc); acc+=len(r.text)
d=docx.Document(SRC); body=d.element.body; kids=list(body.iterchildren())
P=lambda i: Paragraph(kids[i],d)
supp_items={1:[98,99,100],2:[114,115,116],3:[117,118,119,120],4:[122,123,124],5:[142,143,144],6:[152,153,154],7:[171,172,173],8:[179,180,181],
 9:[202,203,204],10:[209,210,211],11:[231,232,233],12:[239,240,241],13:[246,247,248],14:[260,261],15:[268,269],16:[277,278],17:[283,284],18:[296,297]}
supp_files={1:'R1_dataset_composition',2:'A1b_violins',3:'A3_correlation',4:'A12_pca',5:'S4_online_state',6:'S3_protocol_matrix',7:'R2_main_results',8:'R3_recall_heatmap',9:'R4_ablation_heatmap',10:'R5_shortcut_fixes',11:'R6_seen_unseen_models',12:'R7_latency',13:'F24_phantom_bars',14:'A5_model_zoo',15:'A6_hparam',16:'A7_threshold_sweep',17:'A10_confusion',18:'A16_noise'}
# sanity checks
for k,ids in supp_items.items():
    caps=[i for i in ids if P(i).text.startswith('Fig. ')]
    assert any(re.match(r'Fig\. \d+\.',P(i).text) for i in ids),(k,[P(i).text[:30] for i in ids])
# collect supplement content (before renumber, renumber texts later on the new doc)
supp=[]
for k,ids in supp_items.items():
    cap=[P(i).text for i in ids if re.match(r'Fig\. \d+\.',P(i).text)][0]
    desc=[P(i).text for i in ids if P(i).text and not re.match(r'Fig\. \d+\.',P(i).text) and not kids[i].xpath('.//w:drawing') and '·' not in P(i).text]
    supp.append((k,cap,desc))
img_main={66:('F01_architecture',6.3),72:('S1_system_model',6.3),78:('S2_attack_types',6.3),113:('A1_feature_auc_shift',6.3),127:('A2_domain_classifier',4.5),131:('F10_feature_hierarchy',6.3),148:('F12_pipeline',6.3),185:('F16_roc',4.6),191:('F17_group_importance',4.6),215:('F20_loto',4.6),223:('F21_precision_prevalence',4.6),254:('R8_phantom_curves',6.3),265:('A4_learning_curve',4.2),274:('A13_importance_topk',6.3),281:('A8_pr_calibration',6.3),293:('A11_delay_pseudonym',6.3)}
for i,(f,w) in img_main.items():
    p=P(i); assert kids[i].xpath('.//w:drawing'),i
    for r in list(p.runs): r._element.getparent().remove(r._element)
    p.add_run().add_picture(F+f+'.png',width=Inches(w)); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
remove=set(i for ids in supp_items.values() for i in ids)|{67,132,149,186,192,216,224}
for i in sorted(remove,reverse=True): body.remove(kids[i])
# heading renumber 4.5.4 -> 4.5.3
for p in d.paragraphs:
    if p.text.startswith('4.5.4 Global shift'):
        for r in p.runs:
            if '4.5.4' in r.text: r.text=r.text.replace('4.5.4','4.5.3')
    if p.text.startswith('Further analyses.'):
        p.add_run(' Additional figures (Figs. S1–S18) are given in the Supplementary material.')
# renumber everywhere (body + tables)
for el in body.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
    p=Paragraph(el,d)
    if 'Figs. S1–S18' in p.text: continue
    fix_par(p)
d.save('/mnt/user-data/outputs/Sybil_VANET_manuscript_submission.docx')
# supplement
title=[p.text for p in docx.Document(SRC).paragraphs][0]
S=docx.Document(); st=S.styles['Normal']; st.font.name='Times New Roman'; st.font.size=Pt(11)
S.add_heading('Supplementary material',0)
S.add_paragraph(title).runs[0].bold=True
S.add_paragraph('Nitha C. Velayudhan, Arun Pradeep, Mukesh Madanan')
S.add_paragraph('This file contains Figs. S1–S18, which support the results in the main text. Section and table numbers refer to the main article. Data and code: github.com/arunpradeep-sec/vanet-sybil-shortcut.')
def ren(t):
    class Q: pass
    return PAT.sub(repl,t)
for k,cap,desc in supp:
    S.add_paragraph().add_run().add_picture(F+supp_files[k]+'.png',width=Inches(6.3)); S.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
    c=ren(cap); m=re.match(r'(Figs?\. S?\d+\.)(.*)',c,re.S); para=S.add_paragraph(); r=para.add_run(m.group(1)); r.bold=True; para.add_run(m.group(2))
    for t in desc:
        S.add_paragraph(ren(t))
S.save('/mnt/user-data/outputs/Sybil_VANET_supplementary.docx')
print('done')
