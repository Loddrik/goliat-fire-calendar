import sys,glob,os,html
# uso: python3 hoja.py <carpeta> <titulo> -> <carpeta>/hoja.html (un cuadro por cada 12 imágenes)
d,t=sys.argv[1],sys.argv[2]
imgs=sorted(f for f in glob.glob(f"{d}/*") if f.endswith('.svg') or (f.endswith('.png') and not f.endswith('.svg.png')) or f.endswith('.jpg'))
secs=[]
for k in range(0,len(imgs),12):
    figs=''.join(f'<figure><img src="{os.path.basename(f)}"><figcaption>{html.escape(os.path.basename(f).split("-recraft")[0].split("-nano")[0])}</figcaption></figure>' for f in imgs[k:k+12])
    secs.append(f'<section class="slide" id="s{k//12+1}"><h1>{html.escape(t)}</h1><div class="g">{figs}</div></section>')
open(f"{d}/hoja.html","w").write(f'''<!doctype html><meta charset="utf-8"><meta name="lienzo" content="1080x1350"><style>
*{{margin:0;box-sizing:border-box}}.slide{{width:1080px;height:1350px;background:#FBF8F2;padding:72px;font-family:monospace}}
h1{{font-size:36px;color:#0B2545;margin-bottom:24px}}.g{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
figure{{background:#fff;border:1px solid #ddd;border-radius:10px;padding:8px;text-align:center}}img{{width:100%;height:236px;object-fit:contain}}
figcaption{{font-size:20px;color:#0B2545}}</style>{''.join(secs)}''')
print(len(imgs))
