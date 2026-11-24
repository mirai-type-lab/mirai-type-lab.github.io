#!/usr/bin/env python3
"""ネタぴよニュースを作る。画像は無い時だけ作る（作れない機械では、ひよこの絵で代わりにする）。
news/data.json を読み、一覧・記事ページ・画像・RSS・サイトマップ・llms.txt を作る。
使い方：mirai-type-lab.github.io の中で  python3 news/build.py"""
import json, os, html, datetime
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image=None
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
    out=os.path.join(ROOT,'share','news',n['id']+'.png')
    if not os.path.exists(out):
        try: ogp(n,out)
        except Exception as ex: print('画像は作れなかった（文字の形が無い等）:',n['id'],ex)
    if not os.path.exists(out): img=f"{BASE}/share/netapiyo/chick.png"
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
# カテゴリ（記事の cat。無い時は「くらし」）
CATS=[('bousai','天気・防災'),('chui','注意・詐欺'),('kurashi','くらし・健康'),('keizai','経済・お金'),('seiji','政治'),('odekake','おでかけ・旅行'),('kagaku','科学・宇宙')]
CN=dict(CATS)
for n in D: n['cat']=n.get('cat') if n.get('cat') in CN else 'kurashi'
def chips(cur,depth):
    pre='../'*depth
    a=[f'<a class="chip{" on" if cur=="" else ""}" href="{pre}">すべて</a>']
    for k,v in CATS:
        if any(n['cat']==k for n in D): a.append(f'<a class="chip{" on" if cur==k else ""}" href="{pre}c/{k}/">{e(v)}</a>')
    return '<nav class="chips" aria-label="カテゴリ">'+''.join(a)+'</nav>'
def card(n,depth):
    pre='../'*depth
    return f'''<article class="card" data-cat="{n['cat']}"><span class="tag">{e(CN[n['cat']])}</span><time class="date" datetime="{n['published']}">{jp(n['published'])}</time><h2><a href="{pre}{n['id']}/">{e(n['title'])}</a></h2><p class="sum">{e(n['sum'])}</p><a class="go" href="{pre}{n['id']}/">はい・いいえで今やることを見る</a></article>'''
CHIPCSS='<style>.chips{display:flex;gap:8px;overflow-x:auto;padding:4px 2px 12px;margin-bottom:4px;-webkit-overflow-scrolling:touch}.chip{flex:0 0 auto;border:2px solid #3A2A1A;background:#fff;color:#3A2A1A;border-radius:999px;padding:7px 14px;font-weight:700;font-size:14px;text-decoration:none}.chip.on{background:#3A2A1A;color:#fff}</style>'
# カテゴリごとのページ
for k,v in CATS:
    L=[n for n in D if n['cat']==k]
    if not L: continue
    os.makedirs(os.path.join(ROOT,'news','c',k),exist_ok=True)
    cl=[{"@context":"https://schema.org","@type":"CollectionPage","name":f"{v}のニュース｜{SITE}","url":f"{BASE}/news/c/{k}/","inLanguage":"ja","publisher":ORG},
        {"@context":"https://schema.org","@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{BASE}/news/{n['id']}/","name":n['title']} for i,n in enumerate(L)]}]
    open(os.path.join(ROOT,'news','c',k,'index.html'),'w',encoding='utf-8').write(head(f"{v}のニュース｜{SITE}",f"{v}の気になるニュースを、ひよこのネタぴよがやさしく紹介。はい・いいえで答えると、今やることがわかります。",f"{BASE}/news/c/{k}/",f"{BASE}/share/news/{L[0]['id']}.png",cl,3)+CHIPCSS+'<main>'+chips(k,2)+''.join(card(n,2) for n in L)+'</main>'+FOOT+'</body></html>')

RECJS="""<div id="rec"></div><div id="ob" class="ob" hidden><div class="obi"><p class="obh">どのニュースが気になる？</p><p class="obs">えらんだ話題を「あなたへのおすすめ」で上に出すよ（いくつでもOK・このスマホの中だけに保存）</p><div class="obc">"""+''.join(f'<button type="button" class="chip" data-k="{k}">{e(v)}</button>' for k,v in CATS)+"""</div><button type="button" class="obok">これで決定</button><button type="button" class="obno">あとで</button></div></div>
<script>(function(){
var K='np-likes',C='np-clicks';function get(k,d){try{return JSON.parse(localStorage.getItem(k))||d}catch(e){return d}}function set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function ev(n,p){try{gtag('event',n,p||{})}catch(e){}}
var NAMES="""+json.dumps(CN,ensure_ascii=False)+""";
var cards=[].slice.call(document.querySelectorAll('main .card[data-cat]'));
// 記事を開いたらそのカテゴリを1点（好みを少しずつ覚える）
cards.forEach(function(c){c.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){var x=get(C,{});x[c.dataset.cat]=(x[c.dataset.cat]||0)+1;set(C,x)})})});
function score(cat){var l=get(K,null)||[],x=get(C,{});return (l.indexOf(cat)>=0?10:0)+(x[cat]||0)}
function draw(){
 var box=document.getElementById('rec');var l=get(K,null);box.innerHTML='';if(!l||!l.length&&!Object.keys(get(C,{})).length)return;
 var pick=cards.filter(function(c){return score(c.dataset.cat)>0}).sort(function(a,b){return score(b.dataset.cat)-score(a.dataset.cat)}).slice(0,4);
 if(!pick.length)return;
 var h=document.createElement('div');h.className='rech';h.innerHTML='<b>🐣 あなたへのおすすめ</b><button type="button" class="recedit">好みを変える</button>';box.appendChild(h);
 pick.forEach(function(c){var k=c.cloneNode(true);k.classList.add('recc');k.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){ev('np_rec_click',{cat:c.dataset.cat})})});box.appendChild(k)});
 var t=document.createElement('p');t.className='rech';t.innerHTML='<b>📰 新しい順</b>';box.appendChild(t);
 h.querySelector('.recedit').onclick=open;
}
function open(){var ob=document.getElementById('ob'),l=get(K,[])||[];ob.hidden=false;ob.querySelectorAll('.obc .chip').forEach(function(b){b.classList.toggle('on',l.indexOf(b.dataset.k)>=0);b.onclick=function(){b.classList.toggle('on')}});
 ob.querySelector('.obok').onclick=function(){var v=[].slice.call(ob.querySelectorAll('.obc .chip.on')).map(function(b){return b.dataset.k});set(K,v);ob.hidden=true;ev('np_interest',{cats:v.map(function(k){return NAMES[k]}).join(',')});draw();window.scrollTo(0,0)};
 ob.querySelector('.obno').onclick=function(){set(K,[]);ob.hidden=true;draw()}}
var main=document.querySelector('main');main.insertBefore(document.getElementById('rec'),main.querySelector('.card'));
if(get(K,null)===null)open();draw();
})();</script>
<style>.ob{position:fixed;inset:0;background:rgba(58,42,26,.55);display:flex;align-items:flex-end;justify-content:center;z-index:20}.ob[hidden]{display:none}.obi{background:#FFF8E7;border:3px solid #3A2A1A;border-radius:24px 24px 0 0;padding:22px 18px 28px;width:100%;max-width:560px}.obh{font-weight:900;font-size:19px;margin-bottom:6px}.obs{font-size:13px;color:#6b5a48;margin-bottom:14px;line-height:1.6}.obc{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}.obok{display:block;width:100%;background:#FFC83D;border:3px solid #3A2A1A;border-radius:999px;padding:13px;font-weight:900;font-size:16px;margin-bottom:8px}.obno{display:block;width:100%;background:none;border:0;color:#6b5a48;font-size:14px;padding:6px}.rech{display:flex;justify-content:space-between;align-items:center;margin:6px 2px 10px;font-size:16px}.recedit{background:#fff;border:2px solid #3A2A1A;border-radius:999px;padding:4px 12px;font-size:12px;font-weight:700}.recc{border-color:#E5484D}</style>"""
# 一覧
ld=[{"@context":"https://schema.org","@type":"CollectionPage","name":SITE,"url":BASE+"/news/","inLanguage":"ja","publisher":ORG},
    {"@context":"https://schema.org","@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{BASE}/news/{n['id']}/","name":n['title']} for i,n in enumerate(D)]}]
cards=chips('',0)+''.join(card(n,0) for n in D)
open(os.path.join(ROOT,'news','index.html'),'w',encoding='utf-8').write(head(f"{SITE}｜はい・いいえで「今やること」がわかるニュースサイト","毎日の気になるニュースを、ひよこのネタぴよがやさしく紹介。記事ごとに、はい・いいえで答えると、あなたが今やることがわかります。",BASE+"/news/",f"{BASE}/share/news/{D[0]['id']}.png",ld,1)+CHIPCSS+'<script>(function(){var n=new URLSearchParams(location.search).get("n");if(n&&/^[a-z0-9-]+$/.test(n))location.replace(n+"/"+location.search.replace(/([?&])n=[^&]*&?/,"$1").replace(/[?&]$/,""))})();</script><main>'+cards+'</main>'+RECJS+FOOT+'</body></html>')
# RSS
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%a, %d %b %Y %H:%M:%S +0900')
items=''.join(f"<item><title>{e(n['title'])}</title><link>{BASE}/news/{n['id']}/</link><guid>{BASE}/news/{n['id']}/</guid><pubDate>{datetime.datetime.strptime(n['published'],'%Y-%m-%d').strftime('%a, %d %b %Y 09:00:00 +0900')}</pubDate><description>{e(n['sum'])}</description></item>" for n in D)
open(os.path.join(ROOT,'news','feed.xml'),'w',encoding='utf-8').write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{SITE}</title><link>{BASE}/news/</link><description>はい・いいえで今やることがわかるニュース</description><language>ja</language><lastBuildDate>{now}</lastBuildDate>{items}</channel></rss>')
# サイトマップ
urls=[(BASE+'/','2026-11-23'),(BASE+'/shindan/love/','2026-11-23'),(BASE+'/news/',D[0]['published'])]+[(f"{BASE}/news/c/{k}/",[n for n in D if n['cat']==k][0]['published']) for k,_ in CATS if any(n['cat']==k for n in D)]+[(f"{BASE}/news/{n['id']}/",n.get('modified',n['published'])) for n in D]
open(os.path.join(ROOT,'sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{u}</loc><lastmod>{m}</lastmod></url>\n' for u,m in urls)+'</urlset>\n')
open(os.path.join(ROOT,'sitemap.txt'),'w').write(''.join(u+'\n' for u,_ in urls))
# llms.txt（AIに向けたサイトの案内）
lt=f"# 未来タイプ診断ラボ\n\n> 無料の「未来タイプ診断」と、はい・いいえで今やることがわかるニュースサイト「{SITE}」を運営しています。記事は出どころの記事・公的な発表を確かめて書いています。\n\n## 診断\n- [未来タイプ診断]({BASE}/): 50問で、ふだんのクセから未来のタイプと行動のクセがわかる無料の診断\n- [恋愛のクセ診断]({BASE}/shindan/love/): 12問で、恋愛での自分のクセを6タイプで占うあそびの診断（結果ごとに今やること1つ）\n\n## {SITE}\n- [記事の一覧]({BASE}/news/): 毎日の気になるニュースと、はい・いいえで出る「今やること」\n- [RSS]({BASE}/news/feed.xml)\n"+''.join(f"- [{v}のニュース]({BASE}/news/c/{k}/)\n" for k,v in CATS if any(n['cat']==k for n in D))+''.join(f"- [{n['title']}]({BASE}/news/{n['id']}/): {n['sum'][:80]}\n" for n in D)
open(os.path.join(ROOT,'llms.txt'),'w',encoding='utf-8').write(lt)
print('built',len(D))
