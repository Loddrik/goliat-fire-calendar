import re
s=open('marca.src.html').read()
m=open('mark.js').read()
b=re.sub(r'<\?xml.*?\?>','',open('spaceapps/Space Apps Logo Color and Black.svg').read().strip())
w=re.sub(r'<\?xml.*?\?>','',open('spaceapps/Space Apps Logo Color and White.svg').read().strip()).replace('clip0_','clipw_')
open('opciones-logo.html','w').write(s.replace('%%MARKJS%%',m).replace('%%SA_BLACK%%',b).replace('%%SA_WHITE%%',w))
