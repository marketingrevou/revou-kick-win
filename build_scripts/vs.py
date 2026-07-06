from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cs_new as F   # reuse load_flag / trim_border / NO_TRIM / fill_tile

SCR  = F.SCR
PROJ = F.PROJ
W, H = 1344, 768
YELLOW=(255,222,61); NAVY=(18,26,64); NAVYO=(20,29,69); WHITE=(255,255,255)
RED=(232,60,60)

def font(sz):
    for n in ["arialbd.ttf","DejaVuSans-Bold.ttf"]:
        try: return ImageFont.truetype(n,sz)
        except: pass
    return ImageFont.load_default()

# ---- backdrop: dimmed stadium (matches country select) ----
bg = Image.open(SCR + "/stadium_empty.png").convert("RGBA").resize((W,H), Image.LANCZOS)
bg.alpha_composite(Image.new("RGBA",(W,H),(6,10,30,205)))
vig = Image.new("L",(W,H),0)
ImageDraw.Draw(vig).ellipse([-W*0.35,-H*0.35,W*1.35,H*1.35], fill=120)
vig = vig.filter(ImageFilter.GaussianBlur(120))
dk = Image.new("RGBA",(W,H),(0,0,6,255))
dk.putalpha(Image.eval(vig, lambda a: 150-a if 150-a>0 else 0))
bg.alpha_composite(dk)
d = ImageDraw.Draw(bg,"RGBA")

def otext(x,y,s,sz,fill=WHITE,oc=NAVYO,ow=5,anchor="mm",shadow=True):
    f=font(sz)
    if shadow: d.text((x+ow+2,y+ow+3),s,font=f,fill=(0,0,10,180),anchor=anchor)
    for dx in range(-ow,ow+1):
        for dy in range(-ow,ow+1):
            if dx*dx+dy*dy<=ow*ow: d.text((x+dx,y+dy),s,font=f,fill=oc,anchor=anchor)
    d.text((x,y),s,font=f,fill=fill,anchor=anchor)

# diagonal accent split behind the two sides
split = Image.new("RGBA",(W,H),(0,0,0,0))
sd = ImageDraw.Draw(split)
sd.polygon([(0,0),(W*0.52,0),(W*0.44,H),(0,H)], fill=(30,44,110,90))   # left tint
sd.polygon([(W*0.56,0),(W,0),(W,H),(W*0.48,H)], fill=(110,30,40,90))   # right tint
bg.alpha_composite(split)
d = ImageDraw.Draw(bg,"RGBA")

# ---- header ----
otext(W//2, int(H*0.11), "GET READY!", int(H*0.085), fill=YELLOW, ow=6)

# ---- flag card helper ----
def flag_card(cx, cy, w, name_txt, fn, label):
    fw = w; fh = int(w*2/3)
    fl = F.fill_tile(F.load_flag(fn), fw, fh, trim=(fn not in F.NO_TRIM))
    x0 = cx - fw//2; y0 = cy - fh//2
    # shadow
    sh = Image.new("RGBA",(fw+40,fh+40),(0,0,0,0))
    ImageDraw.Draw(sh).rectangle([20,24,20+fw,24+fh], fill=(0,0,8,160))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    bg.alpha_composite(sh,(x0-20,y0-16))
    bg.alpha_composite(fl,(x0,y0))
    d.rectangle([x0,y0,x0+fw-1,y0+fh-1], outline=YELLOW, width=5)
    # role label above, country below
    otext(cx, y0 - int(fh*0.16), label, int(fh*0.14), fill=WHITE, ow=4)
    otext(cx, y0 + fh + int(fh*0.17), name_txt, int(fh*0.19), fill=YELLOW, ow=5)

card_w = int(W*0.29)
cy = int(H*0.46)
flag_card(int(W*0.245), cy, card_w, "ARGENTINA", "argentina", "KAMU")

# ---- rival card: RevoU keeper. Show rival COUNTRY flag but note keeper is RevoU ----
flag_card(int(W*0.755), cy, card_w, "PORTUGAL", "portugal", "RIVAL KEEPER")

# ---- center VS badge ----
vcx, vcy = W//2, cy
R = int(H*0.11)
# glow
glow = Image.new("RGBA",(W,H),(0,0,0,0))
ImageDraw.Draw(glow).ellipse([vcx-R-40,vcy-R-40,vcx+R+40,vcy+R+40], fill=(255,222,61,80))
glow = glow.filter(ImageFilter.GaussianBlur(30))
bg.alpha_composite(glow)
d = ImageDraw.Draw(bg,"RGBA")
d.ellipse([vcx-R,vcy-R,vcx+R,vcy+R], fill=(14,20,52,255), outline=YELLOW, width=8)
otext(vcx, vcy, "VS", int(R*1.1), fill=YELLOW, ow=5)

# ---- game instruction (Bahasa Indonesia) ----
otext(W//2, int(H*0.83), "Cetak 3 gol untuk memenangkan hadiah terbaik!", int(H*0.036), fill=WHITE, ow=4)

# ---- continue prompt ----
otext(W//2, int(H*0.925), "TAP TO KICK OFF", int(H*0.05), fill=YELLOW, ow=5)

out = bg.convert("RGB")
out.save(SCR + "/vs_native.png")
out.resize((1024,int(1024*H/W)), Image.LANCZOS).save(SCR + "/vs_preview.png")
print("done")
