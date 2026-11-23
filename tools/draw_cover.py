"""Draw the mod's original geometric cover art; no external art assets."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parents[1]
im=Image.new('RGB',(1024,1024),'#101e2a');d=ImageDraw.Draw(im)
gold='#dfb864';cream='#fff0c7';teal='#24515a'
for r in range(480,40,-12):
    d.ellipse((512-r,390-r,512+r,390+r),outline='#182d39',width=2)
d.rounded_rectangle((35,35,989,989),radius=26,outline=gold,width=4)
d.line((75,82,949,82),fill=gold,width=2)
d.polygon([(215,290),(470,320),(512,350),(554,320),(809,290),(809,563),(554,593),(512,625),(470,593),(215,563)],fill=teal,outline=gold,width=5)
d.polygon([(235,272),(470,302),(512,337),(512,596),(470,568),(235,538)],fill=cream)
d.polygon([(789,272),(554,302),(512,337),(512,596),(554,568),(789,538)],fill='#e3d3a4')
for y in (394,428,462,496):
    d.line((268,y,455,y+23),fill='#ad9760',width=3)
    d.line((570,y+23,757,y),fill='#ad9760',width=3)
d.ellipse((402,174,622,394),fill='#101e2a',outline=gold,width=5)
font=lambda size:ImageFont.truetype(r'C:\Windows\Fonts\georgiab.ttf',size)
def centered(text,y,size,fill):
    d.text((512,y),text,font=font(size),fill=fill,anchor='mt')
centered('?',180,165,gold)
centered('KNOWLEDGE',659,65,cream)
centered('IS POWER',747,65,cream)
for x,letter in zip((362,462,562,662),'ABCD'):
    d.rounded_rectangle((x-32,868,x+32,930),radius=9,fill=teal,outline=gold,width=2)
    d.text((x,874),letter,font=font(35),fill=cream,anchor='mt')
im.save(root/'assets/mod.png')
print('Created original 1024px cover.')
