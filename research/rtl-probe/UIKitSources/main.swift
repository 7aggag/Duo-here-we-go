import UIKit

func probeLog(_ tag: String, _ value: String) {
    let line = "PROBE|\(tag)|\(value)\n"
    FileHandle.standardError.write(Data(line.utf8))
    let url = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("probe.log")
    if let h = try? FileHandle(forWritingTo: url) {
        h.seekToEndOfFile()
        h.write(Data(line.utf8))
        try? h.close()
    } else {
        try? Data(line.utf8).write(to: url)
    }
}

func r(_ rect: CGRect) -> String { "x=\(Int(rect.minX)) y=\(Int(rect.minY)) w=\(Int(rect.width)) h=\(Int(rect.height))" }

final class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        let force = UserDefaults.standard.bool(forKey: "ForceRTLAppearance")
        if force {
            UIView.appearance().semanticContentAttribute = .forceRightToLeft
        }
        probeLog("launch", "pureUIKit lang=\(Locale.preferredLanguages.first ?? "?") bundleLoc=\(Bundle.main.preferredLocalizations.first ?? "?") forceRTL=\(force)")
        return true
    }

    func application(_ application: UIApplication, configurationForConnecting session: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        let config = UISceneConfiguration(name: nil, sessionRole: session.role)
        config.delegateClass = SceneDelegate.self
        return config
    }
}

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let ws = scene as? UIWindowScene else { return }
        let split = UISplitViewController(style: .doubleColumn)
        split.preferredDisplayMode = .oneBesideSecondary
        split.setViewController(UINavigationController(rootViewController: ListVC()), for: .primary)
        split.setViewController(UINavigationController(rootViewController: InfoVC()), for: .secondary)
        let w = UIWindow(windowScene: ws)
        if UserDefaults.standard.bool(forKey: "ForceRTLTraits") {
            w.traitOverrides.layoutDirection = .rightToLeft
        }
        probeLog("traitsAffectingBarEdge", UITraitCollection.systemTraitsAffectingVerticalBarEdge.map { "\($0)" }.joined(separator: ","))
        w.rootViewController = split
        w.makeKeyAndVisible()
        window = w
    }
}

final class ListVC: UITableViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Sidebar"
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "c")
    }
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int { 4 }
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let c = tableView.dequeueReusableCell(withIdentifier: "c", for: indexPath)
        c.textLabel?.text = "Item \(indexPath.row + 1)"
        return c
    }
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        probeLog("uikit.primary", "frame=\(r(view.convert(view.bounds, to: nil))) dir=\(view.effectiveUserInterfaceLayoutDirection == .rightToLeft ? "rtl" : "ltr")")
    }
}

final class InfoVC: UIViewController {
    private let leadingLabel = UILabel()
    private let trailingLabel = UILabel()
    private let physicalLeftLabel = UILabel()
    private var physicalLeft: NSLayoutConstraint!
    private let info = UILabel()

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Detail"
        view.backgroundColor = .systemBackground
        navigationItem.rightBarButtonItems = [
            UIBarButtonItem(systemItem: .action),
            UIBarButtonItem(systemItem: .edit),
        ]
        leadingLabel.text = "LEADING"; leadingLabel.backgroundColor = .systemGreen
        trailingLabel.text = "TRAILING"; trailingLabel.backgroundColor = .systemOrange
        physicalLeftLabel.text = "LEFT+inset"; physicalLeftLabel.backgroundColor = .systemPink
        info.numberOfLines = 0
        info.font = .monospacedSystemFont(ofSize: 11, weight: .regular)
        for v in [leadingLabel, trailingLabel, physicalLeftLabel, info] {
            v.translatesAutoresizingMaskIntoConstraints = false
            view.addSubview(v)
        }
        let g = view.safeAreaLayoutGuide
        physicalLeft = physicalLeftLabel.leftAnchor.constraint(equalTo: view.leftAnchor)
        NSLayoutConstraint.activate([
            leadingLabel.leadingAnchor.constraint(equalTo: g.leadingAnchor),
            leadingLabel.topAnchor.constraint(equalTo: g.topAnchor, constant: 8),
            trailingLabel.trailingAnchor.constraint(equalTo: g.trailingAnchor),
            trailingLabel.topAnchor.constraint(equalTo: g.topAnchor, constant: 8),
            physicalLeft,
            physicalLeftLabel.topAnchor.constraint(equalTo: leadingLabel.bottomAnchor, constant: 8),
            info.leadingAnchor.constraint(equalTo: g.leadingAnchor, constant: 8),
            info.trailingAnchor.constraint(equalTo: g.trailingAnchor, constant: -8),
            info.topAnchor.constraint(equalTo: physicalLeftLabel.bottomAnchor, constant: 8),
        ])
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        let s = view.safeAreaInsets
        if physicalLeft.constant != s.left { physicalLeft.constant = s.left }
        let edge: String = switch traitCollection.verticalBarEdge {
        case .leading: "leading"
        case .trailing: "trailing"
        default: "unspecified"
        }
        let division = view.reservedRegions(kind: .division, options: .includeInactive).map { "\(r($0.frame)) active=\($0.isActive)" }.joined(separator: "; ")
        let text = [
            "dir=\(view.effectiveUserInterfaceLayoutDirection == .rightToLeft ? "rtl" : "ltr") semantic=\(view.semanticContentAttribute.rawValue) barEdge=\(edge)",
            "frameInWindow=\(r(view.convert(view.bounds, to: nil))) safe(l=\(Int(s.left)) r=\(Int(s.right)))",
            "leading=\(r(leadingLabel.frame)) trailing=\(r(trailingLabel.frame)) leftPlusInset=\(r(physicalLeftLabel.frame))",
            "division=[\(division)]",
        ]
        info.text = text.joined(separator: "\n")
        probeLog("uikit.secondary", text.joined(separator: " | "))
    }
}

UIApplicationMain(CommandLine.argc, CommandLine.unsafeArgv, nil, NSStringFromClass(AppDelegate.self))
