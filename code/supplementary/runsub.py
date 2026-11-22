import re
def sub_par(p, pat, fn):
    """regex-substitute over a paragraph's full text, splicing into runs (keeps run formatting)."""
    runs=p.runs; text=''.join(r.text for r in runs)
    ms=list(re.finditer(pat,text))
    if not ms: return False
    changed=False
    for m in reversed(ms):
        new=fn(m)
        if new==m.group(0): continue
        changed=True
        s,e=m.start(),m.end(); acc=0; placed=False
        for r in runs:
            a=acc; b=a+len(r.text); acc=b
            if b<=s and not (a==b==s): continue
            if a>=e and placed: break
            t=r.text; ls=max(s,a)-a; le=max(0,min(e,b)-a)
            if not placed and a<=s<=b and (s<b or b==e or len(t)==0 or b==s and e==s):
                nt=t[:ls]+new+t[le:]; placed=True
            else: nt=t[:ls]+t[le:]
            if nt!=t: r.text=nt
    return changed
