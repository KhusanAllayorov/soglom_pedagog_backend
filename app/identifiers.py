"""Login identifikatorini (telefon) tekshirish va bir ko'rinishga keltirish.

Foydalanuvchi telefon raqami bilan ro'yxatdan o'tadi va kiradi. Bazaga
saqlashdan oldin raqam shu yerda normallashtiriladi — shunda
"+998 90 123 45 67" va "998901234567" bir xil raqam deb qabul qilinadi.
"""

import re

# O'zbekiston raqami: +998 dan keyin 9 ta raqam.
_UZ_PHONE_RE = re.compile(r"^998\d{9}$")


def normalize_phone(raw: str | None) -> str | None:
    """O'zbekiston raqamini `+998XXXXXXXXX` ko'rinishiga keltiradi.

    Qabul qilinadi: `+998901234567`, `998901234567`, `90 123 45 67`,
    `(90) 123-45-67`. To'g'ri bo'lmasa None.
    """
    if not raw:
        return None

    digits = re.sub(r"\D", "", raw)

    # Faqat operator kodi + raqam kiritilgan bo'lsa (9 ta raqam) — 998 qo'shamiz.
    if len(digits) == 9:
        digits = "998" + digits
    # 8 bilan boshlanuvchi eski ichki format: 8 90 123 45 67
    elif len(digits) == 10 and digits.startswith("8"):
        digits = "998" + digits[1:]

    return "+" + digits if _UZ_PHONE_RE.match(digits) else None
