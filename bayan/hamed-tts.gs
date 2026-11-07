/**
 * خدمة صوت «حامد» لتطبيق «بيان» — Google Apps Script
 * تستقبل نصًا عربيًا وتعيده صوتًا بصوت ar-SA-HamedNeural من خدمة Microsoft Azure Speech الرسمية.
 * المفتاح محفوظ في «خصائص السكربت» ولا يظهر في الموقع.
 *
 * الإعداد (مرة واحدة):
 *   1) من «إعدادات المشروع ⚙️» ← «خصائص السكربت» أضف:
 *        AZURE_KEY     = مفتاح خدمة الكلام (Key 1)
 *        AZURE_REGION  = منطقة الخدمة كما تظهر في Azure (مثل: uaenorth أو eastus)
 *   2) «نشر» ← «نشر جديد» ← النوع «تطبيق ويب» ← التنفيذ باسم «أنا» ← من يمكنه الوصول «أي شخص».
 *   3) انسخ رابط تطبيق الويب (ينتهي بـ /exec) وأرسله.
 *
 * للتجربة: افتح الرابط في المتصفح مضافًا إليه  ?text=مرحبا  — يجب أن يظهر {"audio":"..."}
 */
const VOICE = 'ar-SA-HamedNeural';
const ALLOWED_RATES = /^[-+]?\d{1,2}%$/;

function doGet(e) { return handle_((e && e.parameter) || {}); }
function doPost(e) {
  let p = {};
  try { p = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) {}
  return handle_(p);
}

function handle_(p) {
  const text = String(p.text || '').trim().slice(0, 1500);
  if (!text) return out_({ error: 'no text' });
  const rate = ALLOWED_RATES.test(String(p.rate || '')) ? String(p.rate) : '-10%';
  const props = PropertiesService.getScriptProperties();
  const key = props.getProperty('AZURE_KEY'), region = props.getProperty('AZURE_REGION') || 'uaenorth';
  if (!key) return out_({ error: 'missing AZURE_KEY' });

  // تخزين مؤقت: الجملة نفسها لا تُطلب من Microsoft مرتين (يوفّر الوقت والرصيد المجاني)
  const cache = CacheService.getScriptCache();
  const ck = 'h' + Utilities.base64EncodeWebSafe(
    Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, VOICE + '|' + rate + '|' + text, Utilities.Charset.UTF_8)).slice(0, 40);
  const hit = cache.get(ck);
  if (hit) return out_({ audio: hit, cached: true });

  const ssml = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-SA">' +
    '<voice name="' + VOICE + '"><prosody rate="' + rate + '">' + esc_(text) + '</prosody></voice></speak>';
  const r = UrlFetchApp.fetch('https://' + region + '.tts.speech.microsoft.com/cognitiveservices/v1', {
    method: 'post',
    contentType: 'application/ssml+xml; charset=utf-8',
    payload: Utilities.newBlob(ssml, 'application/ssml+xml').getBytes(),
    headers: {
      'Ocp-Apim-Subscription-Key': key,
      'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
      'User-Agent': 'bayan-tts'
    },
    muteHttpExceptions: true
  });
  const code = r.getResponseCode();
  if (code !== 200) return out_({ error: 'azure ' + code, detail: r.getContentText().slice(0, 200) });
  const b64 = Utilities.base64Encode(r.getContent());
  if (b64.length < 95000) { try { cache.put(ck, b64, 21600); } catch (err) {} }
  return out_({ audio: b64 });
}

function esc_(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');
}
function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/** لتجربة الإعداد من داخل المحرر: اختر الدالة test ثم «تشغيل» وراجع السجل */
function test() {
  const res = JSON.parse(handle_({ text: 'مَرْحَبًا، أَنَا المُحَاوِرُ فِي سَاحَةِ المُوَاجَهَة.' }).getContent());
  Logger.log(res.error ? ('خطأ: ' + res.error + ' ' + (res.detail || '')) : ('تم ✓ طول الصوت: ' + res.audio.length));
}
