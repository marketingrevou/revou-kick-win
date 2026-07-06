from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

SCR  = os.path.dirname(os.path.abspath(__file__))   # script folder (outputs here)
PROJ = os.path.dirname(SCR)                          # project root (has scene_final.png)

YELLOW=(255,222,61); NAVY=(18,26,64); WHITE=(255,255,255)
GREEN=(70,220,100); RED=(232,60,60)

def font(sz):
    for n in ["arialbd.ttf","DejaVuSans-Bold.ttf"]:
        try: return ImageFont.truetype(n,sz)
        except: pass
    return ImageFont.load_default()

def render(kind):
    base = Image.open(PROJ + "/scene_final.png").convert("RGBA")
    W,H = base.size
    d = ImageDraw.Draw(base,"RGBA")

    def otext(x,y,s,sz,fill=WHITE,oc=NAVY,ow=8,anchor="mm",shadow=True):
        f=font(sz)
        if shadow: d.text((x+ow+4,y+ow+6),s,font=f,fill=(0,0,10,190),anchor=anchor)
        for dx in range(-ow,ow+1):
            for dy in range(-ow,ow+1):
                if dx*dx+dy*dy<=ow*ow: d.text((x+dx,y+dy),s,font=f,fill=oc,anchor=anchor)
        d.text((x,y),s,font=f,fill=fill,anchor=anchor)

    # colored flash tint over the whole scene
    tint = GREEN if kind=="goal" else RED
    base.alpha_composite(Image.new("RGBA",(W,H),(*tint,55)))
    # darken slightly for text contrast
    base.alpha_composite(Image.new("RGBA",(W,H),(0,0,10,60)))
    d = ImageDraw.Draw(base,"RGBA")

    # ball position (goal or saved)
    if kind == "goal":
        bx, by = int(W*0.70), int(H*0.52)   # ball tucked into top-right corner of net
    else:
        bx, by = int(W*0.50), int(H*0.63)   # ball at keeper's hands, center

    # impact burst behind ball
    burst = Image.new("RGBA",(W,H),(0,0,0,0))
    bd = ImageDraw.Draw(burst)
    for i in range(14):
        a = i*(math.pi*2/14)
        r1 = int(H*0.05); r2 = int(H*0.11)
        x1 = bx+int(math.cos(a)*r1); y1 = by+int(math.sin(a)*r1)
        x2 = bx+int(math.cos(a)*r2); y2 = by+int(math.sin(a)*r2)
        bd.line([x1,y1,x2,y2], fill=(*YELLOW,235), width=10)
    burst = burst.filter(ImageFilter.GaussianBlur(2))
    base.alpha_composite(burst)
    d = ImageDraw.Draw(base,"RGBA")

    # ball
    br = int(H*0.032)
    d.ellipse([bx-br,by-br,bx+br,by+br], fill=WHITE, outline=NAVY, width=6)
    d.ellipse([bx-br*0.34,by-br*0.34,bx+br*0.34,by+br*0.34], fill=(40,44,60))

    # motion/trail lines toward the ball
    for k in range(3):
        oy = (k-1)*int(H*0.03)
        d.line([int(W*0.50), by+oy, bx-br, by+oy*0.3], fill=(*WHITE,120), width=6)

    # big headline text
    if kind == "goal":
        otext(W//2, int(H*0.30), "GOOOAL!", int(H*0.19), fill=YELLOW, ow=10)
        otext(W//2, int(H*0.46), "+1", int(H*0.09), fill=GREEN, ow=7)
    else:
        otext(W//2, int(H*0.30), "SAVED!", int(H*0.19), fill=WHITE, ow=10)
        otext(W//2, int(H*0.46), "COBA LAGI", int(H*0.055), fill=RED, ow=6)

    out = base.convert("RGB")
    out.save(SCR + f"/fb_{kind}_native.png")
    out.resize((1100,int(1100*H/W)), Image.LANCZOS).save(SCR + f"/fb_{kind}_preview.png")

render("goal")
render("save")
print("done")
