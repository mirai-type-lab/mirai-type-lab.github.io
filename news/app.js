// ネタぴよニュース：記事ページの「はい・いいえ」。中身は各ページの <script type="application/json" id="news-data">。
(function(){
var el=document.getElementById('news-data'),box=document.getElementById('yesno');if(!el||!box)return;
var n=JSON.parse(el.textContent);
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function ev(name,p){try{gtag('event',name,p)}catch(e){}}
function go(st,push){if(push)history.pushState(st,'');else history.replaceState(st,'');draw(st)}
function draw(st){
 if(!st||st.v==='top'){box.innerHTML='<p class="q">はい・いいえで答えると、あなたが今やることがわかるよ</p><button class="go" id="yn-start">はい・いいえで答える</button>';document.getElementById('yn-start').onclick=function(){ev('news_start',{news_id:n.id});go({v:'q',i:0,k:1},true)};return}
 if(st.v==='q'){var q=n.qs[st.i];box.innerHTML='<p class="step">しつもん '+st.k+'</p><p class="q">'+esc(q.q)+'</p><div class="btns"><button class="yes">はい</button><button class="no">いいえ</button></div>';
  box.querySelector('.yes').onclick=function(){step(q.yes,st.k)};box.querySelector('.no').onclick=function(){step(q.no,st.k)};return}
 if(st.v==='a'){var a=n.as[st.j];var u=encodeURIComponent(location.origin+location.pathname+'?utm_source=share');var tx=encodeURIComponent('「'+n.title+'」にはい・いいえで答えたら、今やることがわかった #ネタぴよニュース #ニュース');
  box.innerHTML='<p class="step">あなたが今やること</p><div class="ans"><b>'+esc(a.t)+'</b>'+esc(a.b)+'</div>'+(a.l&&a.l.length?'<p class="src">'+a.l.map(function(l){return '▶ <a href="'+l[1]+'" target="_blank" rel="noopener">'+esc(l[0])+'</a>'}).join('<br>')+'</p>':'')+'<div class="row"><a href="https://x.com/intent/post?text='+tx+'&url='+u+'" target="_blank" rel="noopener">Xでシェア</a><a href="https://social-plugins.line.me/lineit/share?url='+u+'" target="_blank" rel="noopener">LINEで送る</a></div><div class="row"><button id="yn-again">もう一回</button><a href="../">ほかのニュース</a></div>';
  document.getElementById('yn-again').onclick=function(){go({v:'q',i:0,k:1},true)}}
}
function step(v,k){if(typeof v==='string'&&v.indexOf('a:')===0){var j=+v.slice(2);ev('news_answer',{news_id:n.id,answer_no:j});go({v:'a',j:j},true)}else go({v:'q',i:v,k:k+1},true);box.scrollIntoView({block:'start'})}
window.addEventListener('popstate',function(e){draw(e.state)});
go(history.state||{v:'top'},false);
})();
