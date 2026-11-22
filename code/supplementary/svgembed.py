import docx, copy
from docx.opc.part import Part
from docx.opc.packuri import PackURI
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from lxml import etree
A='http://schemas.openxmlformats.org/drawingml/2006/main'; R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
SV='http://schemas.microsoft.com/office/drawing/2016/SVG/main'
main=['F01_architecture','S1_system_model','S2_attack_types','A1_feature_auc_shift','A2_domain_classifier','F10_feature_hierarchy','F12_pipeline','F16_roc','F17_group_importance','F20_loto','F21_precision_prevalence','R8_phantom_curves','A4_learning_curve','A13_importance_topk','A8_pr_calibration','A11_delay_pseudonym','R9_robust_ablation','R10_adaptive_attacker']
supp=['R1_dataset_composition','A1b_violins','A3_correlation','A12_pca','S4_online_state','S3_protocol_matrix','R2_main_results','R3_recall_heatmap','R4_ablation_heatmap','R5_shortcut_fixes','R6_seen_unseen_models','R7_latency','F24_phantom_bars','A5_model_zoo','A6_hparam','A7_threshold_sweep','A10_confusion','A16_noise']
def embed(path,names,tag):
    d=docx.Document(path); blips=d.element.body.findall('.//{%s}blip'%A)
    assert len(blips)==len(names),(len(blips),len(names))
    for k,(b,n) in enumerate(zip(blips,names)):
        part=Part(PackURI(f'/word/media/{tag}_svg{k+1}.svg'),'image/svg+xml',open(f'/home/claude/an/figs/{n}.svg','rb').read(),d.part.package)
        rid=d.part.relate_to(part,RT.IMAGE)
        ext=b.find('{%s}extLst'%A)
        if ext is None: ext=etree.SubElement(b,'{%s}extLst'%A)
        e=etree.SubElement(ext,'{%s}ext'%A); e.set('uri','{96DAC541-7B7A-43D3-8B79-37D633B846F1}')
        s=etree.SubElement(e,'{%s}svgBlip'%SV,nsmap={'asvg':SV}); s.set('{%s}embed'%R,rid)
    d.save(path); print(path,len(blips))
embed('/mnt/user-data/outputs/Sybil_VANET_manuscript_submission.docx',main,'m')
embed('/mnt/user-data/outputs/Sybil_VANET_supplementary.docx',supp,'s')
