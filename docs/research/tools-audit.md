# تدقيق أدوات iPhone Duo — رخص، تغطية، فجوات، ومقترح معمارية الـ orchestrator

**التاريخ:** 2026-11-09 · **المنهج:** قراءة فقط (ملفات الريبو اتسحبت كـ tarball عبر `gh api` واتقرت offline، ومفيش أي كود اتشغّل منها) · **كل الأرقام (نجوم/آخر commit) لحظة التدقيق.**

> **تنبيه مهم:** أي حاجة متعلمة **(غير متحقق منها)** معناها إني ملقتش دليل مباشر، فمتبنيش عليها قرار من غير ما تتأكد. الجزء القانوني (رخصة Xcode) مش استشارة قانونية.

---

## 1. جدول الرخص والنضج

| الريبو | الرخصة | ⭐ | آخر push | الحجم/النضج | الحكم |
|---|---|---|---|---|---|
| [bones7456/iphone-duo-skill](https://github.com/bones7456/iphone-duo-skill) | MIT | 1 | 2026-10-10 | صغير (33 KB، 5 commits، skill واحد + سكريبتين) — "دليل ميداني" من تطبيق حقيقي | **نقدر نقتبس كود** مع attribution |
| [hechen/iphone-duo-skills](https://github.com/hechen/iphone-duo-skills) | MIT | 7 | 2026-09-27 | متوسط (8 skills، SOURCES.md، validate CI، multi-agent install) | **نقدر نقتبس كود** |
| [MustafaNatur/iphone-duo-adaptive-skill](https://github.com/MustafaNatur/iphone-duo-adaptive-skill) | **لا توجد رخصة** | 0 | 2026-10-10 | متوسط (26 ملف، سكريبتات capture/audit/preflight، bridge لسكيلات Apple) | **أفكار فقط** — ممنوع نسخ أي سطر |
| [anatoliykant/iphone-duo-plugin](https://github.com/anatoliykant/iphone-duo-plugin) | MIT + NOTICE (اقتباسات Apple المعلّمة VERBATIM مستثناة) | 1 | 2026-11-08 | كبير ونشط (853 KB، 22 commits، 3 skills: iphone-duo / foldsim / hig-design-review، CI) | **نقدر نقتبس كود**، لكن نتجنب كتل Apple VERBATIM |
| [bahimzabir/iphone-duo-adaptive-ui](https://github.com/bahimzabir/iphone-duo-adaptive-ui) | MIT (نص السكيل) + ملاحظة إن اقتباسات Apple ملك Apple | 1 | 2026-10-26 | متوسط (مراجع فقط، بدون سكريبتات؛ مبني على مصادر Apple بس مع قوائم "غير موثّق") | **نقدر نقتبس** الكلام الأصلي للمؤلف؛ اقتباسات Apple نرجع فيها للمصدر |
| [NanWuIT/adapt-ui-for-iphone-duo](https://github.com/NanWuIT/adapt-ui-for-iphone-duo) | MIT + NOTICE | 0 | 2026-09-13 | صغير (موجّه لـ Codex، سكريبت audit بـ rg، evals وfixtures، 4 READMEs) — متوقف من سبتمبر | **نقدر نقتبس كود** |
| [Urbanrenewalroridula3044/iPhone-Duo-Agent-Skill](https://github.com/Urbanrenewalroridula3044/iPhone-Duo-Agent-Skill) | MIT (منسوخة، حقوق Aleksei Kakoulin محتفظ بيها) | 0 | 2026-10-12 | **نسخة قديمة (v1.2.2) من alexey1312** — انظر §1.1 | **تجنّب** — استخدم الأصل |
| [alexey1312/iPhone-Duo-Agent-Skill](https://github.com/alexey1312/iPhone-Duo-Agent-Skill) (الأصل) | MIT | 7 | 2026-10-30 | كبير (163 ملف، v1.6.0، 24 commits، 5 skills، duo_scan.py بـ JSON، duo_pose.py، benchmarks، probes ضد SDK) | **نقدر نقتبس كود** |
| [Kimeur/duology](https://github.com/Kimeur/duology) | MIT | 40 | 2026-11-08 | كبير جدًا (37 MB، 5 plugins، 36 skill + 8 recipes، evals بـ fixtures Xcode، duo-lint، pose-matrix) | **نقدر نقتبس كود** |
| [CharlesWiltgen/Axiom](https://github.com/CharlesWiltgen/Axiom) — `axiom-audit-resize` + `iphone-duo.md` | MIT | 1255 | 2026-11-08 | ضخم ومتعدد المساهمين (7)؛ Duo جزء من منظومة xOS أكبر | **نقدر نقتبس كود** (أفكار الـ auditor prompt) |
| [belweave/iphone-duo-design](https://github.com/belweave/iphone-duo-design) (مصدر plugin الـ claudepluginhub) | MIT | 7 | 2026-10-28 | متوسط (duo-lint بـ 19 قاعدة + tests، templates SwiftUI/UIKit، previewers HTML offline، test-plan، rubric) — حساب المالك جديد (2026-05) | **نقدر نقتبس كود** |
| [islam-diab/duo-adapt](https://github.com/islam-diab/duo-adapt) (Flutter — مرجع فقط) | MIT | 6 | 2026-11-08 | جديد (أنشئ 2026-11-08)؛ 3 agents + طبقة responsive مختبرة | مرجع للفكرة (مش Swift) |
| **إضافات مهمة لقيتها:** | | | | | |
| [mirzaaghazadeh/iphone-duo-skills](https://github.com/mirzaaghazadeh/iphone-duo-skills) | MIT (+ تنويه علامات تجارية) | **306** (الأعلى نجومًا) | 2026-11-06 | 11 skills (منها Flutter/RN/Capacitor/games)، workflow يراقب docs Apple، 3 مساهمين | **نقدر نقتبس كود** |
| [d-date/iphone-duo-skill](https://github.com/d-date/iphone-duo-skill) | MIT | 46 | 2026-10-15 | مضغوط (5 مراجع) من 6 Tech Talks + HIG + Group Labs؛ مؤلف معروف (Daiki Matsudate) | **نقدر نقتبس كود** |
| [funsiyuan/iPhone-Duo-Skill-apple-app-resizability](https://github.com/funsiyuan/iPhone-Duo-Skill-apple-app-resizability) | **لا توجد رخصة** (أرشيف غير رسمي لمحتوى Apple) | 34 | 2026-10-23 | نسخة مستخرجة من Xcode 27.1 لسكيل Apple | **تجنّب** كاعتماد/نسخ؛ مفيد بس لفهم محتوى سكيل Apple |
| [artemnovichkov/hinge](https://github.com/artemnovichkov/hinge) · [skarol/duoctl](https://github.com/skarol/duoctl) | MIT · MIT | 42 · 27 | 2026-11-04 · 2026-10-28 | أدوات CLI للتحكم في مفصلة الـ simulator (تستخدم private events) | أدوات خارجية اختيارية |

### 1.1 الريبو المشبوه: Urbanrenewalroridula3044

اللي اتحقق منه:
- تاريخ الـ commits في الريبو **هو نفسه تاريخ alexey1312/iPhone-Duo-Agent-Skill** لغاية 2026-09-19 (مؤلف الـ commits: Aleksei Kakoulin)، وبعدين الحساب `Urbanrenewalroridula3044` (إيميل gmail) عمل commit مكرر "Release 1.2.2" مرتين يوم 2026-09-27، وبعدها "Update README.md" يوم 2026-10-12.
- الـ README الأصلي اتشال واتحط بداله README عام من نوع "Download ZIP / Visit this link" بيوجّه لـ `urbanrenewalroridula3044.github.io` — ده نمط معروف لريبوهات mirror/SEO. **محتوى صفحة الـ github.io ماتفحصش (غير متحقق منه).**
- الحساب أُنشئ 2026-05-01، له ريبوهان فقط و0 متابعين. الـ LICENSE محتفظ بحقوق Aleksei.
- السكريبتات الـ Python اللي فحصتها (duo_scan.py، sdk_api_check.py): مفيش أي اتصال شبكة أو تنفيذ مشبوه؛ الـ `subprocess` الوحيد بينادي `xcrun` زي الأصل. **مافحصتش كل الـ 110 ملف سطرًا سطرًا (غير متحقق منه بالكامل).**
- **الخلاصة:** مش مشروع مستقل؛ نسخة متجمدة على v1.2.2 بينما الأصل وصل v1.6.0 (2026-10-30). مفيش دليل على malware في اللي اتفحص، لكن **تجنّبه واستخدم الأصل alexey1312**.

---

## 2. مصفوفة التغطية

✓ = مغطّى فعليًا (قرأت SKILL.md/المراجع/السكريبتات) · ◐ = جزئي/ذكر عابر · ✗ = مش موجود

| البند | bones7456 | hechen | MustafaNatur | anatoliykant | bahimzabir | NanWuIT | alexey1312 (=Urban) | duology | Axiom | belweave | mirza | d-date |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Size classes & resizability | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Vertical bars (`toolbarVerticalEdge`/`verticalBarEdge`) | ✗ | ✓ | ✓ | ✓ (أعمق واحد) | ✓ | ✓ | ✓ | ✓ | ◐ (UIKit فقط، 3 checks) | ✓ | ✓ | ✓ |
| Reserved regions | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ◐ | ✓ | ✓ | ✓ |
| `ArrangementView`/`UIArrangementViewController` | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ◐ | ✓ | ✓ | ✓ |
| Hinge (`onHingeChange`/`UIHingeInteraction`) | ✗ | ✓ | ✓ | ✓ | ✓ | ◐ | ✓ | ✓ | ◐ | ✓ | ✓ | ✓ |
| UIScene migration | ✗ | ◐ | ✓ (عبر سكيل Apple) | ✓ | ◐ | ✗ | ✓ | ✓ (duo-migrate) | ✓ (قلب الـ auditor) | ✓ | ◐ | ◐ |
| Outer display / `sceneAccessory` | ◐ (لقطة شاشة) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ◐ | ✓ | ✓ | ✓ |
| Camera (`AVCaptureDeviceDirectionCoordinator`) | ✗ | ✓ (skill مستقل) | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ◐ | ✓ | ✓ |
| Lint أنماط ممنوعة (`UIScreen.main`/idiom/orientation) | ✓ (audit_duo.sh) | ◐ (أوامر rg) | ✓ (audit.py) | ✓ (grep audit) | ◐ (checklist) | ✓ (audit-duo-layout.sh + tests) | ✓ (duo_scan.py → JSON، DUO001–022) | ✓ (duo-lint DUO001–009 + تعطيل بتعليقات) | ✓ (15 check، prompt) | ✓ (duo-lint DUO001–019، قواعد bars/regions) | ◐ | ◐ |
| أتمتة simulator / لقطات قبل-بعد | ✓ (duo_sim.sh: شاشتين، فيديو، hang) | ✗ (مصفوفة اختبار فقط) | ✓ (capture.sh + contact sheet) | ✓ (foldsim: fold/rotate/tap/tour) | ✗ | ✗ | ✓ (duo_pose.py فوق hinge CLI) | ✓ (pose-matrix عبر Accessibility API) | ◐ (`xcui resize sweep` لـ Mirroring) | ✗ (previewers HTML فقط) | ✗ | ✗ |
| App Store screenshots للـ Duo | ✓ | ◐ | ✓ (تحقق أبعاد) | ✓ | ✓ | ✗ | ✓ | ✓ (duo-app-store) | ✗ | ✓ | ◐ | ✓ |
| Design review | ◐ | ✓ (skill) | ◐ (أسئلة قرار) | ✓ (hig-design-review، D1–D32، Figma) | ✓ | ◐ | ◐ | ✓ (duo-design-review + rubric) | ✗ | ✓ (rubric + checklist) | ✓ (skill) | ◐ |
| RTL / localization | ✗ | ◐ (سطر + ملاحظة تعارض مصادر) | ◐ (§5 في reserved-regions) | ◐ (D21 + فقرة من lab 288) | ◐ (اقتباسات HIG/TT) | ◐ (صف في test matrix) | ◐ (P11 + سطر layout) | ◐ (39 ملف، أغلبها "unverified"، لعبة واحدة مقيسة) | ◐ (سطر واحد) | ◐ (E6 + تعليق في template) | ◐ (ملاحظة swap leading/trailing) | ✗ |
| يستدعي/يبني على سكيل Apple App Resizability | ✗ | ◐ ("أداة منفصلة تشتغل جنبنا") | **✓ (يصدّره runtime ويعطيه الأولوية)** | ◐ (الخطوة 13 من 13) | ✓ (الخطوة 1: شغّله أولًا + ملف تحليل له) | ✗ | ◐ (يذكر التصدير) | ◐ ("نشير له ولا ننسخه") | ◐ (ذكر إعادة التسمية) | ✓ ("شغّل الاتنين") | ◐ | ◐ (checklist) |

**ملاحظة على الـ lint:** تلات أدوات بتستخدم نفس نطاق الأرقام `DUO0xx` بمعاني مختلفة (duology: DUO001 = main-screen؛ belweave: DUO002 = fixed-width بينما duology DUO002 = device-orientation؛ alexey1312: DUO001–DUO022). لو هندمج، لازم namespace خاص بينا.

### 2.1 أحسن فكرة في كل ريبو (تستاهل الاقتباس)

| الريبو | الفكرة | نقدر نأخدها كـ |
|---|---|---|
| bones7456 | `duo_sim.sh`: التقاط الشاشتين بتحديد display ID عن طريق probe وتصنيف بالـ pixel size (لأن الـ default screenshot = الشاشة الخارجية)، أمر `hang` يقيس CPU ويعمل sample للـ "wide-layout feedback loop" اللي بيعلّق الـ main thread | **كود** (MIT) |
| hechen | مبدأ "اقرأ القيمة ولا تفترض الحافة" (`toolbarVerticalEdge`/`verticalBarEdge`) + فصل التقرير إلى: مراجعة مصدر / compile / simulator / جهاز — "ما تحوّلش سيناريو ماتنفذش لـ pass" | فكرة + كود |
| MustafaNatur | **Apple Skills Bridge**: تصدير سكيلات Apple بـ `xcrun agent skills export --output-dir "$TMPDIR/..."` وقت التشغيل، ترتيب أولوية (المستخدم → Apple → السكيل)، exit codes للـ fallback، "لا تنسخ ملفات Apple للريبو أبدًا"؛ + ملف قرارات `DUO_DECISIONS.md` + مبدأ "الآيفونات العادية ما تتغيرش" | **فكرة فقط** (مفيش رخصة) — نعيد كتابتها من الصفر |
| anatoliykant | `foldsim` (Swift CLI: fold لأي زاوية، أوضاع closed/tent/book/open/table، لمس الشاشة الداخلية، `tour` بلقطات) + قواعد مراجعة تصميم D1–D32 مع D21 للـ RTL + تصنيف Tier 1/2/3 و"hinge-presence gate" | **كود** (MIT) — مع تحذير إنه بيستخدم private simulator interfaces |
| bahimzabir | "claim ledger": كل معلومة بمصدرها وتاريخ التحقق + قوائم "Apple لم توثّق" (أبعاد، عرض البار، زوايا المفصلة) + أوضح تحليل لتقسيم العمل مع سكيل Apple | فكرة (الاقتباسات من Apple نرجع لمصدرها) |
| NanWuIT | evals للـ trigger + fixtures إيجابية/سلبية + اختبارات للـ audit script (exclusions للـ Pods/DerivedData) | **كود** (MIT) |
| alexey1312 | `duo_scan.py` بيطلع **JSON منظم** (findings + inventory) مع severity ومصدر Apple لكل قاعدة؛ `sdk_api_check.py` بيتحقق من وجود الرموز في SDK فعلًا؛ `duo_pose.py` بيحرك المفصلة بـ sweep قصير (مش قفزة، لأن القفزة بتعطّل تبديل الشاشات) | **كود** (MIT) |
| duology | `duo-lint` بتعليقات تعطيل `// duo-lint:disable-next-line DUO001 -- reason` + دعم plist + اختبارات؛ `duo-pose-matrix` بيضغط أزرار Device Hub عبر macOS Accessibility API (بدون private APIs) مع fallback يدوي؛ انضباط وسم "(unverified)" | **كود** (MIT) |
| Axiom | مخرجات الـ auditor: "Windowing Model Map" + **Resize Readiness Score** (RESIZE-READY / PARTIAL / FIXED-CANVAS) + compound findings + تقسيم العمل بين auditors | فكرة/prompt (MIT) |
| belweave | قواعد lint خاصة بالـ Duo مش بس الـ resizability: `custom-bar`، `symmetric-insets`، `reserved-regions-ignored`، `text-only-toolbar-item`، `destructive-outside-overflow`، `cropped-hero`، `size-read-at-launch` + previewers HTML offline | **كود** (MIT) |
| mirzaaghazadeh | workflow `watch-apple-docs.yml` يراقب تغيّر صفحات Apple؛ ملاحظة "توقّع إن `.leading`/`.trailing` يتبدلوا مع الـ locale" | فكرة |
| d-date | أوضح جدول "سلوك حسب SDK" + ملخص Group Labs | فكرة |
| islam-diab (Flutter) | الكود الوحيد اللي بيتعامل مع RTL فعليًا حوالين "عمود البار الفيزيائي": `Directionality.of(context) == TextDirection.rtl` → عرض القائمة بيتحسب من الناحية التانية، و"العمود ما بيتعكسش" + اختبار RTL | فكرة نترجمها لـ SwiftUI/UIKit |

---

## 3. سكيل Apple "App Resizability"

### 3.1 إيه اللي بيغطيه (من ملف SKILL.md المستخرج ومن تحليل bahimzabir/belweave/MustafaNatur المتطابق)
- الاسم الفني: `app-resizability` (بيشحن مع Xcode 27.1؛ إعادة تسمية لسكيل `uikit-app-modernization` من WWDC26 session 278 — حسب Tech Talk 111461 المُشار له في belweave وAxiom).
- **Task Registry (5 مهام):** `UIScreen.main` → بدائل سياقية؛ orientation → size classes/bounds؛ app lifecycle → scene lifecycle؛ safe area (أعلى/أسفل guides، insets غير متماثلة، **`.left` فيزيائي ولا يعني leading**؛ `additionalSafeAreaInsets.left` بيقع على الـ trailing في RTL)؛ `userInterfaceIdiom` → size classes.
- **Prerequisites للقراءة فقط:** launch screen (ITMS-90870 / TN3208)، اتجاهات iPad، `UIRequiresFullScreen` (TN3192) — بدون تعديل مفاتيح.
- Swift + Objective-C، UIKit أساسًا، مع قسم SwiftUI لكل مهمة (حسب bahimzabir — **غير متحقق منه مباشرة** لأني ماقرأتش كل ملفات المهام).
- Apple نفسها في [صفحة prepare](https://developer.apple.com/iphone-duo/prepare/): "The skill finds most issues, but not all of them" وبتطلب مراجعة قائمة Step 2 يدويًا: التوقف عن `UIScreen.main.bounds`، عدم استخدام orientation للـ layout، عدم افتراض idiom/size class = جهاز، فحص media الـ `.scaleAspectFill`. وStep 3 اختبار (resizable simulator، iPhone Mirroring، Duo simulator). وتنويه: قبل الشحن بـ SDK 27.1 "make sure your app's content adapts to the bars becoming vertical".

### 3.2 إيه اللي **مش** بيغطيه (إجماع الأدوات + صفحة Apple)
- تصميم عناصر الـ vertical bar وواجهاتها (`axisBehavior`، `visibilityPriority`، compression، opt-out للـ sheets).
- `ArrangementView`/`UIArrangementViewController`، reserved regions، hinge، scene accessories، camera direction.
- قواعد HIG للتصميم، الألعاب، أصول App Store (المقاسات/الـ badge/الترشيح).
- أي أرقام للجهاز (Apple لم تنشر نقاط pt).
- **أتمتة الـ simulator، لقطات قبل/بعد، أي تقرير موحّد، وأي شيء عن RTL غير قاعدة `.left` ≠ leading.**

### 3.3 حكم إعادة التوزيع
- الملفات المصدَّرة **لا تحمل أي ملف رخصة أو إشعار حقوق** (bahimzabir فحصها 2026-10-26 من Xcode 27.1 27A9275؛ النسخة المؤرشفة عند funsiyuan كمان بلا أي إشعار؛ ومؤلفها كتب "No independent license grant is implied").
- [Xcode and Apple SDKs Agreement](https://www.apple.com/legal/sla/docs/xcode.pdf): تعريف "Xcode Developer Tools" يشمل "software tools, compilers, sample code, Documentation ... and overall design package"؛ **البند 2.7**: "unless otherwise expressly permitted by Apple in writing, You agree not to rent, lease, lend, upload to or host on any website or server, sell, redistribute, or sublicense the Apple Software and Apple Services, in whole or in part"؛ **البند 2.5**: النسخ مسموح للحزمة كاملة فقط وبإشعارات Apple. الاتفاقية ما بتسمّيش "agent skills" صراحةً **(غير متحقق منه إن Apple تعتبرها Apple Software، لكن التعريفات واسعة بما يكفي)**.
- **الخلاصة: لا نُضمّن (bundle) سكيل Apple ولا نرفعه على GitHub.** نخلّي الـ orchestrator يشغّل `xcrun agent skills export --output-dir <absolute path داخل $TMPDIR>` على جهاز كل مستخدم (بموافقته)، يقرأها من هناك في الجلسة، ولا ينسخها لريبو المشروع (نفس نهج MustafaNatur وbahimzabir وduology). لو Xcode أقدم من 27.1 أو الأمر غير مدعوم → fallback لقائمة Step 2 من صفحة Apple كـ checklist نكتبها بكلامنا.
- ملاحظة: مقالات التصدير على Xcode 27.0 بتذكر 7 سكيلات بدون `app-resizability` ([Reda Lemeden](https://redalemeden.com/derived-data/2026/using-xcode-27-skills-with-any-harness)، [dev.to](https://dev.to/arshtechpro/wwdc-2026-xcode-27-ships-with-apples-own-agent-skills-what-they-are-and-how-to-use-them-3g2))؛ bahimzabir بيقول 27.1 بتصدّر عشرة منها `app-resizability`. يعني الـ orchestrator لازم **يطابق بالوصف** (كلمة "resiz"/"iPhone Duo" في frontmatter) مش بالاسم فقط.

---

## 4. فحص فجوة RTL/العربي — النتيجة: **فجوة مفتوحة كـ workflow، مش كمعلومة**

### 4.1 اللي Apple وثّقته (تم التحقق من الـ JSON الرسمي للصفحات)
- **HIG "Designing for iPhone Duo" › Vertical controls:** "Because controls on the vertical axis stay aligned with the hardware, they hold the same position relative to the camera on the outer display, and stay on the same side in right-to-left languages." وفي Split View كل تطبيق يضع عناصره على حافته الخارجية.
- **[`toolbarVerticalEdge`](https://developer.apple.com/documentation/swiftui/environmentvalues/toolbarverticaledge):** `HorizontalEdge?`، "the system determines the edge based on **locale** and device"؛ بيرجع `nil` حيث لا يوجد بار رأسي. (يعني القيمة `.leading`/`.trailing` **تتبدل مع الـ locale** بينما البار فيزيائيًا ثابت — hechen رصد التوتر الظاهري بين الصياغتين، وmirzaaghazadeh بيقول "توقّع التبديل".)
- **[`reservedRegions(kind:options:layoutDirectionBehavior:)`](https://developer.apple.com/documentation/swiftui/geometryproxy/reservedregions(kind:options:layoutdirectionbehavior:)):** الافتراضي `.mirrors` — SwiftUI بتعكس إطارات المناطق في RTL؛ `.fixed` للإطارات الفيزيائية.
- **سكيل Apple نفسه (safe-area-task):** `safeAreaInsets.left` فيزيائي دائمًا؛ استخدم `safeAreaLayoutGuide.leadingAnchor`؛ `additionalSafeAreaInsets.left` يقع trailing في RTL.
- **صفحة prepare وصفحة "Preparing your app for iPhone Duo":** لا تذكر RTL إطلاقًا.

### 4.2 اللي المجتمع عمله
- 13 من 16 ريبو **بتذكر** RTL، لكن في شكل: صف واحد في مصفوفة اختبار (alexey1312 P11، belweave E6، NanWuIT، hechen) أو اقتباس HIG (bahimzabir، anatoliykant D21) أو ملاحظة عن `.mirrors`. أعمق شرح عند anatoliykant (من Group Lab 288: في RTL عمود القائمة في split view بيروح **يمين بين البار والتفاصيل**).
- duology عنده أكتر ذكر (39 ملف) لكن أغلب نقاط RTL معلّمة **"(unverified)"** عنده نفسه؛ القياس الفعلي الوحيد: recipe لعبة لاعبين بتشغيل `-AppleTextDirection YES -NSForceRightToLeftWritingDirection YES`، وملاحظة عند duo-postures إن UIKit `reservedRegions` **بلا mirroring** (غير مختبر عندهم).
- **ولا أداة واحدة** عندها: قاعدة lint خاصة بالـ RTL، أو خطوة في الأتمتة تشغّل التطبيق بالعربي على كل pose وتقارن مع LTR، أو فحص لتبديل اللغة داخل التطبيق، أو screenshots عربية للـ App Store.
- الكود الوحيد الواعي بالـ RTL حوالين البار هو Flutter (islam-diab).

### 4.3 دليل من الواقع
- Apple Developer Forums thread [852870](https://developer.apple.com/forums/thread/852870): "RTL Layout Issue on iPhone Duo Simulator (iOS 27.1) When Switching App Language to Arabic" — UIKit + Auto Layout، فراغ كبير غير متوقع على الشمال عند التبديل للعربي داخل التطبيق (النظام إنجليزي) مع `semanticContentAttribute` عبر `UIAppearance` على كل الـ classes. **رد واحد من المجتمع (مش Apple) بدون حل مؤكد.** ده بالظبط نمط الكود اللي هيتضرر من insets غير متماثلة + بار رأسي، ومحدش من الأدوات بيكشفه.

### 4.4 الأسئلة المفتوحة اللي محدش تحقق منها (تستاهل قياس على الـ simulator ثم على جهاز)
1. قيمة `toolbarVerticalEdge`/`verticalBarEdge` في العربي على الشاشة الخارجية والداخلية-landscape: هل فعلًا تتبدل `.leading↔.trailing`؟
2. هل UIKit `UIView.reservedRegions(kind:options:)` بيرجع إطارات معكوسة في RTL زي SwiftUI ولا فيزيائية؟
3. ترتيب أعمدة `NavigationSplitView`/`UISplitViewController` بالنسبة للبار في RTL (كلام lab 288 — غير متحقق منه بالقياس).
4. التبديل اللغوي داخل التطبيق (`semanticContentAttribute` عبر appearance) مع الـ safe area غير المتماثل (الـ forum thread).
5. `ArrangementView` overlay: "primary في trailing" — إيه اللي يحصل في RTL؟
6. لقطات App Store عربية للـ Duo (المقاسات نفسها، لكن اتجاه الـ bar في الموكاب).

---

## 5. الفجوات اللي محدش بيغطيها (مرتبة بالقيمة)

1. **مرحلة RTL/عربي كاملة** (lint + تشغيل بالعربي على كل pose + مقارنة LTR/RTL + قائمة الأسئلة أعلاه + نمط تبديل اللغة داخل التطبيق). الطلب عليها حقيقي (forum) ولا أحد يقدّمها.
2. **تقرير واحد قبل/بعد** يدمج: نتائج سكيل Apple + نتائج lint الخاصة بالـ Duo + لقطات الشاشتين لكل pose (قبل/بعد، LTR/RTL) + "ما لم يُتحقق منه" + Readiness Score. (MustafaNatur عنده أقرب شيء لكن بلا رخصة وبدون دمج مخرجات Apple؛ Axiom عنده Score بدون لقطات.)
3. **تشغيل سكيل Apple كـ step منظم** مع التقاط مخرجاته في schema موحّد وحساب "الدلتا" (إيه اللي Apple لقته vs إيه اللي إحنا لقيناه). الكل بيقول "شغّل الاتنين"؛ واحد بس (بلا رخصة) بينفّذها.
4. **Linter موحّد بـ namespace واحد** بدل 3 أنظمة `DUO0xx` متضاربة، يجمع: أنماط Step 2 من Apple + قواعد البار/المناطق (belweave) + قواعد resizability (duology/alexey) + قواعد RTL الجديدة، مع تعليقات تعطيل بسبب.
5. **تجريد قيادة الـ poses مع fallback متدرّج:** foldsim (private APIs) → hinge/duoctl CLI → Device Hub عبر Accessibility API → طلب يدوي من المستخدم؛ وتثبيت display IDs بالـ pixel size. (3 مقاربات متنافسة اليوم، كلها هشة أمام تحديثات Xcode.)
6. **بوابة انحدار "الآيفونات العادية ما تتغيرش"**: لقطات iPhone 17 قبل/بعد وdiff، لأن أشهر خطأ هو فك قفل الاتجاه على مستوى التطبيق (مبدأ MustafaNatur رقم 5 — نعيد كتابته).
7. **Localization عامة في البار الرأسي:** نصوص طويلة (ألماني/عربي) في overflow، Dynamic Type AX5 في البار الرأسي (duology بس عنده accessibility مفصّل).

---

## 6. مقترح معمارية الـ orchestrator skill

**اسم مبدئي:** `duo-ready` (skill واحد + `scripts/` + `references/`). كل قاعدة lint بـ namespace خاص `DR-xxx` (و`DR-RTL-xxx` للعربي). مفيش اعتماد runtime على أي ريبو خارجي: نسخ السكريبتات المرخّصة MIT داخل `scripts/vendor/` مع `THIRD_PARTY_NOTICES.md`، وأي أداة اختيارية (hinge/duoctl/foldsim) نتعامل معها كـ "لو موجودة".

| المرحلة | إيه اللي بتعمله | مستوحاة من | إيه اللي نكتبه إحنا |
|---|---|---|---|
| **0. Preflight** | بوابة toolchain (Xcode 27.1+، runtime iOS 27.1، Duo simulator موجود/يتعمل)، كشف UIKit/SwiftUI/mixed، حالة git، **تصدير سكيلات Apple لـ `$TMPDIR` بموافقة المستخدم** ومطابقتها بالوصف | MustafaNatur bridge (فكرة)، anatoliykant toolchain gate، hechen baseline، alexey1312 `sdk_api_check.py` (MIT) | `preflight.sh` + `export_apple_skills.sh` (كتابتنا)، exit codes للـ fallback |
| **1. Baseline capture** | بناء موقّع، التقاط الشاشتين لكل pose (closed/open/book/tabletop/landscape) **× {LTR، RTL}** عبر launch args `-AppleLanguages (ar) -AppleTextDirection YES`، contact sheet | bones7456 `duo_sim.sh` (MIT، نقتبسه)، alexey1312 `duo_pose.py` (MIT)، duology pose-matrix (MIT) كـ fallback | `pose_driver.sh` (التجريد + fallback متدرّج)، `contact_sheet.py` (كتابتنا؛ ما ننسخش نسخة MustafaNatur) |
| **2. Apple pass** | تشغيل سكيل `app-resizability` المصدَّر كما هو على المشروع، تحويل نتائجه لـ `findings.json` (schema موحّد: rule، file:line، severity، source=apple) | Apple (محلي فقط)؛ لو غير متاح → checklist Step 2 بكلامنا | `apple_findings_adapter.md` (تعليمات للـ agent) + schema |
| **3. Duo audit** | lint ثابت: البار (`custom-bar`، `text-only-toolbar-item`، `symmetric-insets`)، reserved regions، arrangements، scenes/windows (طلب نافذة بلا معالج خطأ)، camera؛ جرد containers | belweave duo-lint (MIT، ندمج قواعده)، Axiom checks 13–15 (MIT، كـ prompt)، alexey1312 duo_scan JSON (MIT)، duology تعليقات التعطيل (MIT) | `dr-lint.py` موحّد بـ namespace `DR-` + fixtures إيجابية/سلبية (نمط NanWuIT) |
| **4. RTL/Arabic phase (جديدة)** | lint: `UIEdgeInsets.left/.right` قرب `verticalBarEdge`/`safeAreaInsets`، `semanticContentAttribute` عبر `UIAppearance`، `layoutDirectionBehavior: .fixed` بدون سبب، افتراض `.trailing` ثابت للبار، `.frame(alignment: .trailing)` مربوط بالبار بدل `toolbarVerticalEdge`؛ تشغيل بالعربي على كل pose؛ قائمة فحص (جانب البار، ترتيب أعمدة split view، mirroring المناطق في UIKit vs SwiftUI، تبديل اللغة داخل التطبيق)؛ لقطات App Store عربية | Apple docs (HIG، `toolbarVerticalEdge`، `reservedRegions`)، forum 852870، islam-diab (فكرة العمود الفيزيائي)، anatoliykant D21/lab 288 | **كله كتابتنا**: `DR-RTL-001..0xx`، `rtl_run.sh`، `references/rtl-checklist.md`، وتجربة قياس توثّق الأسئلة المفتوحة §4.4 |
| **5. Fix + decision checkpoint** | إصلاحات ميكانيكية تلقائيًا (Apple أولًا)، إعادة التصميم تسأل المستخدم (خيار موصى به أولًا) وتسجّل في `DUO_DECISIONS.md`؛ Tier 1/2/3؛ **بوابة "الآيفونات العادية بدون تغيير"** (لقطات iPhone 17 قبل/بعد) | MustafaNatur (فكرة: قرارات + مبدأ 5)، anatoliykant tiers + hinge-presence gate | `references/decisions.md` + `regression_gate.sh` (كتابتنا) |
| **6. Verify + design review** | إعادة الالتقاط، diff، مراجعة تصميم بقواعد D-rules/rubric، تحقق أبعاد App Store | anatoliykant hig-design-review (MIT)، belweave rubric (MIT)، duology duo-design-review (MIT) | دمج القوائم في rubric واحدة بلغتنا |
| **7. Unified report** | ملف واحد Markdown (+HTML اختياري): Windowing Model Map، Readiness Score، جدول findings (apple / duo / rtl) مع الدلتا، شبكة لقطات قبل/بعد × pose × اتجاه، قرارات، TODOs، "لم يُتحقق منه"، ما يحتاج جهازًا حقيقيًا، App Store checklist | Axiom (Score/Map — فكرة)، hechen (فصل مستويات التحقق)، bahimzabir/duology (وسم unverified) | `report.py` (كتابتنا) |

**قواعد صارمة في الـ orchestrator:**
- Apple أولًا؛ عند التعارض نتبع Apple ونذكر الفرق في التقرير.
- لا نسمّي أي API غير موجود في SDK (`sdk_api_check` قبل كتابة كود 27.1) ونغلّف كل جديد بـ `#available(iOS 27.1, *)`.
- لا ندّعي pass لسيناريو ما اتنفذش؛ كل pose اتلقطت تُذكر بزاوية المفصلة.
- الملفات المصدَّرة من Apple تعيش في `$TMPDIR` فقط ولا تدخل الريبو أبدًا.

**ترتيب التنفيذ المقترح:** المرحلة 4 (RTL) + المرحلة 7 (التقرير) هما القيمة المضافة الفريدة؛ المراحل 0–3 ممكن تتجمع بسرعة من كود MIT جاهز. أول تجربة قياس: تشغيل تطبيق UIKit بسيط بالعربي على الـ Duo simulator وتوثيق إجابات §4.4 — ده هيبقى المحتوى اللي محدش غيرنا عنده.

---

## 7. المصادر
- Apple: [Get ready / prepare](https://developer.apple.com/iphone-duo/prepare/) · [Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo) · [HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo) · [`toolbarVerticalEdge`](https://developer.apple.com/documentation/swiftui/environmentvalues/toolbarverticaledge) · [`verticalBarEdge`](https://developer.apple.com/documentation/uikit/uitraitcollection/verticalbaredge) · [`reservedRegions(kind:options:layoutDirectionBehavior:)`](https://developer.apple.com/documentation/swiftui/geometryproxy/reservedregions(kind:options:layoutdirectionbehavior:)) · [`ReservedRegion`](https://developer.apple.com/documentation/swiftui/reservedregion) · [Xcode and Apple SDKs Agreement (PDF)](https://www.apple.com/legal/sla/docs/xcode.pdf) · [Forum 852870 (RTL على Duo)](https://developer.apple.com/forums/thread/852870)
- مقالات التصدير: [Reda Lemeden](https://redalemeden.com/derived-data/2026/using-xcode-27-skills-with-any-harness) · [dev.to arshtechpro](https://dev.to/arshtechpro/wwdc-2026-xcode-27-ships-with-apples-own-agent-skills-what-they-are-and-how-to-use-them-3g2)
- الريبوهات: الروابط في جدول §1 · [tessl: axiom-audit-resize](https://tessl.io/registry/skills/github/CharlesWiltgen/Axiom/axiom-audit-resize) · [claudepluginhub: belweave](https://www.claudepluginhub.com/plugins/belweave-iphone-duo-design)
- ريبوهات إضافية ظهرت في البحث ولم تُفحص بعمق: [Erikote04/iPhone-Duo-Agent-Skill](https://github.com/Erikote04/iPhone-Duo-Agent-Skill) (MIT، 0⭐، commitان) · [mahdi-salmanzade/iphone-duo-skill](https://github.com/mahdi-salmanzade/iphone-duo-skill) (MIT، 6⭐، يغطي RN/Flutter/web wrappers) · [artemnovichkov/iPhone-Duo-by-Examples](https://github.com/artemnovichkov/iPhone-Duo-by-Examples) (MIT، 84⭐، أمثلة SwiftUI)
