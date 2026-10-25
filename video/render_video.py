"""Deterministic 1080p motion edit, using actual app capture and labeled workflow animation."""
import argparse, bisect, functools, json, math, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
W,H,FPS=1920,1080,30
SCENES=json.loads((ROOT/'storyboard.json').read_text())
STARTS=[s['start'] for s in SCENES]
INK='#091222'; PANEL='#121f32'; LINE='#2b3c50'; WHITE='#f4f7fc'; MUTED='#9bacbf'; MINT='#55e2c4'; CORAL='#ffadba'; VIOLET='#b8a2fc'
FONT='/System/Library/Fonts/Avenir Next.ttc'
FONT_B='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
@functools.lru_cache(maxsize=100)
def font(size,bold=False): return ImageFont.truetype(FONT_B if bold else FONT,int(size))
def ease(x):
    x=max(0,min(1,x)); return x*x*(3-2*x)
def lerp(a,b,p): return a+(b-a)*p
def rect(d,box,fill=PANEL,r=24,outline=None,width=1):
    d.rounded_rectangle(tuple(int(x) for x in box),radius=r,fill=fill,outline=outline,width=width)
def txt(d,xy,s,size=34,fill=WHITE,bold=False,anchor=None):
    d.text(tuple(int(v) for v in xy),s,font=font(size,bold),fill=fill,anchor=anchor,spacing=12)
def lines(d,xy,text,size=66,fill=WHITE,bold=True,gap=1.12):
    for n,line in enumerate(text.split('\n')): txt(d,(xy[0],xy[1]+n*size*gap),line,size,fill,bold)
def pill(d,xy,label,color=MINT,bg='#173d3c',size=22):
    width=d.textlength(label,font=font(size,True))+36
    rect(d,(xy[0],xy[1],xy[0]+width,xy[1]+43),bg,21)
    txt(d,(xy[0]+18,xy[1]+6),label,size,color,True)
    return width
def check(d,x,y,s=22,color=MINT): d.line([(x-s*.7,y),(x-s*.15,y+s*.55),(x+s*.85,y-s*.7)],fill=color,width=max(3,int(s*.16)),joint='curve')
def arrow(d,x1,y1,x2,y2,color=MINT,width=4):
    d.line((x1,y1,x2,y2),fill=color,width=width)
    a=math.atan2(y2-y1,x2-x1)
    d.polygon([(x2,y2),(x2-16*math.cos(a-.45),y2-16*math.sin(a-.45)),(x2-16*math.cos(a+.45),y2-16*math.sin(a+.45))],fill=color)
def lock(d,x,y,scale=1,color=MINT):
    d.arc((x-30*scale,y-62*scale,x+30*scale,y+8*scale),180,360,fill=color,width=int(7*scale))
    rect(d,(x-46*scale,y-15*scale,x+46*scale,y+60*scale),color,int(12*scale))
    d.ellipse((x-6*scale,y+10*scale,x+6*scale,y+22*scale),fill=INK)
    d.line((x,y+21*scale,x,y+39*scale),fill=INK,width=int(5*scale))
def cursor(d,x,y,t,click=False):
    if click:
        r=20+22*((t%1.2)/1.2)
        d.ellipse((x-r,y-r,x+r,y+r),outline=MINT,width=2)
    pts=[(x,y),(x+4,y+36),(x+13,y+26),(x+23,y+43),(x+31,y+38),(x+21,y+23),(x+36,y+21)]
    d.polygon(pts,fill=WHITE,outline=INK)
def node(d,box,title,subtitle='',accent=MINT):
    rect(d,box,PANEL,25,LINE,2)
    txt(d,(box[0]+26,box[1]+24),title,31,accent,True)
    if subtitle: txt(d,(box[0]+26,box[1]+76),subtitle,23,MUTED)

yy,xx=np.mgrid[0:H,0:W]
glow=np.exp(-((xx-1500)**2/(900**2)+(yy-150)**2/(680**2)))
glow2=np.exp(-((xx-100)**2/(650**2)+(yy-940)**2/(450**2)))
base=np.zeros((H,W,3),dtype=np.float32)+np.array([8,15,28])
base+=glow[:,:,None]*np.array([5,23,23])+glow2[:,:,None]*np.array([14,8,26])
BG=Image.fromarray(np.uint8(np.clip(base,0,255)),'RGB')
del xx,yy,glow,glow2,base
ASSETS=ROOT.parent/'web/public/landing'
PORTRAIT=Image.open(ASSETS/'portrait-cyan.png').convert('RGB')
DASH=Image.open(ROOT/'assets/dashboard.png').convert('RGB')
def cropfill(im,size,box=None):
    im=im.crop(box) if box else im
    factor=max(size[0]/im.width,size[1]/im.height)
    im=im.resize((round(im.width*factor),round(im.height*factor)),Image.Resampling.LANCZOS)
    l=(im.width-size[0])//2; t=(im.height-size[1])//2
    return im.crop((l,t,l+size[0],t+size[1]))
@functools.lru_cache(maxsize=20)
def photo(w,h): return cropfill(PORTRAIT,(w,h))
def paste_round(im,asset,box,r=28):
    x,y,x2,y2=map(int,box);w=x2-x;h=y2-y
    if w<=0 or h<=0:return
    if asset.size!=(w,h):asset=asset.resize((w,h),Image.Resampling.BICUBIC)
    mask=Image.new('L',(w,h)); ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),radius=r,fill=255)
    im.paste(asset,(x,y),mask)
def photo_card(im,x,y,w,h,label=None):
    paste_round(im,photo(w,h),(x,y,x+w,y+h),28)
    d=ImageDraw.Draw(im)
    if label:
        rect(d,(x+14,y+h-60,x+w-14,y+h-14),INK,15)
        txt(d,(x+30,y+h-53),label,22,WHITE,True)

def head(im,s,i,t):
    d=ImageDraw.Draw(im)
    d.ellipse((88,50,128,90),fill=MINT)
    d.arc((96,56,120,79),0,180,fill=INK,width=3)
    txt(d,(145,48),'facetime',34,WHITE,True)
    txt(d,(1810,57),f'{i+1:02} / {len(SCENES):02}',22,MUTED,anchor='ra')
    d.line((90,112,1830,112),fill=LINE,width=1)
    evidence=''
    if s['id'] in ['identity','protect']:evidence='ONBOARDING · ANIMATED RECONSTRUCTION'
    elif s['id'] in ['dashboard','terms']:evidence='ACTUAL APP CAPTURE · LOCAL FORK'
    elif s['id'] in ['request','approve','escrow','render','revoke']:evidence='ILLUSTRATED WORKFLOW'
    elif s['id']=='architecture':evidence='SYSTEM OVERVIEW'
    if evidence:txt(d,(1810,137),evidence,18,MUTED,anchor='ra')
    return d

def render_scene(s,t,i):
    im=BG.copy();d=head(im,s,i,t); kind=s['id'];e=ease(t/.75)
    if kind=='hook':
        lines(d,(118,270+30*(1-e)),'Your face.\nSomeone else’s ad.',83)
        pill(d,(120,555),'WHO GETS TO SAY YES?',MINT)
        txt(d,(122,644),'A new image. A missing agreement.',30,MUTED)
        x=1210+90*(1-e);photo_card(im,int(x),205,480,590,'ILLUSTRATIVE PORTRAIT')
        d=ImageDraw.Draw(im)
        if t>3:
            p=ease((t-3)/.7);rect(d,(1090,680+65*(1-p),1730,805+65*(1-p)),'#3c2330',22,CORAL)
            txt(d,(1120,704+65*(1-p)),'Permission?',34,CORAL,True)
            txt(d,(1120,750+65*(1-p)),'Nobody asked.',26,WHITE)
    elif kind=='question':
        lines(d,(118,240),'Where was\nyour permission?',88)
        txt(d,(120,495),'The person should get a say.',34,MUTED)
        for k,(x,y) in enumerate([(1130,245),(1350,355),(1120,485)]):
            p=ease((t-k*.75)/.7);photo_card(im,int(x+100*(1-p)),int(y),300,330,['SOCIAL AD','CAMPAIGN','NEW VARIATION'][k])
        d=ImageDraw.Draw(im);pill(d,(120,670),'CONSENT SHOULD COME FIRST')
    elif kind=='problem':
        lines(d,(120,190),'Three missing pieces.',75)
        for k,(title,body,color) in enumerate([('Permission','Who agreed to this?',MINT),('Payment','Who gets the value?',VIOLET),('Proof','Can anyone verify it?',CORAL)]):
            p=ease((t-.6-k*3)/.75);x=120+k*575;y=350+70*(1-p)
            if p<=0:continue
            rect(d,(x,y,x+535,y+380),PANEL,30,LINE,2)
            txt(d,(x+35,y+32),f'0{k+1}',31,color,True)
            txt(d,(x+35,y+130),title,49,WHITE,True)
            txt(d,(x+35,y+218),body,29,MUTED)
            d.line((x+35,y+300,x+35+420*p,y+300),fill=color,width=4)
        if t>11:txt(d,(120,798),'One agreement should connect all three.',33,MINT)
    elif kind=='promise':
        txt(d,(960,235),'Facetime.',140,WHITE,True,anchor='ma')
        txt(d,(960,420),'Your face. Your terms.',51,MINT,True,anchor='ma')
        names=['Verify','License','Earn','Revoke']
        for k,n in enumerate(names):
            p=ease((t-2-k*2)/.7)
            if p>0:
                x=190+k*420;y=595+40*(1-p)
                rect(d,(x,y,x+345,y+114),PANEL,24,LINE,2);txt(d,(x+172,y+29),n,37,WHITE,True,anchor='ma')
                if k and p>.6:arrow(d,x-55,y+58,x-16,y+58)
        txt(d,(960,807),'Consent that software can check.',30,MUTED,anchor='ma')
    elif kind=='identity':
        lines(d,(120,220),'First,\na real person.',79)
        txt(d,(120,450),'An identity check. A live selfie.',32,MUTED)
        txt(d,(120,503),'A match to the person registering.',32,MUTED)
        rect(d,(1195,190,1650,840),PANEL,44,LINE,2)
        photo_card(im,1240,250,365,410)
        d=ImageDraw.Draw(im);scan=275+(t%3)/3*340
        d.line((1258,scan,1587,scan),fill=MINT,width=4)
        if t>2:pill(d,(1250,690),'LIVENESS CHECKED')
        if t>4:pill(d,(1250,747),'ADULT · 18+')
    elif kind=='protect':
        lines(d,(120,180),'Photos, protected.',77)
        for k in range(3):
            p=ease(max(0,t-2.3)/1.1);x=lerp(200+k*540,745+k*40,p);y=lerp(350,340,p)
            photo_card(im,int(x),int(y),330,350)
        if t>2.3:
            p=ease((t-2.3)/.65)
            overlay=Image.new('RGBA',(W,H),(0,0,0,0));od=ImageDraw.Draw(overlay)
            rect(od,(720,310,1200,740),(18,31,50,int(255*p)),30)
            im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB');d=ImageDraw.Draw(im)
            lock(d,960,475,1.4)
            txt(d,(960,590),'Encrypted in your browser',29,WHITE,True,anchor='ma')
            txt(d,(960,640),'Protected by your passkey',25,MINT,anchor='ma')
        txt(d,(960,805),'Matched photos → encrypted reference set',31,MUTED,anchor='ma')
    elif kind=='dashboard':
        lines(d,(120,175),'Now, my actual account.',67)
        rect(d,(115,283,1805,871),'#25354a',30)
        # Zoom to the registered creator summary; all pixels are from the captured local app.
        p=ease((t-5)/2);box=(lerp(735,1170,p),lerp(65,120,p),lerp(2690,2690,p),lerp(945,880,p))
        shot=cropfill(DASH,(1660,550),box)
        paste_round(im,shot,(130,300,1790,850),20);d=ImageDraw.Draw(im)
        pill(d,(140,248),'localhost:3000/dashboard',MUTED,'#1b293c',20)
        if t>5:
            cursor(d,lerp(880,1555,ease((t-5)/.75)),lerp(770,403,ease((t-5)/.75)),t,True)
    elif kind=='terms':
        lines(d,(120,230),'I set\nthe terms.',83)
        for k,(label,val) in enumerate([('USE','Advertising + Social'),('PRICE','2 USDC per render'),('LIMIT','100 renders / 30 days'),('APPROVAL','Ask me each time')]):
            p=ease((t-k*2)/.7)
            if p>0:
                y=470+k*83+20*(1-p);txt(d,(125,y),label,18,MINT,True);txt(d,(320,y-6),val,28,WHITE)
        shot=cropfill(DASH,(820,650),(2010,970,2680,1460))
        rect(d,(942,211,1798,897),'#25354a',30)
        paste_round(im,shot,(960,229,1780,879),21)
        d=ImageDraw.Draw(im);cursor(d,1530,lerp(482,678,ease((t-6)/.75)),t,t>6)
    elif kind=='request':
        lines(d,(120,175),'A request, not a blank cheque.',63)
        node(d,(120,310,655,780),'Coffee campaign','Example brand · five images')
        txt(d,(155,465),'SOCIAL',28,MINT,True);txt(d,(155,520),'5 renders',43,WHITE,True);txt(d,(155,600),'30 days · Worldwide',27,MUTED)
        arrow(d,690,550,790,550)
        rect(d,(830,310,1800,800),PANEL,30,LINE,2)
        txt(d,(880,344),'Request a licence',39,WHITE,True)
        labels=[('Use','Social'),('Campaign','Morning coffee'),('Renders','5'),('Price per render','2.00 USDC')]
        for k,(label,value) in enumerate(labels):
            p=ease((t-1-k*1.4)/.7);y=432+k*58
            txt(d,(880,y),label,25,MUTED)
            if p>0:txt(d,(1310,y),value,27,WHITE,True)
        rect(d,(880,707,1740,769),MINT,18);txt(d,(1310,720),'Send to creator for approval',28,INK,True,anchor='ma')
        if t>9:cursor(d,lerp(1660,1460,ease((t-9)/.7)),lerp(650,740,ease((t-9)/.7)),t,True)
    elif kind=='approve':
        lines(d,(120,175),'Permission is specific.',70)
        stages=[('Creator approval','Sign this agreement'),('Licence issued','Scope + price + expiry'),('Photo release','For this licence only')]
        for k,(title,sub) in enumerate(stages):
            p=ease((t-k*3.8)/.75);x=120+k*580;y=365+50*(1-p)
            if p<=0:continue
            node(d,(x,y,x+520,y+330),title,sub)
            d.ellipse((x+220,y+170,x+300,y+250),fill='#173d3c');check(d,x+260,y+207,25)
            if k and p>.5:arrow(d,x-45,y+160,x-10,y+160)
        txt(d,(960,800),'An account is not permission to use a face.',33,MUTED,anchor='ma')
    elif kind=='escrow':
        lines(d,(120,175),'Pay for each use.',76)
        rect(d,(120,330,650,800),PANEL,30,LINE,2)
        txt(d,(160,370),'LICENCE ESCROW',23,MUTED,True)
        amount=10 if t<5 else lerp(10,8,ease((t-5)/1))
        txt(d,(160,450),f'{amount:.2f}',100,WHITE,True)
        txt(d,(160,580),'USDC remaining',28,MUTED)
        pill(d,(160,705),'5 RENDERS × 2 USDC',MINT)
        arrow(d,700,565,855,565)
        node(d,(915,330,1780,545),'Creator','1.80 USDC per render',MINT)
        node(d,(915,590,1780,805),'Platform','0.20 USDC per render',VIOLET)
        if t>5:
            for k in range(7):
                p=((t-5)*.35+k*.12)%1;x=lerp(710,920,p);y=565+(-110 if k%2==0 else 100)*p
                d.ellipse((x-7,y-7,x+7,y+7),fill=MINT if k%2==0 else VIOLET)
    elif kind=='render':
        lines(d,(120,175),'Check before creating.',72)
        labels=['Licence active','Within render limits','Escrow available','Prompt checked']
        for k,label in enumerate(labels):
            y=350+k*108;rect(d,(120,y,820,y+82),PANEL,20,LINE)
            txt(d,(155,y+20),label,31,WHITE,True)
            if t>k*1.3:check(d,765,y+40,19)
        rect(d,(960,320,1790,820),PANEL,30,LINE,2)
        lock(d,1375,440,1.05,VIOLET)
        txt(d,(1375,550),'TEST RENDERER',45,CORAL,True,anchor='ma')
        txt(d,(1375,627),'Consent + payment pipeline',29,WHITE,anchor='ma')
        txt(d,(1375,676),'Image model not configured locally',25,MUTED,anchor='ma')
        pill(d,(1115,744),'NO GENERATED OUTPUT CLAIMED',CORAL,'#3c2330',19)
    elif kind=='revoke':
        lines(d,(120,175),'Proof. And a way to stop.',68)
        rect(d,(120,330,860,825),PANEL,30,LINE,2)
        txt(d,(165,375),'File provenance',38,WHITE,True)
        for k,label in enumerate(['Licence and creator','Paid render receipt','Content credential']):
            txt(d,(205,470+k*75),label,28,MUTED);check(d,165,489+k*75,14)
        revoked=t>7.5
        rect(d,(1020,330,1790,825),PANEL,30,CORAL if revoked else LINE,2)
        txt(d,(1060,375),'Creator control',37,WHITE,True)
        rect(d,(1070,480,1735,560),'#3c2330' if revoked else MINT,20)
        txt(d,(1400,499),'Licence revoked' if revoked else 'Revoke licence',32,CORAL if revoked else INK,True,anchor='ma')
        if t>5:cursor(d,1600,520,t,not revoked)
        txt(d,(1070,620),'Future renders refused' if revoked else 'Consent can be withdrawn',29,WHITE,True)
        if revoked:
            txt(d,(1070,687),'Earlier files: licensed when made,',26,MUTED)
            txt(d,(1070,729),'since revoked.',26,CORAL)
    elif kind=='architecture':
        lines(d,(120,175),'One connected flow.',72)
        node(d,(120,350,570,710),'Browser','Wallet + encrypted photos')
        node(d,(735,350,1185,710),'Render service','Checks + authorized render')
        node(d,(1350,350,1800,710),'Contracts','Licences + escrow + receipts')
        for x in [570,1185]:arrow(d,x+25,530,x+135,530)
        for k,(x,l1,l2) in enumerate([(155,'React / Next.js','Dynamic · Didit · Mera'),(770,'Gemini integration','C2PA file credential'),(1385,'Monad','Local fork for this demo')]):
            p=ease((t-k*4)/.75)
            if p>0:txt(d,(x,525),l1,29,WHITE,True);txt(d,(x,588),l2,23,MUTED)
        for x1,x2 in [(595,710),(1210,1325)]:
            p=(t*.36)%1;x=lerp(x1,x2,p);d.ellipse((x-8,522,x+8,538),fill=MINT)
        txt(d,(960,810),'Encrypted at rest · decrypted in memory for authorized rendering',29,MUTED,anchor='ma')
    elif kind=='scope':
        lines(d,(120,180),'Built to be inspected.',74)
        for k,(a,b) in enumerate([('RUNNING LOCALLY','Registered creator + configurable terms'),('DEMO ENVIRONMENT','Monad fork + test signing credentials'),('NEXT MILESTONE','Production services + independent contract review')]):
            y=340+k*165;p=ease((t-k*2)/.7)
            if p>0:
                rect(d,(120,y,1800,y+125),PANEL,22,LINE)
                txt(d,(150,y+24),a,21,MINT,True);txt(d,(670,y+36),b,31,WHITE)
    elif kind=='close':
        lines(d,(120,225),'Your face.\nYour terms.',111)
        txt(d,(123,535),'A say in what happens next.',40,MINT)
        txt(d,(123,645),'Facetime',57,WHITE,True)
        txt(d,(125,730),'Consent that software can check.',30,MUTED)
        # The final shape returns to the face motif in the opening.
        cx,cy=1450,515;r=225+8*math.sin(t*.65)
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=MINT)
        d.ellipse((cx-78,cy-55,cx-53,cy-25),fill=INK);d.ellipse((cx+53,cy-55,cx+78,cy-25),fill=INK)
        d.arc((cx-100,cy-10,cx+100,cy+105),0,180,fill=INK,width=11)
        if t>8:pill(d,(125,820),'EXPLORE THE DEMO',MINT)
    return im

WORDS=json.loads((ROOT/'words.json').read_text()) if (ROOT/'words.json').exists() else []
GROUPS=[]
for s in SCENES:
    ws=[w for w in WORDS if w['scene']==s['id']]
    for k in range(0,len(ws),6):GROUPS.append(ws[k:k+6])
GSTART=[g[0]['start'] for g in GROUPS]
def captions(im,t):
    if not GROUPS:return
    gi=bisect.bisect_right(GSTART,t)-1
    if gi<0:return
    g=GROUPS[gi]
    if t>g[-1]['end']+.18:return
    d=ImageDraw.Draw(im);size=37
    widths=[d.textlength(w['text'],font=font(size,True)) for w in g]
    total=sum(widths)+20*(len(g)-1)
    if total>1640:
        size=31;widths=[d.textlength(w['text'],font=font(size,True)) for w in g];total=sum(widths)+20*(len(g)-1)
    x=(W-total)/2;y=957
    rect(d,(x-28,y-13,x+total+28,y+61),'#070e19',20)
    for w,width in zip(g,widths):
        active=w['start']<=t<=w['end']+.04
        lift=3*math.sin(min(1,max(0,(t-w['start'])/.15))*math.pi) if active else 0
        if active:rect(d,(x-8,y-5-lift,x+width+8,y+50-lift),MINT,9)
        txt(d,(x,y-lift),w['text'],size,INK if active else WHITE,True)
        x+=width+20

def frame(t):
    i=min(len(SCENES)-1,bisect.bisect_right(STARTS,t)-1);s=SCENES[i];local=t-s['start']
    im=render_scene(s,local,i)
    if i and local<.65:
        prev=render_scene(SCENES[i-1],SCENES[i-1]['duration']-.02,i-1)
        im=Image.blend(prev,im,ease(local/.65))
    captions(im,t)
    d=ImageDraw.Draw(im);d.line((90,1045,1830,1045),fill=LINE,width=2)
    d.line((90,1045,90+1740*t/210,1045),fill=MINT,width=3)
    return im

def main():
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');p.add_argument('--start',type=float,default=0);p.add_argument('--duration',type=float,default=210);p.add_argument('--output',default='visuals.mp4');args=p.parse_args()
    if args.preview:
        times=[3,11,24,40,49,57,65,82,99,113,128,143,160,176,190,204]
        contact=Image.new('RGB',(1280,720*4),'#080f1c')
        for i,t in enumerate(times):
            img=frame(t); img.save(OUT/f'frame-{t:03}.jpg',quality=92)
            contact.paste(img.resize((640,360)),((i%2)*640,(i//2)*360))
        contact.save(OUT/'contact-sheet.jpg',quality=92)
        frame(202).save(OUT/'Facetime-thumbnail.png')
        print('Preview frames rendered.');return
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/args.output)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    total=round(args.duration*FPS)
    try:
        for f in range(total):
            proc.stdin.write(frame(args.start+f/FPS).tobytes())
            if f%(FPS*10)==0:print(f'Rendered {f/FPS:.0f}/{args.duration:.0f} seconds',flush=True)
    finally:
        proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError('Video encoding failed')
    print('Video render complete:',OUT/args.output,flush=True)

if __name__=='__main__':main()
