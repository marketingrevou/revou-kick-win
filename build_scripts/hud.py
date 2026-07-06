from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

SCR  = os.path.dirname(os.path.abspath(__file__))   # script folder (outputs here)
PROJ = os.path.dirname(SCR)                          # project root (has scene_final.png)

# work on the locked penalty scene
base = Image.open(PROJ + "/scene_final.png").convert("RGBA")
W, H = base.size          # 2148 x 1198
d = ImageDraw.Draw(base, "RGBA")

YELLOW = (255, 222, 61)
NAVY   = (18, 26, 64)
WHITE  = (255, 255, 255)
GREEN  = (60, 210, 90)
RED    = (232, 60, 60)

def font(sz):
    for n in ["arialbd.ttf", "DejaVuSans-Bold.ttf"]:
        try: return ImageFont.truetype(n, sz)
        except: pass
    return ImageFont.load_default()

def otext(x, y, s, sz, fill=WHITE, oc=NAVY, ow=4, anchor="la"):
    f = font(sz)
    for dx in range(-ow, ow+1):
        for dy in range(-ow, ow+1):
            if dx*dx+dy*dy <= ow*ow:
                d.text((x+dx, y+dy), s, font=f, fill=oc, anchor=anchor)
    d.text((x, y), s, font=f, fill=fill, anchor=anchor)

# ---------- top scoreboard: 3 ball dots, center ----------
def ball_dot(cx, cy, r, state):
    # state: 'goal','save','pending'
    # backing chip
    d.ellipse([cx-r-8, cy-r-8, cx+r+8, cy+r+8], fill=(10,16,40,180))
    if state == "pending":
        # empty ball outline
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(230,230,235,255), outline=NAVY, width=6)
        # pentagon hint
        d.ellipse([cx-r*0.32, cy-r*0.32, cx+r*0.32, cy+r*0.32], fill=(40,44,60))
        ring = None
    else:
        col = GREEN if state=="goal" else RED
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(245,245,248,255), outline=NAVY, width=6)
        d.ellipse([cx-r*0.34, cy-r*0.34, cx+r*0.34, cy+r*0.34], fill=(40,44,60))
        # status ring
        d.ellipse([cx-r-3, cy-r-3, cx+r+3, cy+r+3], outline=col, width=9)
    # icon overlay
    if state == "goal":
        d.line([cx-r*0.45, cy+2, cx-r*0.08, cy+r*0.42], fill=GREEN, width=11)
        d.line([cx-r*0.08, cy+r*0.42, cx+r*0.5, cy-r*0.42], fill=GREEN, width=11)
    elif state == "save":
        o=r*0.42
        d.line([cx-o, cy-o, cx+o, cy+o], fill=RED, width=11)
        d.line([cx-o, cy+o, cx+o, cy-o], fill=RED, width=11)

r = 34
gap = 130
cx0 = W//2 - gap
cy = 78
states = ["goal", "save", "pending"]   # demo: shot1 scored, shot2 saved, shot3 upcoming
for i, st in enumerate(states):
    ball_dot(cx0 + i*gap, cy, r, st)
# "SHOT 2/3" not requested; keep it clean per '3 ball dots' choice

# ---------- 6 aim-zone circle outlines in the goal mouth ----------
# goal mouth measured on scene: x 26%->74%, y 41%->71%
gx0, gx1 = int(W*0.285), int(W*0.715)
gy0, gy1 = int(H*0.44),  int(H*0.70)
col_x = [gx0 + (gx1-gx0)*f for f in (0.15, 0.5, 0.85)]
row_y = [gy0 + (gy1-gy0)*f for f in (0.24, 0.76)]
aim_r = int((gx1-gx0)*0.055)   # smaller circles

hovered = (2, 1)  # bottom-right circle is "hovered" in this mockup (col idx2, row idx1)
for ri, cyz in enumerate(row_y):
    for ci, cxz in enumerate(col_x):
        cxz = int(cxz); cyz = int(cyz)
        is_hover = (ci, ri) == hovered
        if is_hover:
            # glow
            glow = Image.new("RGBA", (W, H), (0,0,0,0))
            gd = ImageDraw.Draw(glow)
            gd.ellipse([cxz-aim_r-30, cyz-aim_r-30, cxz+aim_r+30, cyz+aim_r+30],
                       fill=(255,222,61,70))
            glow = glow.filter(ImageFilter.GaussianBlur(24))
            base.alpha_composite(glow)
            d.ellipse([cxz-aim_r, cyz-aim_r, cxz+aim_r, cyz+aim_r],
                      outline=YELLOW, width=12)
            d.ellipse([cxz-aim_r+14, cyz-aim_r+14, cxz+aim_r-14, cyz+aim_r-14],
                      outline=(255,255,255,230), width=5)
            # small center dot
            d.ellipse([cxz-8, cyz-8, cxz+8, cyz+8], fill=YELLOW)
        else:
            d.ellipse([cxz-aim_r, cyz-aim_r, cxz+aim_r, cyz+aim_r],
                      outline=(255,255,255,180), width=7)
            d.ellipse([cxz-aim_r, cyz-aim_r, cxz+aim_r, cyz+aim_r],
                      outline=(20,29,69,160), width=3)

# ---------- vertical power bar, right side ----------
pb_w = 58
pb_x = W - 120
pb_y0 = int(H*0.30)
pb_y1 = int(H*0.82)
# frame
d.rounded_rectangle([pb_x-10, pb_y0-46, pb_x+pb_w+10, pb_y1+16], radius=18,
                    fill=(10,16,40,200), outline=NAVY, width=5)
otext(pb_x+pb_w//2, pb_y0-40, "PWR", 34, fill=YELLOW, ow=3, anchor="ma")
# gradient fill (green->yellow->red bottom->top)
bar_h = pb_y1 - pb_y0
for i in range(bar_h):
    t = i/bar_h                      # 0 bottom .. 1 top
    if t < 0.5:
        f = t/0.5; col = (int(60+195*f), int(210+12*f), int(90-30*f))
    else:
        f = (t-0.5)/0.5; col = (int(255), int(222-162*f), int(60-0*f))
    y = pb_y1 - i
    d.line([pb_x, y, pb_x+pb_w, y], fill=col+(255,))
# current-power marker (locked mid-high for demo)
mk = pb_y1 - int(bar_h*0.72)
d.rectangle([pb_x-16, mk-9, pb_x+pb_w+16, mk+9], fill=WHITE, outline=NAVY, width=4)
d.polygon([(pb_x-16, mk-16),(pb_x-40, mk),(pb_x-16, mk+16)], fill=YELLOW, outline=NAVY)

# ---------- bottom hint ----------
otext(W//2, H-70, "PILIH TARGET  •  LALU KUNCI POWER", 40, fill=YELLOW, ow=4, anchor="ma")

out = base.convert("RGB")
out.save(SCR + "/hud_native.png")
out.resize((1100, int(1100*H/W)), Image.LANCZOS).save(SCR + "/hud_preview.png")
print("done")
