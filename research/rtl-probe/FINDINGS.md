# نتايج تجربة RTL على iPhone Duo

**التاريخ:** 2026-11-09
**البيئة:** Xcode 27.1 (27A9275)، محاكي iPhone Duo على iOS 27.1 (24A94425)، والتطبيق متبني بـ SDK 27.1.
**المفصلة:** اتحركت بأداة [artemnovichkov/hinge](https://github.com/artemnovichkov/hinge) v0.3.1 (رخصتها MIT). بتبعت نفس حدث HID اللي DeviceHub بيبعته.
**الحدود:** دي نتايج **محاكي بس**، ماتجربتش على جهاز حقيقي. ووضع اللاندسكيب للشاشة الخارجية ووضع الترابيزة (tabletop) ماتجربوش.

الأرقام كلها بالنقاط (pt). الشاشة الجوانية مفتوحة 951×669، والشريط الرأسي بياخد 84 نقطة على **اليمين الفعلي** للجهاز. منطقة المفصلة عند `x=455` وعرضها 40.

## الإجابات

| # | السؤال | النتيجة | الدليل |
|---|---|---|---|
| 1 | هل `toolbarVerticalEdge` / `verticalBarEdge` بيتقلبوا في العربي؟ | **أيوه.** الإنجليزي `trailing` والعربي `leading`، في الوضع المقفول والمفتوح ونص الطيّة. الشريط نفسه **ثابت على يمين الجهاز** في اللغتين. | `results/*/split-{en,ar}` + اللقطات |
| 2 | هل `reservedRegions` في UIKit بيتعكس في RTL؟ | **لأ.** UIKit بيرجع إحداثيات فعلية (`x=455` في اللغتين)، ومفيهوش أصلاً parameter للاتجاه. SwiftUI الافتراضي `.mirrors` (`x=371` في العربي)، و`.fixed` بيرجع نفس رقم UIKit. | `results/half/uikit-*`، `arrangement-*` |
| 3 | ترتيب أعمدة split view جنب الشريط في RTL | الترتيب من اليمين: **الشريط ← الـ sidebar ← التفاصيل**. ولما المفصلة بتبقى نص طيّة، الأعمدة بتتظبط عليها لوحدها: في العربي الـ sidebar بياخد النص اليمين الأضيق (371، لأن الشريط واكل منه)، وفي الإنجليزي بياخد النص الشمال (455). نفس السلوك في `NavigationSplitView` و `UISplitViewController`. | `results/half/split-*`، `pureuikit-*` |
| 4 | تغيير اللغة من جوه التطبيق بـ `UIView.appearance().semanticContentAttribute` | **فيه bug حقيقي.** الـ views بتتعكس، لكن `verticalBarEdge` بيفضل `trailing` لأنه بيتحسب من traits النظام. والنتيجة **مسافة فاضية 88pt على الشمال** (`safe l=88`)، وده نفس بلاغ [المنتدى 852870](https://developer.apple.com/forums/thread/852870). **الحل اللي اتجرب ونجح:** `window.traitOverrides.layoutDirection = .rightToLeft`، وبعده الأرقام بقت مطابقة للعربي الحقيقي (`barEdge=leading`، `safe l=0`). وفي SwiftUI الطريقة دي مالهاش أي تأثير خالص، والتطبيق بيفضل LTR. | `results/half/pureuikit-en-forceRTL{,-traits}` |
| 5 | `ArrangementView` + `overlayArrangementEdge(.trailing)` في RTL | الـ edge **بيتبع اتجاه اللغة**: في الإنجليزي الـ primary على اليمين (371)، وفي العربي على الشمال (455). وفي الوضع المفتوح على الآخر (180°) مفيش تقسيم، والاتنين بياخدوا الشاشة كلها. | `results/{open,half}/arrangement-*` |
| 6 | لقطات App Store بالعربي | الشريط في اللقطات العربي بيبان على **اليمين** زي الإنجليزي بالظبط، والمحتوى بس هو اللي بيتعكس. فالموكابات العربي **ماينفعش** تتعمل بقلب اللقطة الإنجليزي. لازم تتصوّر بالعربي فعلاً. | اللقطات في `results/` |

`systemTraitsAffectingVerticalBarEdge` بيرجع: `_UITraitVerticalBarAllowed`، `_UITraitSystemVerticalBarAllowed`، `_UITraitSystemVerticalBarHorizontalEdge`، `_UITraitVerticalBarSuppressed`، `UITraitLayoutDirection`. وده بيشرح ليه الـ override على `layoutDirection` بيصلّح المشكلة.

## قواعد lint مقترحة لمرحلة RTL في `duo-ready`

| القاعدة | النمط | ليه |
|---|---|---|
| `DR-RTL-001` | `UIView.appearance().semanticContentAttribute = .forceRightToLeft` من غير `traitOverrides.layoutDirection` على الـ window | بيعمل مسافة فاضية 88pt والشريط بيتحسب على الناحية الغلط (سؤال 4) |
| `DR-RTL-002` | خلط frames من `UIView.reservedRegions` (إحداثيات فعلية) مع `GeometryProxy.reservedRegions` بالإعداد الافتراضي `.mirrors` | في العربي الفرق 84 نقطة أو أكتر (سؤال 2) |
| `DR-RTL-003` | افتراض إن الشريط دايماً `.trailing`، أو ربطه بـ `.left`/`.right` بدل ما نقرا `toolbarVerticalEdge`/`verticalBarEdge` | القيمة بتتقلب مع اللغة (سؤال 1) |
| `DR-RTL-004` | عرض ثابت أو افتراض عرض معين لعمود الـ sidebar أو للـ primary في `ArrangementView` | النص اللي جنب الشريط أضيق بـ 84pt، والعمود بيغيّر النص اللي هو فيه حسب اللغة (أسئلة 3 و 5) |
| `DR-RTL-005` | تغيير لغة من جوه التطبيق بالـ appearance proxy في كود SwiftUI | مالوش تأثير في SwiftUI. (الحل البديل في SwiftUI ماتجربش) |

## الحاجات اللي لسه ماتجربتش

- جهاز iPhone Duo حقيقي.
- اللاندسكيب للشاشة الخارجية، والشاشة الجوانية لما تتلف.
- وضع الترابيزة (tabletop).
- حل SwiftUI لتغيير اللغة من جوه التطبيق (`.environment(\.layoutDirection, .rightToLeft)`).
- `UIArrangementViewController` (جربنا `ArrangementView` في SwiftUI بس).

## إعادة التجربة

```bash
./build.sh && ./build-uikit.sh
xcrun simctl install <udid> build/DuoRTLProbe.app
xcrun simctl install <udid> build/DuoRTLProbeUIKit.app
hinge -d <udid> half
./run.sh <udid> half split ar
BID=dev.probe.DuoRTLProbeUIKit ./run.sh <udid> half pureuikit en-forceRTL
```
