import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "duo-here-we-go" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from dhwg_lint import lint  # noqa: E402

UIKIT_APPEARANCE = """
    import UIKit
    final class AppDelegate: UIResponder, UIApplicationDelegate {
        func application(_ a: UIApplication, didFinishLaunchingWithOptions o: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
            UIView.appearance().semanticContentAttribute = .forceRightToLeft
            return true
        }
    }
"""


def project(files: dict) -> Path:
    root = Path(tempfile.mkdtemp())
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(body))
    return root


def ids(result) -> list:
    return sorted(f["id"] for f in result["findings"])


class RTL001(unittest.TestCase):
    def test_appearance_without_trait_fix_is_error(self):
        r = lint(project({"App/AppDelegate.swift": UIKIT_APPEARANCE}))
        self.assertEqual(ids(r), ["DHWG-RTL-001"])
        self.assertEqual(r["findings"][0]["severity"], "error")
        self.assertEqual(r["findings"][0]["line"], 5)

    def test_trait_override_anywhere_clears_it(self):
        r = lint(project({
            "App/AppDelegate.swift": UIKIT_APPEARANCE,
            "App/Scene.swift": """
                import UIKit
                func configure(_ w: UIWindow) { w.traitOverrides.layoutDirection = .rightToLeft }
            """,
        }))
        self.assertEqual(ids(r), [])

    def test_ternary_assignment_is_caught(self):
        r = lint(project({"A.swift": """
            import UIKit
            func apply(rtl: Bool) {
                UIView.appearance(whenContainedInInstancesOf: [UINavigationBar.self]).semanticContentAttribute = rtl ? .forceRightToLeft : .forceLeftToRight
            }
        """}))
        self.assertEqual(ids(r), ["DHWG-RTL-001"])


class RTL005(unittest.TestCase):
    def test_swiftui_lifecycle_gets_005_too(self):
        r = lint(project({"App.swift": """
            import SwiftUI
            @main
            struct MyApp: App {
                init() { UIView.appearance().semanticContentAttribute = .forceRightToLeft }
                var body: some Scene { WindowGroup { Text("hi") } }
            }
        """}))
        self.assertEqual(ids(r), ["DHWG-RTL-001", "DHWG-RTL-005"])


class RTL002(unittest.TestCase):
    UIKIT = """
        import UIKit
        final class V: UIView {
            func hinge() -> CGRect? { reservedRegions(kind: .division).first?.frame }
        }
    """

    def test_mixed_default_mirrors_is_flagged(self):
        r = lint(project({"V.swift": self.UIKIT, "S.swift": """
            import SwiftUI
            struct S: View {
                var body: some View {
                    GeometryReader { proxy in
                        let r = proxy.reservedRegions(kind: .division)
                        Text("\\(r.count)")
                    }
                }
            }
        """}))
        self.assertEqual(ids(r), ["DHWG-RTL-002"])

    def test_fixed_behavior_is_fine(self):
        r = lint(project({"V.swift": self.UIKIT, "S.swift": """
            import SwiftUI
            func f(_ proxy: GeometryProxy) { _ = proxy.reservedRegions(kind: .division, layoutDirectionBehavior: .fixed) }
        """}))
        self.assertEqual(ids(r), [])

    def test_uikit_call_in_file_that_also_imports_swiftui(self):
        r = lint(project({"Mixed.swift": """
            import SwiftUI
            import UIKit
            final class VC: UIViewController {
                override func viewDidLayoutSubviews() { _ = view.reservedRegions(kind: .division) }
            }
            struct S: View {
                var body: some View {
                    GeometryReader { geo in Text("\\(geo.reservedRegions(kind: .division, layoutDirectionBehavior: .fixed).count)") }
                }
            }
        """}))
        self.assertEqual(ids(r), [])

    def test_swiftui_only_is_fine(self):
        r = lint(project({"S.swift": """
            import SwiftUI
            func f(_ proxy: GeometryProxy) { _ = proxy.reservedRegions(kind: .division) }
        """}))
        self.assertEqual(ids(r), [])


class RTL003(unittest.TestCase):
    def test_edge_mapped_to_physical_side(self):
        r = lint(project({"V.swift": """
            import UIKit
            func place(_ v: UIView, in c: UIView) {
                if c.traitCollection.verticalBarEdge == .trailing {
                    v.center.x = c.bounds.maxX - 100
                }
            }
        """}))
        self.assertEqual(ids(r), ["DHWG-RTL-003"])

    def test_physical_access_before_the_edge_read_is_not_linked(self):
        r = lint(project({"V.swift": """
            import UIKit
            func log(_ v: UIView) {
                let left = v.safeAreaInsets.left
                let edge = v.traitCollection.verticalBarEdge
                print(left, edge)
            }
        """}))
        self.assertEqual(ids(r), [])

    def test_directional_use_is_fine(self):
        r = lint(project({"V.swift": """
            import SwiftUI
            struct V: View {
                @Environment(\\.toolbarVerticalEdge) var edge
                var body: some View { Text("x").padding(edge == .leading ? .leading : .trailing, 8) }
            }
        """}))
        self.assertEqual(ids(r), [])


class RTL004(unittest.TestCase):
    def test_fixed_column_width(self):
        r = lint(project({"S.swift": """
            import SwiftUI
            struct S: View {
                var body: some View {
                    NavigationSplitView { List { }.navigationSplitViewColumnWidth(320) } detail: { Text("d") }
                }
            }
        """}))
        self.assertEqual(ids(r), ["DHWG-001", "DHWG-RTL-004"])
        self.assertEqual(next(f for f in r["findings"] if f["id"] == "DHWG-RTL-004")["severity"], "info")

    def test_flexible_column_width_is_fine(self):
        r = lint(project({"S.swift": """
            import SwiftUI
            let x = List { }.navigationSplitViewColumnWidth(min: 280, ideal: 320, max: 480)
        """}))
        self.assertEqual(ids(r), [])

    def test_uikit_preferred_width(self):
        r = lint(project({"S.swift": """
            import UIKit
            func f(_ s: UISplitViewController) { s.preferredPrimaryColumnWidth = 320 }
        """}))
        self.assertEqual(ids(r), ["DHWG-RTL-004"])


class DHWG001(unittest.TestCase):
    def test_cap_at_or_below_hinge_center_is_flagged(self):
        for cap in ("420", "475"):
            r = lint(project({"S.swift": f"""
                import SwiftUI
                let s = List {{ }}.navigationSplitViewColumnWidth(min: 280, ideal: 320, max: {cap})
            """}))
            self.assertEqual(ids(r), ["DHWG-001"], cap)
            self.assertEqual(r["findings"][0]["source"], "dhwg")
            self.assertEqual(r["findings"][0]["severity"], "warn")

    def test_cap_above_hinge_center_or_none_is_fine(self):
        r = lint(project({"S.swift": """
            import SwiftUI
            let a = List { }.navigationSplitViewColumnWidth(min: 280, ideal: 320, max: 476)
            let b = List { }.navigationSplitViewColumnWidth(min: 280, ideal: 320)
        """}))
        self.assertEqual(ids(r), [])


class Suppression(unittest.TestCase):
    def test_next_line_and_same_line(self):
        r = lint(project({"A.swift": """
            import UIKit
            func a() {
                // dhwg:disable-next-line DHWG-RTL-001 -- window traits set in a framework we do not scan
                UIView.appearance().semanticContentAttribute = .forceRightToLeft
            }
            func b(_ s: UISplitViewController) { s.preferredPrimaryColumnWidth = 320 } // dhwg:disable DHWG-RTL-004 -- design spec
        """}))
        self.assertEqual(ids(r), [])
        self.assertEqual(len(r["suppressed"]), 2)

    def test_reason_is_required(self):
        r = lint(project({"A.swift": """
            import UIKit
            // dhwg:disable-next-line DHWG-RTL-001
            func a() { UIView.appearance().semanticContentAttribute = .forceRightToLeft }
        """}))
        self.assertEqual(ids(r), ["DHWG-RTL-001"])

    def test_commented_out_code_is_ignored(self):
        r = lint(project({"A.swift": """
            import UIKit
            // UIView.appearance().semanticContentAttribute = .forceRightToLeft
        """}))
        self.assertEqual(ids(r), [])


class Scope(unittest.TestCase):
    def test_vendor_dirs_are_skipped(self):
        r = lint(project({"Pods/X/X.swift": UIKIT_APPEARANCE, "build/Y.swift": UIKIT_APPEARANCE}))
        self.assertEqual(r["files_scanned"], 0)

    def test_exit_codes(self):
        root = project({"A.swift": UIKIT_APPEARANCE})
        script = str(SCRIPTS / "dhwg_lint.py")
        run = lambda *a: subprocess.run([sys.executable, script, str(root), *a], capture_output=True).returncode
        self.assertEqual(run(), 1)
        self.assertEqual(run("--fail-on", "never"), 0)
        clean = project({"A.swift": "import UIKit\n"})
        self.assertEqual(subprocess.run([sys.executable, script, str(clean)], capture_output=True).returncode, 0)


class FaceIDCopy(unittest.TestCase):
    SWIFT = """
        import UIKit
        let title = "Unlock with Face ID"
        // "Face ID" in a comment is fine
    """

    def test_hard_coded_face_id_copy_warns(self):
        r = lint(project({"App/Login.swift": self.SWIFT}))
        self.assertEqual(ids(r), ["DHWG-002"])
        self.assertEqual(r["findings"][0]["severity"], "warn")
        self.assertEqual(r["findings"][0]["line"], 3)

    def test_copy_chosen_from_biometry_type_is_info(self):
        body = self.SWIFT + "\nlet kind = LAContext().biometryType\n"
        r = lint(project({"App/Login.swift": body}))
        self.assertEqual([f["severity"] for f in r["findings"]], ["info"])

    def test_arabic_strings_file_is_checked_but_info_plist_strings_are_not(self):
        r = lint(project({
            "App/ar.lproj/Localizable.strings": '"unlock" = "افتح ببصمة الوجه";\n',
            "App/ar.lproj/InfoPlist.strings": '"NSFaceIDUsageDescription" = "نستخدم Face ID";\n',
            "App/en.lproj/Main.strings": '"NSFaceIDUsageDescription" = "We use Face ID";\n',
        }))
        self.assertEqual([(f["id"], f["file"]) for f in r["findings"]],
                         [("DHWG-002", "App/ar.lproj/Localizable.strings")])

    def test_suppressed_with_reason(self):
        body = 'let t = "Face ID" // dhwg:disable DHWG-002 -- only shown on .faceID\n'
        r = lint(project({"App/Login.swift": body}))
        self.assertEqual(ids(r), [])
        self.assertEqual(len(r["suppressed"]), 1)


if __name__ == "__main__":
    unittest.main()
