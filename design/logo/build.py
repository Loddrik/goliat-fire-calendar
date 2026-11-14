import re
old=open('opciones-logo.src.html').read()
head=old[:old.index('</style>')+len('</style>')]
body=open('v2-body.html').read()
b=re.sub(r'<\?xml.*?\?>','',open('spaceapps/Space Apps Logo Color and Black.svg').read().strip())
w=re.sub(r'<\?xml.*?\?>','',open('spaceapps/Space Apps Logo Color and White.svg').read().strip()).replace('clip0_','clipw_')
open('opciones-logo.html','w').write((head+'\n'+body).replace('%%SA_BLACK%%',b).replace('%%SA_WHITE%%',w))
