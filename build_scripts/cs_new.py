from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# SCR = this script's own folder (holds stadium_empty.png + output pngs).
# PROJ = the project root (one level up from build_scripts/).
SCR  = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(SCR)
FLAGS = PROJ + "/flags"

W, H = 1344, 768
YELLOW = (255, 222, 61)
NAVY   = (18, 26, 64)
NAVYO  = (20, 29, 69)   # outline navy
WHITE  = (255, 255, 255)

def font(sz):
    for n in ["arialbd.ttf", "DejaVuSans-Bold.ttf"]:
        try: return ImageFont.truetype(n, sz)
        except: pass
    return ImageFont.load_default()

# ---------- backdrop: dimmed stadium ----------
bg = Image.open(SCR + "/stadium_empty.png").convert("RGBA").resize((W, H), Image.LANCZOS)
# hard dark-navy scrim so flags dominate
bg.alpha_composite(Image.new("RGBA", (W, H), (6, 10, 30, 190)))
# subtle vignette
vig = Image.new("L", (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-W*0.35, -H*0.35, W*1.35, H*1.35], fill=110)
vig = vig.filter(ImageFilter.GaussianBlur(120))
dark = Image.new("RGBA", (W, H), (0, 0, 6, 255))
dark.putalpha(Image.eval(vig, lambda a: 150 - a if 150 - a > 0 else 0))
bg.alpha_composite(dark)
d = ImageDraw.Draw(bg)

# ---------- flag preprocessing ----------
def clean_colombia(im):
    """Rebuild Colombia as clean bands to kill the checkerboard artifact."""
    w, h = im.size
    out = Image.new("RGB", (w, h))
    dd = ImageDraw.Draw(out)
    C_Y = (252, 209, 22); C_B = (0, 56, 147); C_R = (206, 17, 38)
    dd.rectangle([0, 0, w, int(h*0.50)], fill=C_Y)
    dd.rectangle([0, int(h*0.50), w, int(h*0.75)], fill=C_B)
    dd.rectangle([0, int(h*0.75), w, h], fill=C_R)
    return out

def load_flag(name):
    im = Image.open(FLAGS + "/f_" + name + ".png").convert("RGB")
    if name == "colombia":
        return clean_colombia(im)
    return im

def trim_border(im):
    """Strip any decorative frame (black/white/colored) around the flag by
    scanning inward from each edge. An edge line is 'border' while it stays
    close to that edge's own starting color; we advance until it changes a lot."""
    p = im.load(); w, h = im.size

    def line_avg_col(x):
        rs=gs=bs=0; n=0
        for y in range(0, h, 4):
            r,g,b = p[x,y]; rs+=r; gs+=g; bs+=b; n+=1
        return (rs/n, gs/n, bs/n)
    def line_avg_row(y):
        rs=gs=bs=0; n=0
        for x in range(0, w, 4):
            r,g,b = p[x,y]; rs+=r; gs+=g; bs+=b; n+=1
        return (rs/n, gs/n, bs/n)
    def cdiff(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])+abs(a[2]-b[2])

    def scan(get, span):
        base = get(0)
        # a real frame is dark or near-uniform; walk in while line ~ base OR very dark/near-white uniform
        i = 0
        while i < span//3:
            cur = get(i)
            avg = sum(cur)/3
            uniform = (max(cur)-min(cur) < 40)
            darkish = avg < 70
            whitish = avg > 225
            near_base = cdiff(cur, base) < 55
            if (near_base or (uniform and (darkish or whitish))):
                i += 1
            else:
                break
        return i

    l = scan(lambda i: line_avg_col(i), w)
    r = scan(lambda i: line_avg_col(w-1-i), w)
    t = scan(lambda i: line_avg_row(i), h)
    b = scan(lambda i: line_avg_row(h-1-i), h)
    # safety clamp
    l=min(l,int(w*0.18)); r=min(r,int(w*0.18)); t=min(t,int(h*0.18)); b=min(b,int(h*0.18))
    box = (l, t, w-r, h-b)
    if box[2]-box[0] < w*0.4 or box[3]-box[1] < h*0.4:
        return im
    return im.crop(box)

# flags regenerated edge-to-edge (already full-bleed, DO NOT trim)
NO_TRIM = {"norway", "england", "usa", "portugal", "egypt", "colombia"}

def fill_tile(im, tw, th, pxw=64, trim=True):
    """optionally trim frame, contain-fit whole flag into tile on navy, then pixelate."""
    if trim:
        im = trim_border(im)
    sw, sh = im.size
    scale = min(tw/sw, th/sh)          # CONTAIN: whole flag visible, nothing cropped
    nw, nh = max(1,int(sw*scale)), max(1,int(sh*scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    tile = Image.new("RGB", (tw, th), NAVY)   # navy fill behind any letterbox
    tile.paste(im, ((tw-nw)//2, (th-nh)//2))
    # pixelate to chunky scale
    pxh = max(1, int(th*(pxw/tw)))
    tile = tile.resize((pxw, pxh), Image.LANCZOS).resize((tw, th), Image.NEAREST)
    return tile.convert("RGBA")

# ---------- header ----------
def ctext(s, y, sz, fill, ow=4, oc=NAVYO, shadow=True):
    f = font(sz); w = d.textbbox((0,0), s, font=f)[2]; x = (W-w)//2
    if shadow:
        d.text((x+ow+2, y+ow+3), s, font=f, fill=(0,0,10))
    for dx in range(-ow, ow+1):
        for dy in range(-ow, ow+1):
            if dx or dy: d.text((x+dx, y+dy), s, font=f, fill=oc)
    d.text((x, y), s, font=f, fill=fill)

ctext("PILIH NEGARAMU", 34, 58, YELLOW, ow=5)

# RevoU roundel top-left
if os.path.exists(PROJ + "/revou-logo.png"):
    rl = Image.open(PROJ + "/revou-logo.png").convert("RGBA").resize((64, 64), Image.LANCZOS)
    bg.alpha_composite(rl, (26, 26))

# ---------- grid ----------
flags = [("NORWAY","norway"),("ENGLAND","england"),("FRANCE","france"),("MOROCCO","morocco"),
         ("ARGENTINA","argentina"),("USA","usa"),("PORTUGAL","portugal"),("SPAIN","spain"),
         ("BELGIUM","belgium"),("SWITZERLAND","switzerland"),("COLOMBIA","colombia"),("EGYPT","egypt")]

cols, rows = 4, 3
grid_top = 118        # clear space below header
grid_bottom = H - 62  # clear space above footer
gutter = 40           # wider horizontal distance between flags
name_h = 34           # name bar BELOW the flag
gap_y = 34            # wider vertical distance between rows
scale = 0.86          # shrink tiles overall

grid_h = grid_bottom - grid_top
side_margin = int(W * 0.05)
# height available per tile once gaps + name bars are removed
tile_h_max = (grid_h - (rows-1)*gap_y) // rows
flag_h = tile_h_max - name_h
# width-derived flag height (3:2); take the smaller so the grid always fits
flag_w_fit = (W - 2*side_margin - (cols-1)*gutter) // cols
flag_h = int(min(flag_h, int(flag_w_fit * 2/3)) * scale)   # shrink
tile_w = int(flag_h * 3/2)          # keep flags a true 3:2
tile_h = flag_h + name_h

# recentre both axes with the reduced tile size
row_w = cols*tile_w + (cols-1)*gutter
start_x = (W - row_w)//2
start_y = grid_top + (grid_h - (rows*tile_h + (rows-1)*gap_y))//2

for i, (nm, fn) in enumerate(flags):
    c = i % cols; r = i // cols
    tx = start_x + c*(tile_w+gutter)
    ty = start_y + r*(tile_h+gap_y)
    # drop shadow (whole tile)
    sh = Image.new("RGBA", (tile_w+24, tile_h+24), (0,0,0,0))
    ImageDraw.Draw(sh).rectangle([12,14,12+tile_w,14+tile_h], fill=(0,0,8,150))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    bg.alpha_composite(sh, (tx-12, ty-10))
    # flag fills ONLY the flag area (whole flag visible, nothing covered)
    fl = fill_tile(load_flag(fn), tile_w, flag_h, trim=(fn not in NO_TRIM))
    bg.alpha_composite(fl, (tx, ty))
    # solid navy name bar BELOW the flag (does not cover the flag)
    d.rectangle([tx, ty+flag_h, tx+tile_w, ty+tile_h], fill=(12, 18, 46))
    f = font(22); tw = d.textbbox((0,0), nm, font=f)[2]
    d.text((tx+(tile_w-tw)//2, ty+flag_h+9), nm, font=f, fill=WHITE)
    # thin gold keyline around the whole tile (flag + name bar)
    d.rectangle([tx, ty, tx+tile_w-1, ty+tile_h-1], outline=YELLOW, width=2)
    # thin divider between flag and name bar
    d.line([tx, ty+flag_h, tx+tile_w-1, ty+flag_h], fill=YELLOW, width=1)

# ---------- footer ----------
ctext("Pilih tim-mu untuk mulai main!", H-46, 26, YELLOW, ow=3)

out = bg.convert("RGB")
out.save(PROJ + "/country_select.png")
out.resize((1024, int(1024*H/W)), Image.LANCZOS).save(SCR + "/cs_new_preview.png")
print("done", tile_w, tile_h, gap_y)
