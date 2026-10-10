#!/usr/bin/env python3
"""يتحقق من صحة content.json قبل نشره. الاستخدام: python3 scripts/validate_content.py content.json"""
import json, re, sys

CONTR = [("i'm","i am"),("you're","you are"),("it's","it is"),("that's","that is"),("what's","what is"),("he's","he is"),("she's","she is"),
         ("we're","we are"),("they're","they are"),("don't","do not"),("doesn't","does not"),("didn't","did not"),("can't","can not"),
         ("cannot","can not"),("won't","will not"),("isn't","is not"),("aren't","are not"),("shouldn't","should not"),("i'd","i would"),
         ("i'll","i will"),("we'll","we will"),("i've","i have"),("o'clock","o clock"),("let's","let us")]
def tnorm(s):
    s = str(s or '').lower().replace('’', "'")
    for a, b in CONTR: s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9' ]+", ' ', s).replace("'", '')
    return re.sub(r'\s+', ' ', s).strip()
def tok_eq(w, k): return w == k or (len(k) >= 3 and (w.startswith(k) or w.endswith(k)))
def thas(t, ph):
    T, P = t.split(' '), [x for x in ph.split(' ') if x]
    return bool(P) and any(all(tok_eq(T[i+j], k) for j, k in enumerate(P)) for i in range(len(T) - len(P) + 1))
def tmatch(raw, keys):
    vs = [tnorm(raw), tnorm(re.sub(r"['’]s\b", ' is', str(raw), flags=re.I))]
    return any(t and any(all(thas(t, tnorm(p)) for p in g.split('+')) for g in keys.split('|')) for t in vs)

errors = []
def err(where, msg): errors.append(f'{where}: {msg}')
def check_choices(where, c, a, n=4):
    if not isinstance(c, list) or len(c) != n: err(where, f'يجب أن تكون الخيارات {n}'); return
    if len(set(map(str, c))) != len(c): err(where, 'خيارات مكررة')
    if not isinstance(a, int) or not 0 <= a < len(c): err(where, 'رقم الإجابة غير صحيح')
    if any(not str(x).strip() for x in c): err(where, 'خيار فارغ')
def grade_ok(where, g, lo=1, hi=12):
    if not isinstance(g, int) or not lo <= g <= hi: err(where, f'الصف يجب أن يكون بين {lo} و{hi}')

def main(path):
    pk = json.load(open(path, encoding='utf-8'))
    if not pk.get('version'): err('version', 'مفقود')
    seen = set()
    for g, terms in pk.get('vocab', {}).items():
        grade_ok(f'vocab[{g}]', int(g))
        for t, lst in terms.items():
            if t not in ('1', '2'): err(f'vocab[{g}]', 'الفصل يجب أن يكون 1 أو 2')
            for w in lst:
                parts = w.split('|')
                if len(parts) != 3 or not all(p.strip() for p in parts): err(f'vocab[{g}][{t}] {w}', 'الصيغة: word|معنى|example'); continue
                k = (g, parts[0].lower())
                if k in seen: err(f'vocab[{g}] {parts[0]}', 'كلمة مكررة في نفس الصف')
                seen.add(k)
                if parts[0].lower() not in parts[2].lower().replace(',', ' ').replace('.', ' ') and parts[0].split()[0].lower() not in parts[2].lower():
                    err(f'vocab[{g}] {parts[0]}', 'المثال لا يحتوي الكلمة')
    qs = set()
    for i, x in enumerate(pk.get('grammar', [])):
        w = f'grammar[{i}] {x.get("q","")[:30]}'; grade_ok(w, x.get('g')); check_choices(w, x.get('c'), x.get('a'))
        if '___' not in x.get('q', ''): err(w, 'السؤال يجب أن يحتوي ___')
        if not x.get('ex'): err(w, 'الشرح مفقود')
        if x.get('q') in qs: err(w, 'سؤال مكرر')
        qs.add(x.get('q'))
    for i, r in enumerate(pk.get('reading', [])):
        w = f'reading[{i}] {r.get("t")}'; grade_ok(w, r.get('g'))
        if len(r.get('p', '')) < 60: err(w, 'النص قصير جداً')
        if len(r.get('qs', [])) < 3: err(w, '3 أسئلة على الأقل')
        for j, (q, c, a, *_) in enumerate(r.get('qs', [])): check_choices(f'{w} q{j}', c, a)
    sq = set()
    for i, x in enumerate(pk.get('science', [])):
        w = f'science[{i}] {str(x[2])[:30] if len(x) > 2 else ""}'
        if len(x) != 6: err(w, 'الصيغة: [صف, مادة, سؤال, خيارات, رقم الإجابة, شرح]'); continue
        grade_ok(w, x[0])
        if x[1] not in ('phy', 'chem', 'bio', 'earth'): err(w, 'المادة: phy أو chem أو bio أو earth')
        check_choices(w, x[3], x[4])
        if x[2] in sq: err(w, 'سؤال مكرر')
        sq.add(x[2])
    ids = set()
    for i, t in enumerate(pk.get('talks', [])):
        w = f'talks[{t.get("id")}]'; grade_ok(w, t.get('g'))
        if t.get('id') in ids: err(w, 'معرّف مكرر')
        ids.add(t.get('id'))
        if len(t.get('turns', [])) < 3: err(w, '3 جمل على الأقل')
        for j, tr in enumerate(t.get('turns', [])):
            if len(tr) != 5: err(f'{w} turn{j}', 'الصيغة: [كلام التطبيق, الترجمة, التلميح, الإجابة النموذجية, الكلمات المقبولة]'); continue
            if not tmatch(tr[3], tr[4]): err(f'{w} turn{j}', f'الإجابة النموذجية لا تطابق الكلمات المقبولة: {tr[3]}')
    for k, rows in pk.get('verbal', {}).items():
        if k not in ('anal', 'comp', 'err', 'odd'): err(f'verbal.{k}', 'نوع غير معروف')
        for i, r in enumerate(rows):
            w = f'verbal.{k}[{i}]'
            if len(r) != 5: err(w, 'الصيغة: [مستوى 1-3, سؤال, خيارات, رقم الإجابة, شرح]'); continue
            grade_ok(w, r[0], 1, 3); check_choices(w, r[2], r[3])
            if k == 'err' and any(c not in r[1] for c in r[2]): err(w, 'كل خيار يجب أن يكون كلمة من الجملة')
    for i, r in enumerate(pk.get('rc', [])):
        w = f'rc[{i}]'; grade_ok(w, r.get('d'), 1, 3)
        for j, (q, c, a, *_) in enumerate(r.get('qs', [])): check_choices(f'{w} q{j}', c, a)
    if errors:
        print(f'وُجدت {len(errors)} مشكلة:'); [print(' -', e) for e in errors]; sys.exit(1)
    print('المحتوى سليم ✓')

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'content.json')
