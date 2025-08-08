import math
import random
from PIL import Image, ImageDraw

WIDTH, HEIGHT = 1280, 720
FRAMES = 300  # ~10s at 30fps
FPS = 30
BG_TOP = (120, 200, 255)
BG_BOTTOM = (180, 230, 255)

rng = random.Random(42)

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))

def draw_gradient_sky(draw):
    for y in range(HEIGHT):
        t = y / HEIGHT
        draw.line([(0, y), (WIDTH, y)], fill=lerp_color(BG_TOP, BG_BOTTOM, t))

def draw_hills(draw):
    # distant hills
    for i, base_y in enumerate([520, 560]):
        color = (90 - i*10, 180 - i*20, 90)
        points = []
        for x in range(0, WIDTH+20, 20):
            h = 40 + 30*math.sin(x/200 + i)
            points.append((x, base_y - h))
        points = [(0, HEIGHT)] + points + [(WIDTH, HEIGHT)]
        draw.polygon(points, fill=color)

def draw_river(draw, t):
    # simple animated river waves
    river_top = 500
    river_bottom = 700
    left = 0
    right = WIDTH
    draw.rectangle([left, river_top, right, river_bottom], fill=(100, 160, 220))
    for y in range(river_top, river_bottom, 6):
        amp = 10 + (y - river_top) * 0.03
        phase = t*2 + y*0.05
        x1 = int(100 + amp*math.sin(phase))
        x2 = int(WIDTH-100 + amp*math.sin(phase+2))
        draw.line([(x1, y), (x2, y)], fill=(140, 200, 255))


def draw_tree(draw, sway):
    trunk_base = (950, 500)
    trunk_top = (930 + int(10*math.sin(sway)), 300)
    draw.line([trunk_base, trunk_top], fill=(120, 80, 40), width=26)
    # canopy
    canopy_center = (910 + int(18*math.sin(sway)), 270)
    green = (60, 160, 70)
    for r in [110, 90, 70]:
        draw.ellipse([canopy_center[0]-r, canopy_center[1]-r,
                      canopy_center[0]+r, canopy_center[1]+r], fill=green)
        green = (green[0], min(255, green[1]+15), green[2])
    # fruits
    rng2 = random.Random(7)
    for i in range(10):
        ang = i*0.6 + 0.3
        r = 85 + 10*rng2.random()
        x = canopy_center[0] + int(r*math.cos(ang))
        y = canopy_center[1] + int(r*math.sin(ang))
        size = 16 + (i%3)*3
        draw.ellipse([x-size, y-size, x+size, y+size], fill=(230, 80, 40))


def draw_turtle(draw, x, y, look_up=False, step=0):
    # body
    shell_color = (50, 140, 70)
    draw.ellipse([x-50, y-30, x+50, y+30], fill=shell_color, outline=(30,100,50), width=3)
    # head
    hx = x+55
    hy = y-5 - (18 if look_up else 0)
    draw.ellipse([hx-20, hy-15, hx+10, hy+15], fill=(90, 170, 90))
    # eye looking up
    eye_x = hx+3
    eye_y = hy-2-(6 if look_up else 0)
    draw.ellipse([eye_x-3, eye_y-3, eye_x+3, eye_y+3], fill=(0,0,0))
    # legs (simple step animation)
    phase = step
    for i, (lx, ly) in enumerate([(-30, 28), (20, 28), (-30, -28), (20, -28)]):
        offset = int(3*math.sin(phase + i))
        draw.ellipse([x+lx-10, y+ly-6+offset, x+lx+10, y+ly+6+offset], fill=(70,140,80))


def draw_scene(frame_idx):
    t = frame_idx / FPS
    img = Image.new('RGB', (WIDTH, HEIGHT))
    d = ImageDraw.Draw(img)
    draw_gradient_sky(d)
    draw_hills(d)
    draw_river(d, t)
    draw_tree(d, sway=math.sin(t))

    # ground patch under tree
    d.ellipse([800, 520, 1180, 760], fill=(140, 190, 120))

    # multiple turtles, one looking up
    base_y = 580
    step = t*4
    turtles = [
        (400 + 20*math.sin(t*1.5), base_y + 5*math.sin(t*2), False),
        (520 + 15*math.sin(t*1.2+1), base_y + 7*math.sin(t*1.7), False),
        (680 + 10*math.sin(t*1.1+2), base_y + 4*math.sin(t*1.3), True),  # looks up
    ]
    for x, y, look_up in turtles:
        draw_turtle(d, int(x), int(y), look_up=look_up, step=step)

    # subtle shadow for the looking-up turtle
    d.ellipse([660, 600, 700, 610], fill=(60, 90, 60))

    # caption (optional): None to keep scene clean
    return img


if __name__ == '__main__':
    out_dir = 'frames'
    import os
    os.makedirs(out_dir, exist_ok=True)
    for i in range(FRAMES):
        img = draw_scene(i)
        img.save(f"{out_dir}/frame_{i:04d}.png")
    print('Frames saved to', out_dir)
