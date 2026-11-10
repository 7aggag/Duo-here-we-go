# Duo Here We Go — الـ Architecture (مسودة v0.1)

**التاريخ:** 2026-11-09 · **الحالة:** v0.1 اتبنت. القرارات D1 لـ D4 اتوافق عليها بالاقتراحات اللي تحت

## الهدف

Agent skill (لـ Claude Code وأي agent بيدعم Agent Skills) بياخد تطبيق SwiftUI أو UIKit أو Flutter موجود ويجهّزه لـ iPhone Duo. الترتيب كالتالي: skill آبل الرسمي (App Resizability) الأول، بعده الحاجات اللي آبل سايباها، ودعم **RTL والعربي** من الأساس، وفي الآخر **تقرير واحد قبل وبعد**.

**مش من هدفنا:** Flutter و React Native، والأتمتة على جهاز حقيقي، وإننا نستبدل skill آبل، وإننا نوزّع أي محتوى بتاع آبل.

## القواعد الثابتة (من التدقيق والتجربة)

1. **آبل الأول.** لو حصل تعارض نمشي ورا آبل، ونكتب الفرق في التقرير.
2. **skill آبل ماينفعش يتحط جوه أداتنا** (رخصة Xcode، البند 2.7). بنصدّره على جهاز كل مستخدم في `$TMPDIR`، وعمره ما يدخل الريبو.
3. **مانكتبش أي API قبل ما نتأكد إنه موجود في SDK الجهاز.** وأي كود جديد يتغلّف بـ `#available(iOS 27.1, *)`.
4. **مانقولش إن حاجة نجحت وهي ماتشغّلتش.** كل نتيجة بتتكتب معاها طريقة التحقق: `static` أو `simulator` أو `device` أو `unverified`.
5. **الآيفونات العادية لازم ماتتغيرش.** بوابة لقطات قبل وبعد على iPhone عادي.
6. **أرقام القواعد ليها namespace خاص بينا:** `DHWG-xxx` و `DHWG-RTL-xxx`.

## شكل الـ skill

```
duo-here-we-go/
  SKILL.md                    # المدخل: المراحل، القواعد، إمتى نسأل المستخدم
  references/
    apple-bridge.md           # تصدير skill آبل وتشغيله وتحويل نتايجه
    duo-apis.md               # ملخص APIs متراجع على SDK 27.1، وملاحظات Catalyst والـ runtime بتاع 27.2
    rtl.md                    # نتايج تجربة RTL + قايمة الفحص
    flutter.md                # قواعد Flutter وقايمة مراجعة لقطاته، والتوصيل بـ duo-adapt
    decisions.md              # (لاحقاً، مع المرحلة 5) إزاي نسجّل قرارات إعادة التصميم
  scripts/
    dhwg_common.py            # simctl، والبحث عن محاكي Duo، وتشغيل hinge
    preflight.py              # Xcode 27.1+، محاكي Duo، git، نوع المشروع، العربي
    export_apple_skills.sh
    capture.py                # يحرّك المفصلة ويصوّر كل وضعية × {en، ar}، ويستنى لحد ما الصور السودا تختفي
    dhwg_lint.py              # القواعد → findings-lint.json
    report.py                 # findings + اللقطات → REPORT.md
  vendor/hinge/               # أداة hinge (رخصة MIT، commit 06cb720)
  THIRD_PARTY_NOTICES.md
```

## المراحل

| # | المرحلة | بتعمل إيه | v0.1 |
|---|---|---|---|
| 0 | Preflight | تتأكد من الأدوات، ونوع المشروع (UIKit أو SwiftUI أو الاتنين أو Flutter)، وحالة git | ✓ (أقل نسخة) |
| 1 | Baseline | تبني التطبيق وتصوّره قبل أي تعديل: مقفول ومفتوح ونص طيّة × إنجليزي وعربي | ✓ |
| 2 | Apple pass | تشغّل skill آبل وتحوّل نتايجه لـ `findings.json` | ✓ (يدوي في الأول) |
| 3 | Duo lint | الشريط، والمناطق المحجوزة، والـ arrangements، والـ scenes، والكاميرا | لاحقاً |
| 4 | **RTL** | قواعد `DHWG-RTL-*` + تشغيل بالعربي على كل وضعية + مقارنة بالإنجليزي | ✓ |
| 5 | Fix | تصليح تلقائي للحاجات البسيطة، وسؤال المستخدم في أي إعادة تصميم | لاحقاً |
| 6 | Verify | تصوّر تاني وتقارن، ومعاها بوابة الآيفونات العادية | لاحقاً |
| 7 | **Report** | تقرير واحد: النتايج حسب المصدر، واللقطات قبل وبعد، والحاجات اللي ماتتحققتش | ✓ |

## شكل الـ finding

```json
{
  "id": "DHWG-RTL-001",
  "source": "apple | dhwg | rtl",
  "severity": "error | warn | info",
  "file": "Sources/App/SceneDelegate.swift",
  "line": 42,
  "message": "...",
  "fix": "...",
  "verified": "static | simulator | device | unverified",
  "evidence": "results/half/ar/display-3.png"
}
```

## أول قواعد RTL (من التجربة)

| القاعدة | النمط |
|---|---|
| `DHWG-RTL-001` | `UIView.appearance().semanticContentAttribute = .forceRightToLeft` من غير `traitOverrides.layoutDirection` على الـ window |
| `DHWG-RTL-002` | خلط `UIView.reservedRegions` (إحداثيات فعلية) مع `GeometryProxy.reservedRegions` بالإعداد الافتراضي `.mirrors` |
| `DHWG-RTL-003` | افتراض إن الشريط دايماً `.trailing`، أو ربطه بـ `.left`/`.right` |
| `DHWG-RTL-004` | عرض ثابت لعمود الـ sidebar أو للـ primary في `ArrangementView` |
| `DHWG-RTL-005` | تغيير اللغة من جوه التطبيق بالـ appearance proxy في كود SwiftUI |

## قرارات محتاجاك

- **D1: التحكم في المفصلة.** ننسخ أداة `artemnovichkov/hinge` جوه `vendor/` (ملفين، رخصة MIT)، ولو ماشتغلتش نطلب من المستخدم يحرّكها بإيده؟ *المقترح: أيوه.*
- **D2: لغة سكريبتات الـ lint.** Python 3 من غير مكتبات خارجية (موجود مع Xcode Command Line Tools)، ولا Swift script؟ *المقترح: Python*، لأنه أسرع في التشغيل ومش محتاج يتبني.
- **D3: النشر.** ريبو عام على GitHub برخصة MIT، ومعاه Claude Code plugin marketplace؟
- **D4: شكل التقرير.** Markdown بس في v0.1، ولا Markdown + HTML؟ *المقترح: Markdown بس في الأول.*
