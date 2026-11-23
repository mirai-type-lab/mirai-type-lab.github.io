#!/usr/bin/env python3
"""ネタぴよニュースを作る。news/data.json を読み、一覧・記事ページ・画像・RSS・サイトマップ・llms.txt を作る。
使い方：mirai-type-lab.github.io の中で  python3 news/build.py"""
import json, os, html, datetime
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE='https://mirai-type-lab.github.io'
SITE='ネタぴよニュース'
D=json.load(open(os.path.join(ROOT,'news','data.json'),encoding='utf-8'))
D=[n for _,n in sorted(enumerate(D),key=lambda x:(x[1]['published'],x[0]),reverse=True)]  # 新しい日付→後から足した記事が上
e=html.escape
GA='''<script>(function(){try{var q=new URLSearchParams(location.search).get('me');if(q==='1')localStorage.setItem('mirai-me','1');if(q==='0')localStorage.removeItem('mirai-me');if(localStorage.getItem('mirai-me')==='1')window['ga-disable-G-PSHZSB36VV']=true;}catch(e){}})();</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-PSHZSB36VV"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-PSHZSB36VV',{allow_google_signals:false,allow_ad_personalization_signals:false});</script>'''
ORG={"@type":"Organization","name":SITE,"url":BASE+"/news/","logo":{"@type":"ImageObject","url":BASE+"/share/netapiyo/chick.png"}}
def head(title,desc,url,img,ld,depth):
    up='../'*depth
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{SITE}" href="{BASE}/news/feed.xml">
<link rel="stylesheet" href="{up}news/style.css">
<script type="application/ld+json">{json.dumps(ld,ensure_ascii=False)}</script>
{GA}
</head>
<body><div class="wrap">
<header class="site"><a href="{up}news/"><img src="{up}share/netapiyo/chick.png" alt="ネタぴよ" width="72" height="72"><span class="name">{SITE}</span></a><p class="lead">毎日の気になるニュースを、やさしく1分で。はい・いいえで「今やること」がわかる。</p></header>
'''
FOOT='''<div class="card cta"><h2>ついでに、未来の自分もチェック</h2><p>ふだんのクセから、これからのあなたのタイプと行動のクセがわかる無料の診断（50問）。</p><a class="btn" href="https://mirai-type-lab.github.io/?utm_source=news&amp;utm_medium=site&amp;utm_campaign=yesno">未来タイプ診断をやってみる</a></div>
<footer>ここにあるのは一般的な情報です。困った時は、書いてある公的な窓口に相談してね。<br>運営：ネタぴよ（未来タイプ診断ラボ）／記事は出どころの記事・公的な発表を確かめて書いています。</footer>
</div>'''
B='/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
def ogp(n,out):
    W,H=1200,630; im=Image.new('RGB',(W,H),'#FFF6E0'); d=ImageDraw.Draw(im)
    d.rounded_rectangle((30,30,W-30,H-30),40,fill='white',outline='#3A2A1A',width=8)
    f1=ImageFont.truetype(B,40,index=0); f2=ImageFont.truetype(B,64,index=0)
    d.rounded_rectangle((80,80,80+d.textlength(n['tag'],font=f1)+56,146),33,fill='#E5484D'); d.text((108,86),n['tag'],font=f1,fill='white')
    y=190; line=''
    lines=[]
    for ch in n['title']:
        if d.textlength(line+ch,font=f2)>W-420: lines.append(line); line=ch
        else: line+=ch
    lines.append(line)
    for l in lines[:4]: d.text((80,y),l,font=f2,fill='#3A2A1A'); y+=86
    d.text((80,H-110),SITE+'　はい・いいえで今やることがわかる',font=ImageFont.truetype(B,30,index=0),fill='#FF9A2E')
    ic=Image.open(os.path.join(ROOT,'share','netapiyo','chick.png')).convert('RGBA').resize((300,300)); im.paste(ic,(W-350,H-360),ic)
    im.save(out)
def jp(dt): y,m,dd=dt.split('-'); return f'{int(y)}年{int(m)}月{int(dd)}日'
os.makedirs(os.path.join(ROOT,'share','news'),exist_ok=True)
for n in D:
    url=f"{BASE}/news/{n['id']}/"; img=f"{BASE}/share/news/{n['id']}.png"
    ogp(n,os.path.join(ROOT,'share','news',n['id']+'.png'))
    desc=n['sum'][:110]
    faq=[{"@type":"Question","name":q['q'],"acceptedAnswer":{"@type":"Answer","text":"答えによって、次のどれかになります："+" ／ ".join(a['t'] for a in n['as'])}} for q in n['qs']]
    faq+=[{"@type":"Question","name":f"{n['title']}、今やることは？（{a['t']}）","acceptedAnswer":{"@type":"Answer","text":a['b']}} for a in n['as']]
    ld=[{"@context":"https://schema.org","@type":"NewsArticle","headline":n['title'],"description":desc,"image":[img],"datePublished":n['published'],"dateModified":n.get('modified',n['published']),"inLanguage":"ja","author":ORG,"publisher":ORG,"mainEntityOfPage":url,"isBasedOn":[s[1] for s in n['src']],"keywords":n.get('keywords',[])},
        {"@context":"https://schema.org","@type":"FAQPage","mainEntity":faq},
        {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":SITE,"item":BASE+"/news/"},{"@type":"ListItem","position":2,"name":n['title'],"item":url}]}]
    pts=''.join(f'<li>{e(p)}</li>' for p in n.get('points',[]))
    src='／'.join(f'<a href="{e(s[1])}" target="_blank" rel="noopener">{e(s[0])}</a>' for s in n['src'])
    allqa=''.join(f'<dt>Q{i+1}. {e(q["q"])}</dt>' for i,q in enumerate(n['qs']))+''.join(f'<dt>答え：{e(a["t"])}</dt><dd>{e(a["b"])}</dd>' for a in n['as'])
    body=head(f"{n['title']}｜はい・いいえで今やること｜{SITE}",desc,url,img,ld,2)+f'''<nav class="crumb"><a href="../">{SITE}</a> ＞ {e(n['title'])}</nav>
<article class="card"><span class="tag">{e(n['tag'])}</span><time class="date" datetime="{n['published']}">{jp(n['published'])}</time>
<h1>{e(n['title'])}</h1><p class="sum">{e(n['sum'])}</p>
{('<h2 style="margin-top:14px">ポイント</h2><ul class="points">'+pts+'</ul>') if pts else ''}
<p class="src">出どころ：{src}</p></article>
<section class="card" id="yesno"><noscript><p>はい・いいえの質問は、下の「質問と答えの一覧」で読めます。</p></noscript></section>
<section class="card"><details><summary>質問と答えの一覧</summary><dl class="all">{allqa}</dl></details></section>
<script type="application/json" id="news-data">{json.dumps(n,ensure_ascii=False).replace("</","<\\/")}</script>
<script src="../app.js"></script>
{FOOT}</body></html>'''
    os.makedirs(os.path.join(ROOT,'news',n['id']),exist_ok=True)
    open(os.path.join(ROOT,'news',n['id'],'index.html'),'w',encoding='utf-8').write(body)
# 一覧
ld=[{"@context":"https://schema.org","@type":"CollectionPage","name":SITE,"url":BASE+"/news/","inLanguage":"ja","publisher":ORG},
    {"@context":"https://schema.org","@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{BASE}/news/{n['id']}/","name":n['title']} for i,n in enumerate(D)]}]
cards=''.join(f'''<article class="card"><span class="tag">{e(n['tag'])}</span><time class="date" datetime="{n['published']}">{jp(n['published'])}</time><h2><a href="{n['id']}/">{e(n['title'])}</a></h2><p class="sum">{e(n['sum'])}</p><a class="go" href="{n['id']}/">はい・いいえで今やることを見る</a></article>''' for n in D)
open(os.path.join(ROOT,'news','index.html'),'w',encoding='utf-8').write(head(f"{SITE}｜はい・いいえで「今やること」がわかるニュースサイト","毎日の気になるニュースを、ひよこのネタぴよがやさしく紹介。記事ごとに、はい・いいえで答えると、あなたが今やることがわかります。",BASE+"/news/",f"{BASE}/share/news/{D[0]['id']}.png",ld,1)+'<script>(function(){var n=new URLSearchParams(location.search).get("n");if(n&&/^[a-z0-9-]+$/.test(n))location.replace(n+"/"+location.search.replace(/([?&])n=[^&]*&?/,"$1").replace(/[?&]$/,""))})();</script><main>'+cards+'</main>'+FOOT+'</body></html>')
# RSS
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%a, %d %b %Y %H:%M:%S +0900')
items=''.join(f"<item><title>{e(n['title'])}</title><link>{BASE}/news/{n['id']}/</link><guid>{BASE}/news/{n['id']}/</guid><pubDate>{datetime.datetime.strptime(n['published'],'%Y-%m-%d').strftime('%a, %d %b %Y 09:00:00 +0900')}</pubDate><description>{e(n['sum'])}</description></item>" for n in D)
open(os.path.join(ROOT,'news','feed.xml'),'w',encoding='utf-8').write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{SITE}</title><link>{BASE}/news/</link><description>はい・いいえで今やることがわかるニュース</description><language>ja</language><lastBuildDate>{now}</lastBuildDate>{items}</channel></rss>')
# サイトマップ
urls=[(BASE+'/','2026-11-23'),(BASE+'/news/',D[0]['published'])]+[(f"{BASE}/news/{n['id']}/",n.get('modified',n['published'])) for n in D]
open(os.path.join(ROOT,'sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{u}</loc><lastmod>{m}</lastmod></url>\n' for u,m in urls)+'</urlset>\n')
open(os.path.join(ROOT,'sitemap.txt'),'w').write(''.join(u+'\n' for u,_ in urls))
# llms.txt（AIに向けたサイトの案内）
lt=f"# 未来タイプ診断ラボ\n\n> 無料の「未来タイプ診断」と、はい・いいえで今やることがわかるニュースサイト「{SITE}」を運営しています。記事は出どころの記事・公的な発表を確かめて書いています。\n\n## 診断\n- [未来タイプ診断]({BASE}/): 50問で、ふだんのクセから未来のタイプと行動のクセがわかる無料の診断\n\n## {SITE}\n- [記事の一覧]({BASE}/news/): 毎日の気になるニュースと、はい・いいえで出る「今やること」\n- [RSS]({BASE}/news/feed.xml)\n"+''.join(f"- [{n['title']}]({BASE}/news/{n['id']}/): {n['sum'][:80]}\n" for n in D)
open(os.path.join(ROOT,'llms.txt'),'w',encoding='utf-8').write(lt)
print('built',len(D))
