# يبني talk/index.html (تطبيق طلاقة) من index.html (مِران). شغّله من جذر المستودع: python3 tools/make_talk.py
p='./index.html';s=open(p).read()
def R(a,b,c=1):
    global s
    assert s.count(a)==c,(s.count(a),a[:80]);s=s.replace(a,b)
NAME='طلاقة'
R('const CLOUD=!!FB;','const TALKONLY=true;const CLOUD=false;')
R("const KEY='miran-v1'","const KEY='talaqa-v1'")
R("\nfbStart();\ngo(cur()?'home':'who');","\nif(!TALKONLY)fbStart();\ngo(cur()?'talkList':'who');")
R("function render(){","function render(){if(TALKONLY){if(!cur()&&S.profiles.length===1){S.active=S.profiles[0].id;save()}if(cur()&&(!['talkList','talkRun','form','who','setup'].includes(view.name)||(view.name==='who'&&!view.ex)))view={name:'talkList'};else if(!cur()&&S.profiles.length&&!['who','setup','form'].includes(view.name))view={name:'who'}}",1)
R('class="brand">مِران<','class="brand">'+NAME+'<',3)
R("fetch('content.json?v=","fetch('../content.json?v=")
R('<button class="btn plain wide" data-act="parentFromWho">لوحة ولي الأمر</button>','')
R("${S.profiles.length?'إضافة مستخدمين':'مرحباً بك في مِران'}","${S.profiles.length?'إضافة مستخدمين':'مرحباً بك في "+NAME+" 👋'}")
R("<p class=\"sub\">تدريب في الإنجليزي والقدرات والتحصيلي من الأول الابتدائي إلى الثالث الثانوي. سجّل الأسماء بالعدد الذي تريد.</p>",
  "<p class=\"sub\">تكلّم الإنجليزية بصوتك مع معلّمة تسمعك وتصحّح لك، بمحادثات تناسب صفّك من الأول الابتدائي إلى الثالث الثانوي. اكتب اسمك واختر صفّك لتبدأ.</p>")
# head
R('<link rel="manifest" href="manifest.json">','<link rel="manifest" href="manifest.json">')
R('<link rel="icon" type="image/png" href="favicon-48.png">','<link rel="icon" type="image/png" href="icon-192.png">')
R('<meta name="apple-mobile-web-app-title" content="مِران">','<meta name="apple-mobile-web-app-title" content="'+NAME+'">')
R('<meta name="application-name" content="مِران">','<meta name="application-name" content="'+NAME+'">')
R('<title>مِران</title>','<title>'+NAME+' · محادثة إنجليزية</title>')
R("const APPURL='https://alfifitop2015-hub.github.io/miran/';","const APPURL='https://alfifitop2015-hub.github.io/miran/talk/';")
s=s.replace("حمّل تطبيق مِران للتدريب على الإنجليزي والقدرات والتحصيلي:","حمّل تطبيق "+NAME+" للتدرب على المحادثة الإنجليزية:")
s=s.replace("ثبّت مِران على جوالك",'ثبّت '+NAME+' على جوالك').replace("✓ مِران مثبّت على جهازك",'✓ '+NAME+' مثبّت على جهازك').replace('aria-label="تثبيت مِران كتطبيق على الجوال"','aria-label="تثبيت '+NAME+'"')
# talk list intro
R("return header()+band('المحادثة الصوتية',","return header()+band('🗣️ "+NAME+"',")
R("const hb=p&&view.name!=='home'&&view.name!=='pboard'?","const hb=!TALKONLY&&p&&view.name!=='home'&&view.name!=='pboard'?")
R('<meta name="theme-color" content="#5B4BDB">','<meta name="theme-color" content="#0EA5A4">')
R("case 'switch':if(CLOUD&&C.mode==='student'){go('who');break}S.active=null;save();go('who');break;","case 'switch':if(CLOUD&&C.mode==='student'){go('who');break}go('who',{ex:1});break;")
open('./talk/index.html','w').write(s)
print('ok',len(s))
