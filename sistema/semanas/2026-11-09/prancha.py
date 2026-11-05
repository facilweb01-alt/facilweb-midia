import sys,glob,os
from PIL import Image,ImageDraw,ImageFont
d=sys.argv[1]; out=sys.argv[2]
fs=sorted(glob.glob(f'saida/{d}/carrossel*.jpg'))+sorted(glob.glob(f'saida/{d}/story*.jpg'))
th=[]
for f in fs:
    im=Image.open(f); h=540 if 'story' in f else 540; w=int(im.width*h/im.height); th.append(im.resize((w,h)))
W=sum(t.width for t in th)+10*(len(th)+1)
cols=5; rows=[th[i:i+cols] for i in range(0,len(th),cols)]
W=max(sum(t.width for t in r)+10*(len(r)+1) for r in rows)
c=Image.new('RGB',(W,len(rows)*550+10),'white');y=10
for r in rows:
    x=10
    for t in r: c.paste(t,(x,y)); x+=t.width+10
    y+=550
c.save(out,quality=85)
