"""Refresh the profile's framed statistics: python scripts/refresh_stats.py.

Only public profile data is requested. The capture date appears on each card.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET
import re

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
DATE=datetime.now(timezone(timedelta(hours=-5))).strftime('%d/%m/%Y')

def fetch(url, prefix, x, y, width, height):
    req=Request(url,headers={'User-Agent':'Angel-ETECH-profile'})
    with urlopen(req,timeout=45) as response:
        raw=response.read().decode('utf-8')
    root=ET.fromstring(raw)
    if 'Something went wrong' in raw or 'Deployment' in raw:
        raise RuntimeError('The statistics provider returned an error card.')
    for el in root.iter():
        if el.get('style'):
            declarations=[d for d in el.get('style').split(';') if d.strip() and not d.strip().startswith(('opacity:', 'animation:'))]
            el.set('style',';'.join(declarations))
        if 'id' in el.attrib:
            el.set('id',prefix+el.get('id'))
        for key,value in list(el.attrib.items()):
            el.set(key,re.sub(r'url\(#([^)]*)\)',lambda m:'url(#'+prefix+m[1]+')',value))
    w=re.sub('[^0-9.]','',root.get('width','495'))
    h=re.sub('[^0-9.]','',root.get('height','195'))
    if not root.get('viewBox'):
        root.set('viewBox',f'0 0 {w} {h}')
    root.set('x',str(x));root.set('y',str(y))
    root.set('width',str(width));root.set('height',str(height))
    return ET.tostring(root,encoding='unicode')

def frame(title,body,h):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{h}" viewBox="0 0 1000 {h}">
<defs><linearGradient id="edge"><stop stop-color="#00e4ef"/><stop offset=".52" stop-color="#29496d"/><stop offset="1" stop-color="#f12bdc"/></linearGradient>
<pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="#16233a" stroke-width=".5"/></pattern></defs>
<path d="M28 5H238L250 14H568L581 5H970L994 29V{h-31}L971 {h-7}H755L743 {h-15}H397L385 {h-7}H28L6 {h-29}V30Z" fill="#050916" stroke="url(#edge)" stroke-width="2"/>
<path d="M28 5H238L250 14H568L581 5H970L994 29V{h-31}L971 {h-7}H755L743 {h-15}H397L385 {h-7}H28L6 {h-29}V30Z" fill="url(#grid)" opacity=".5"/>
<path d="M17 69V34L34 17H132 M866 17H963L982 36V66 M19 {h-70}V{h-37}L36 {h-20}H128 M872 {h-20}H965L982 {h-37}V{h-64}" fill="none" stroke="url(#edge)" opacity=".6"/>
<path d="M24 72L33 63V37L42 28H77L86 37V63L77 72Z" fill="#081329" stroke="#00e4ef"/>
<text x="59" y="56" text-anchor="middle" fill="#00e4ef" font-family="Consolas,monospace" font-size="20">//</text>
<text x="109" y="55" fill="#f4f5ff" font-family="Segoe UI,Arial,sans-serif" font-size="27" font-weight="700">{title}</text>
<path d="M110 75H930" stroke="#21314a"/><path d="M110 75H203" stroke="#00e4ef"/><path d="M911 75H950" stroke="#f12bdc"/>
{body}
<text x="55" y="{h-36}" fill="#7788a9" font-family="Consolas,monospace" font-size="14">DATOS PÚBLICOS · ACTUALIZADO {DATE}</text>
<path d="M907 {h-16}l8 -8m0 8l8 -8m0 8l8 -8m0 8l8 -8m0 8l8 -8m0 8l8 -8m0 8l8 -8" stroke="#f12bdc" stroke-width="3"/>
</svg>'''

common='&hide_border=true&bg_color=00000000&title_color=00e4ef&text_color=a9b6ce&icon_color=f12bdc&disable_animations=true'
summary=fetch('https://github-readme-stats.vercel.app/api?username=Angel-ETECH&show_icons=true'+common,'s_',35,90,465,225)
languages=fetch('https://github-readme-stats.vercel.app/api/top-langs/?username=Angel-ETECH&layout=compact'+common,'l_',520,90,440,225)
streak=fetch('https://github-readme-streak-stats.herokuapp.com/?user=Angel-ETECH&hide_border=true&background=00000000&stroke=35406A&ring=F12BDC&fire=F12BDC&currStreakNum=F4F5FF&sideNums=00E4EF&currStreakLabel=00E4EF&sideLabels=A9B6CE&dates=A9B6CE','r_',130,85,740,240)
(ASSETS/'07-stats.svg').write_text(frame('ACTIVIDAD EN GITHUB',summary+languages,380),encoding='utf-8')
(ASSETS/'07-streak.svg').write_text(frame('CONSTANCIA Y CONTRIBUCIONES',streak,390),encoding='utf-8')
print('Statistics refreshed:',DATE)
