"""Ommaviy huquqiy sahifalar — Google Play talab qiladi (maxfiylik siyosati,
hisobni o'chirish yo'riqnomasi). Autentifikatsiyasiz ochiq."""
import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["legal"])

CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "CONTACT_EMAIL_NI_RAILWAYDA_BERING")
UPDATED = "2026-10-07"

_STYLE = """
<style>
 body{font-family:system-ui,Segoe UI,Roboto,sans-serif;max-width:760px;margin:0 auto;padding:24px 18px;
      line-height:1.65;color:#0e1b19;background:#f7fbfa}
 h1{color:#0a5d50;font-size:26px} h2{color:#0e7c6b;font-size:19px;margin-top:28px}
 li{margin:4px 0} .m{color:#54635f;font-size:14px}
</style>"""


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(
        f'<!doctype html><html lang="uz"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{title}</title>{_STYLE}</head><body>{body}</body></html>"
    )


@router.get("/privacy", response_class=HTMLResponse)
def privacy():
    return _page("Maxfiylik siyosati — Sog‘lom Pedagog", f"""
<h1>Maxfiylik siyosati</h1>
<p class="m">Sog‘lom Pedagog ilovasi · Oxirgi yangilanish: {UPDATED}</p>
<p>Sog‘lom Pedagog — OTM pedagog xodimlari uchun jismoniy faollik ilovasi. Bu hujjat qanday
ma’lumot yig‘ilishi, nima uchun kerakligi va uni qanday o‘chirish mumkinligini tushuntiradi.</p>

<h2>Qanday ma’lumotlar yig‘iladi</h2>
<ul>
 <li><b>Hisob ma’lumotlari:</b> ism-familiya, telefon raqam, parol (serverda faqat shifrlangan «hash» ko‘rinishida saqlanadi).</li>
 <li><b>Profil va salomatlik ko‘rsatkichlari (ixtiyoriy):</b> jins, tug‘ilgan sana, bo‘y, vazn. Tana massasi indeksi (BMI) va yog‘ ulushi qurilmada hisoblanadi.</li>
 <li><b>Faollik ma’lumotlari:</b> bajarilgan mashg‘ulotlar va mashqlar, mashg‘ulot qiyinligi bahosi (RPE), jismoniy test natijalari (yozish tezligi testi natijasi ham).</li>
 <li><b>Sozlamalar:</b> shrift o‘lchami, kunlik eslatma vaqti.</li>
</ul>
<p>Ilova joylashuv, kontaktlar, kamera, mikrofon yoki fayllarga kirmaydi. Reklama va uchinchi tomon
kuzatuv (analytics) xizmatlari ishlatilmaydi.</p>

<h2>Nima uchun ishlatiladi</h2>
<ul>
 <li>Hisobingizga kirish va ma’lumotlaringizni qurilmalar o‘rtasida saqlash.</li>
 <li>Mashg‘ulot rejasini yuritish va test natijalaringizni ko‘rsatish.</li>
 <li>Loyiha ma’muriyati va o‘qituvchilari (admin/instruktor) pedagoglarning umumiy jismoniy faollik natijalarini ilmiy-tadqiqot maqsadida ko‘rishi mumkin.</li>
</ul>

<h2>Saqlash va xavfsizlik</h2>
<p>Ma’lumotlar qurilmangizda (oflayn) va bizning serverimizda saqlanadi. Aloqa HTTPS orqali
shifrlanadi. Ma’lumotlar sotilmaydi va reklama uchun uchinchi shaxslarga berilmaydi.
Mashq videolari Cloudflare xizmatidan yuklab olinadi, serverga esa ma’lumotlaringiz yuborilmaydi.</p>

<h2>Bildirishnomalar</h2>
<p>Kunlik eslatma faqat siz yoqsangiz ishlaydi va qurilmaning o‘zida rejalashtiriladi.</p>

<h2>Ma’lumotni o‘chirish</h2>
<p>Ilovada: <b>Sozlama → Hisobni o‘chirish</b>. Bunda hisob va unga bog‘liq barcha ma’lumot
(profil, progress, test natijalari) serverdan butunlay o‘chiriladi. Batafsil: <a href="/delete-account">/delete-account</a>.</p>

<h2>Bolalar</h2>
<p>Ilova kattalar (pedagog xodimlar) uchun mo‘ljallangan va 13 yoshgacha bolalardan ongli ravishda ma’lumot yig‘maydi.</p>

<h2>Aloqa</h2>
<p>Savollar uchun: <b>{CONTACT_EMAIL}</b></p>
""")


@router.get("/delete-account", response_class=HTMLResponse)
def delete_account_info():
    return _page("Hisobni o‘chirish — Sog‘lom Pedagog", f"""
<h1>Hisobni va ma’lumotlarni o‘chirish</h1>
<p class="m">Sog‘lom Pedagog ilovasi</p>
<h2>Ilova orqali (tavsiya etiladi)</h2>
<ol>
 <li>Ilovani oching va hisobingizga kiring.</li>
 <li><b>Sozlama</b> bo‘limiga o‘ting.</li>
 <li>Pastdagi <b>«Hisobni o‘chirish»</b> tugmasini bosing va tasdiqlang.</li>
</ol>
<p>Hisob, profil, mashg‘ulot progressi va test natijalari serverdan <b>darhol va qaytarib bo‘lmaydigan
tarzda</b> o‘chiriladi. Qurilmadagi lokal ma’lumot ham tozalanadi.</p>
<h2>Ilovaga kira olmasangiz</h2>
<p>Ro‘yxatdan o‘tgan telefon raqamingizni <b>{CONTACT_EMAIL}</b> manziliga yuboring — hisobingiz
va barcha ma’lumotlaringiz 30 kun ichida o‘chiriladi.</p>
""")
