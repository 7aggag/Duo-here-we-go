import SwiftUI
import UIKit

enum Probe {
    nonisolated(unsafe) static var last: [String: String] = [:]

    static func log(_ tag: String, _ value: String) {
        guard last[tag] != value else { return }
        last[tag] = value
        let line = "PROBE|\(tag)|\(value)\n"
        FileHandle.standardError.write(Data(line.utf8))
        let url = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("probe.log")
        if let h = try? FileHandle(forWritingTo: url) {
            h.seekToEndOfFile()
            h.write(Data(line.utf8))
            try? h.close()
        } else {
            try? Data(line.utf8).write(to: url)
        }
    }

    static func r(_ rect: CGRect) -> String {
        "x=\(Int(rect.minX)) y=\(Int(rect.minY)) w=\(Int(rect.width)) h=\(Int(rect.height))"
    }

    static var mode: String { UserDefaults.standard.string(forKey: "ProbeMode") ?? "split" }
}

@main
struct ProbeApp: App {
    init() {
        if UserDefaults.standard.bool(forKey: "ForceRTLAppearance") {
            UIView.appearance().semanticContentAttribute = .forceRightToLeft
        }
        Probe.log("launch", "mode=\(Probe.mode) lang=\(Locale.preferredLanguages.first ?? "?") bundleLoc=\(Bundle.main.preferredLocalizations.first ?? "?") forceRTL=\(UserDefaults.standard.bool(forKey: "ForceRTLAppearance"))")
    }

    var body: some Scene {
        WindowGroup {
            switch Probe.mode {
            case "arrangement": ArrangementProbe()
            case "uikit": UIKitProbe().ignoresSafeArea()
            default: SplitProbe()
            }
        }
    }
}

struct EnvProbe: View {
    let tag: String
    @Environment(\.toolbarVerticalEdge) private var barEdge
    @Environment(\.layoutDirection) private var direction
    @Environment(\.horizontalSizeClass) private var hClass
    @Environment(\.verticalSizeClass) private var vClass

    var body: some View {
        GeometryReader { proxy in
            let text = describe(proxy)
            ScrollView {
                Text(text).font(.system(size: 11, design: .monospaced)).frame(maxWidth: .infinity, alignment: .leading).padding(8)
            }
            .onAppear { Probe.log(tag, text) }
            .onChange(of: text) { _, new in Probe.log(tag, new) }
        }
        .onHingeChange { _, new in
            let h = new.hinge.map { "status=\($0.status) angle=\(Int($0.angle.degrees))" } ?? "nil"
            Probe.log("\(tag).hinge", h)
        }
    }

    private func describe(_ proxy: GeometryProxy) -> String {
        var lines = [
            "dir=\(direction) barEdge=\(barEdge.map { "\($0)" } ?? "nil") h=\(hClass.map { "\($0)" } ?? "nil") v=\(vClass.map { "\($0)" } ?? "nil")",
            "global=\(Probe.r(proxy.frame(in: .global)))",
        ]
        for (kindName, kind) in [("division", ReservedRegion.Kind.division), ("occlusion", ReservedRegion.Kind.occlusion)] {
            for (behName, beh) in [("mirrors", LayoutDirectionBehavior.mirrors), ("fixed", LayoutDirectionBehavior.fixed)] {
                let regions = proxy.reservedRegions(kind: kind, options: .includeInactive, layoutDirectionBehavior: beh)
                let desc = regions.map { "\(Probe.r($0.frame)) active=\($0.isActive)" }.joined(separator: "; ")
                lines.append("\(kindName).\(behName)=[\(desc)]")
            }
        }
        return lines.joined(separator: " | ")
    }
}

// -SidebarMax N mirrors Daftar's split view: balanced style, all columns, width min 280 / ideal 320 / max N.
struct SplitProbe: View {
    private let sidebarMax = UserDefaults.standard.double(forKey: "SidebarMax")
    @State private var visibility: NavigationSplitViewVisibility = .all

    private var sidebar: some View {
        List(1...4, id: \.self) { Text("Item \($0)") }
            .navigationTitle("Sidebar")
            .onGeometryChange(for: CGRect.self, of: { $0.frame(in: .global) }) { Probe.log("split.sidebarFrame", Probe.r($0)) }
    }

    private var detail: some View {
        EnvProbe(tag: "split.detail")
            .navigationTitle("Detail")
            .toolbar {
                ToolbarItem { Button("Share", systemImage: "square.and.arrow.up") {} }
                ToolbarItem { Button("Edit", systemImage: "pencil") {} }
            }
            .onGeometryChange(for: CGRect.self, of: { $0.frame(in: .global) }) { Probe.log("split.detailFrame", Probe.r($0)) }
    }

    var body: some View {
        if sidebarMax > 0 {
            NavigationSplitView(columnVisibility: $visibility) {
                sidebar.navigationSplitViewColumnWidth(min: 280, ideal: 320, max: sidebarMax)
            } detail: {
                detail
            }
            .navigationSplitViewStyle(.balanced)
        } else {
            NavigationSplitView { sidebar } detail: { detail }
        }
    }
}

struct ArrangementProbe: View {
    var body: some View {
        ArrangementView {
            Color.blue.overlay(Text("PRIMARY").foregroundStyle(.white))
                .onGeometryChange(for: CGRect.self, of: { $0.frame(in: .global) }) { Probe.log("arr.primary", Probe.r($0)) }
        } secondary: {
            Color.orange.overlay(Text("SECONDARY"))
                .onGeometryChange(for: CGRect.self, of: { $0.frame(in: .global) }) { Probe.log("arr.secondary", Probe.r($0)) }
        }
        .arrangementViewStyle(OverlayArrangementViewStyle())
        .overlayArrangementEdge(HorizontalEdge.trailing)
        .overlay(alignment: .bottom) { EnvProbe(tag: "arr.env").frame(height: 160).background(.thinMaterial) }
    }
}

struct UIKitProbe: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> ProbeViewController { ProbeViewController() }
    func updateUIViewController(_ vc: ProbeViewController, context: Context) {}
}

final class ProbeViewController: UIViewController {
    private let leadingLabel = UILabel()
    private let info = UILabel()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        leadingLabel.text = "LEADING"
        leadingLabel.backgroundColor = .systemGreen
        info.numberOfLines = 0
        info.font = .monospacedSystemFont(ofSize: 11, weight: .regular)
        for v in [leadingLabel, info] {
            v.translatesAutoresizingMaskIntoConstraints = false
            view.addSubview(v)
        }
        NSLayoutConstraint.activate([
            leadingLabel.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor),
            leadingLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 8),
            info.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor, constant: 8),
            info.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor, constant: -8),
            info.topAnchor.constraint(equalTo: leadingLabel.bottomAnchor, constant: 8),
        ])
        registerForTraitChanges(UITraitCollection.systemTraitsAffectingVerticalBarEdge) { (vc: ProbeViewController, _) in
            vc.view.setNeedsLayout()
        }
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        let regions = [("division", UIView.ReservedRegion.Kind.division), ("occlusion", UIView.ReservedRegion.Kind.occlusion)].map { name, kind in
            "\(name)=[" + view.reservedRegions(kind: kind, options: .includeInactive)
                .map { "\(Probe.r($0.frame)) active=\($0.isActive)" }.joined(separator: "; ") + "]"
        }
        let edge: String = switch traitCollection.verticalBarEdge {
        case .leading: "leading"
        case .trailing: "trailing"
        default: "unspecified"
        }
        let s = view.safeAreaInsets
        let text = [
            "dir=\(view.effectiveUserInterfaceLayoutDirection == .rightToLeft ? "rtl" : "ltr") semantic=\(view.semanticContentAttribute.rawValue) barEdge=\(edge)",
            "bounds=\(Probe.r(view.bounds)) safe(l=\(Int(s.left)) r=\(Int(s.right)) t=\(Int(s.top)) b=\(Int(s.bottom)))",
            "leadingLabel=\(Probe.r(leadingLabel.frame))",
        ] + regions
        info.text = text.joined(separator: "\n")
        Probe.log("uikit", text.joined(separator: " | "))
    }
}
