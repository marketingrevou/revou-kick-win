from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

SCR  = os.path.dirname(os.path.abspath(__file__))   # script folder (outputs here)
PROJ = os.path.dirname(SCR)                          # project root (has title_background.png)

SCALE = 2
YELLOW = (255, 222, 61)
NAVY   = (18, 26, 64)
WHITE  = (255, 255, 255)
GREEN  = (70, 210, 100)
RED    = (232, 60, 60)

def font(sz):
    for n in ["arialbd.ttf", "DejaVuSans-Bold.ttf"]:
        try: return ImageFont.truetype(n, sz)
        except: pass
    return ImageFont.load_default()

# state config: (headline, dots, prize list)
STATES = {
    "1of3": ("GOAL!",    ["goal","save","save"],
             [("AI FREE LEARNING", "ai"), ("REVOU STARTER KIT", "box")]),
    "2of3": ("GOOOAL!",  ["goal","goal","save"],
             [("BNSP CERTIFICATION", "cert"), ("REVOU STARTER KIT", "box")]),
    "3of3": ("PERFECT!", ["goal","goal","goal"],
             [("BNSP CERTIFICATION", "cert"), ("AI FREE LEARNING", "ai"), ("REVOU STARTER KIT", "box")]),
}

def render(key):
    headline, dots, prizes = STATES[key]
    n_goals = sum(1 for s in dots if s == "goal")

    src = Image.open(PROJ + "/title_background.png").convert("RGBA")
    W, H = src.width*SCALE, src.height*SCALE
    bg = src.resize((W, H), Image.NEAREST)
    d = ImageDraw.Draw(bg, "RGBA")

    def otext(x, y, s, sz, fill=WHITE, oc=NAVY, ow=5, anchor="mm", shadow=True):
        f = font(sz)
        if shadow:
            d.text((x+ow+3, y+ow+4), s, font=f, fill=(0,0,10,180), anchor=anchor)
        for dx in range(-ow, ow+1):
            for dy in range(-ow, ow+1):
                if dx*dx+dy*dy <= ow*ow:
                    d.text((x+dx, y+dy), s, font=f, fill=oc, anchor=anchor)
        d.text((x, y), s, font=f, fill=fill, anchor=anchor)

    bg.alpha_composite(Image.new("RGBA", (W, H), (6, 10, 30, 90)))

    # ---- headline + score ----
    otext(W//2, int(H*0.095), headline, int(H*0.11), fill=YELLOW, ow=7)
    otext(W//2, int(H*0.205), f"SKOR KAMU:  {n_goals} / 3", int(H*0.05), fill=WHITE, ow=5)

    # 3 ball dots
    r = int(H*0.022); gap = int(r*3.4); cy = int(H*0.265); cx0 = W//2 - gap
    def ball_dot(cx, cy, r, state):
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(245,245,248), outline=NAVY, width=6)
        d.ellipse([cx-r*0.34, cy-r*0.34, cx+r*0.34, cy+r*0.34], fill=(40,44,60))
        if state == "goal":
            d.ellipse([cx-r-4, cy-r-4, cx+r+4, cy+r+4], outline=GREEN, width=8)
            d.line([cx-r*0.45, cy+2, cx-r*0.08, cy+r*0.42], fill=GREEN, width=9)
            d.line([cx-r*0.08, cy+r*0.42, cx+r*0.5, cy-r*0.42], fill=GREEN, width=9)
        else:
            d.ellipse([cx-r-4, cy-r-4, cx+r+4, cy+r+4], outline=RED, width=8)
            o=r*0.4
            d.line([cx-o,cy-o,cx+o,cy+o], fill=RED, width=9)
            d.line([cx-o,cy+o,cx+o,cy-o], fill=RED, width=9)
    for i, st in enumerate(dots):
        ball_dot(cx0 + i*gap, cy, r, st)

    # ---- prize panel (height scales with prize count) ----
    pw = int(W*0.70)
    ph = int(H*(0.22 + 0.135*len(prizes)))
    px = (W-pw)//2
    py = int(H*0.30) if len(prizes) < 3 else int(H*0.285)
    sh = Image.new("RGBA",(pw+60,ph+60),(0,0,0,0))
    ImageDraw.Draw(sh).rounded_rectangle([30,34,30+pw,34+ph], radius=40, fill=(0,0,10,150))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    bg.alpha_composite(sh,(px-30,py-30))
    d.rounded_rectangle([px,py,px+pw,py+ph], radius=40, fill=(14,20,52,238), outline=YELLOW, width=8)
    rh = int(ph*0.15)
    d.rounded_rectangle([px,py,px+pw,py+rh], radius=40, fill=YELLOW)
    d.rectangle([px,py+rh-40,px+pw,py+rh], fill=YELLOW)
    otext(px+pw//2, py+rh//2, "KAMU MENANG!", int(rh*0.55), fill=NAVY, oc=NAVY, ow=0, shadow=False)

    body_top = py + rh
    body_h = ph - rh
    row_h = int(body_h/len(prizes))
    icon_r = int(row_h*0.30)
    lx = px + int(pw*0.11)

    def draw_icon(cx, cy, kind):
        s = icon_r * 1.4
        if kind == "cert":
            w=s*0.92; h=s*1.05
            d.rounded_rectangle([cx-w, cy-h, cx+w, cy+h], radius=10, fill=WHITE, outline=NAVY, width=5)
            for k in range(3):
                yy=cy-h*0.5+k*h*0.34
                d.line([cx-w*0.6, yy, cx+w*0.6, yy], fill=(120,130,150), width=5)
            sr=s*0.34; scx,scy=cx-w*0.30, cy+h*0.42
            d.ellipse([scx-sr, scy-sr, scx+sr, scy+sr], fill=YELLOW, outline=NAVY, width=4)
            d.polygon([(scx-sr*0.4,scy+sr),(scx-sr*0.9,scy+sr*2.0),(scx-sr*0.05,scy+sr*1.4)], fill=RED, outline=NAVY)
            d.polygon([(scx+sr*0.4,scy+sr),(scx+sr*0.9,scy+sr*2.0),(scx+sr*0.05,scy+sr*1.4)], fill=RED, outline=NAVY)
        elif kind == "box":
            w=s*0.95; h=s*0.85; top=cy-h*0.35
            d.rectangle([cx-w, top, cx+w, cy+h], fill=(232,60,80), outline=NAVY, width=5)
            d.rectangle([cx-w*1.08, top-h*0.28, cx+w*1.08, top], fill=(255,120,140), outline=NAVY, width=5)
            d.rectangle([cx-w*0.15, top-h*0.28, cx+w*0.15, cy+h], fill=YELLOW, outline=NAVY, width=4)
            br=s*0.30
            d.ellipse([cx-w*0.15-br*1.6, top-h*0.28-br*1.4, cx-w*0.15, top-h*0.28+br*0.2], fill=YELLOW, outline=NAVY, width=4)
            d.ellipse([cx+w*0.15, top-h*0.28-br*1.4, cx+w*0.15+br*1.6, top-h*0.28+br*0.2], fill=YELLOW, outline=NAVY, width=4)
            d.ellipse([cx-br*0.5, top-h*0.28-br*0.5, cx+br*0.5, top-h*0.28+br*0.5], fill=YELLOW, outline=NAVY, width=4)
        else:  # ai  -> lightbulb + sparkle (sparkles kept on the LEFT so they don't hit the text)
            r2=s*0.82
            d.ellipse([cx-r2*0.75, cy-r2, cx+r2*0.75, cy+r2*0.5], fill=(120,200,255), outline=NAVY, width=5)
            d.rectangle([cx-r2*0.32, cy+r2*0.2, cx+r2*0.32, cy+r2*0.72], fill=(180,180,190), outline=NAVY, width=5)
            d.rectangle([cx-r2*0.32, cy+r2*0.72, cx+r2*0.32, cy+r2*0.95], fill=(120,130,150), outline=NAVY, width=4)
            d.line([cx, cy-r2*0.5, cx, cy+r2*0.15], fill=YELLOW, width=6)
            for (sx,sy,ss) in [(cx-r2*1.15, cy-r2*0.6, r2*0.26),(cx-r2*0.9, cy+r2*0.55, r2*0.18)]:
                d.line([sx-ss,sy,sx+ss,sy], fill=YELLOW, width=5)
                d.line([sx,sy-ss,sx,sy+ss], fill=YELLOW, width=5)

    for i,(name,kind) in enumerate(prizes):
        ry = body_top + i*row_h + row_h//2
        cr = icon_r*0.7
        d.ellipse([lx-cr, ry-cr, lx+cr, ry+cr], fill=GREEN, outline=WHITE, width=5)
        d.line([lx-cr*0.42, ry+cr*0.05, lx-cr*0.05, ry+cr*0.42], fill=WHITE, width=8)
        d.line([lx-cr*0.05, ry+cr*0.42, lx+cr*0.5, ry-cr*0.4], fill=WHITE, width=8)
        icx = lx + int(pw*0.11)
        draw_icon(icx, ry, kind)
        text_x = icx + int(pw*0.09)
        max_w = (px + pw - 40) - text_x
        fsz = int(row_h*0.26); f = font(fsz)
        while d.textlength(name, font=f) > max_w and fsz > 12:
            fsz -= 2; f = font(fsz)
        d.text((text_x, ry), name, font=f, fill=WHITE, anchor="lm")

    # ---- Play Again button ----
    bw, bh = int(W*0.28), int(H*0.08)
    bx = (W-bw)//2; by = py + ph + int(H*0.03)
    sh2 = Image.new("RGBA",(bw+40,bh+40),(0,0,0,0))
    ImageDraw.Draw(sh2).rounded_rectangle([20,24,20+bw,24+bh], radius=bh//2, fill=(0,0,10,150))
    sh2=sh2.filter(ImageFilter.GaussianBlur(12))
    bg.alpha_composite(sh2,(bx-20,by-20))
    d.rounded_rectangle([bx,by,bx+bw,by+bh], radius=bh//2, fill=YELLOW, outline=NAVY, width=7)
    otext(W//2, by+bh//2, "MAIN LAGI", int(bh*0.44), fill=NAVY, oc=NAVY, ow=0, shadow=False)

    out = bg.convert("RGB")
    out.save(SCR + f"/result_{key}_native.png")
    out.resize((1000, int(1000*H/W)), Image.LANCZOS).save(SCR + f"/result_{key}_preview.png")
    return W, H

for k in ["1of3","2of3","3of3"]:
    render(k)
print("done all")
