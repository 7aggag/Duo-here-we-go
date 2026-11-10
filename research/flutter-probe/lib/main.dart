// Flutter probe for iPhone Duo: shows and logs what Flutter receives in each pose and language.
// Build-time switches: --dart-define=PROBE_DIALOG=true opens an AlertDialog on launch,
// --dart-define=PROBE_SAFE=true wraps the list in a SafeArea,
// --dart-define=PROBE_PUSH=true pushes a detail page with a back button and actions on launch.
// The values go to $HOME/Documents/probe.log (the app's data container) on every layout.
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

const showDialogOnLaunch = bool.fromEnvironment('PROBE_DIALOG');
const safeList = bool.fromEnvironment('PROBE_SAFE');
const pushOnLaunch = bool.fromEnvironment('PROBE_PUSH');

void main() => runApp(const ProbeApp());

class ProbeApp extends StatelessWidget {
  const ProbeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      supportedLocales: const [Locale('en'), Locale('ar')],
      localizationsDelegates: GlobalMaterialLocalizations.delegates,
      home: const ProbePage(),
    );
  }
}

class ProbePage extends StatefulWidget {
  const ProbePage({super.key});

  @override
  State<ProbePage> createState() => _ProbePageState();
}

class _ProbePageState extends State<ProbePage> {
  int tab = 0;

  @override
  void initState() {
    super.initState();
    if (pushOnLaunch) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.of(context).push(MaterialPageRoute<void>(
          builder: (_) => Scaffold(
            appBar: AppBar(
              title: const Text('Detail · تفاصيل'),
              backgroundColor: Colors.lightBlue.shade200,
              actions: [
                IconButton(onPressed: () {}, icon: const Icon(Icons.search)),
                IconButton(onPressed: () {}, icon: const Icon(Icons.more_vert)),
              ],
            ),
            body: const Center(child: Text('detail')),
          ),
        ));
      });
    }
    if (showDialogOnLaunch) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        showDialog<void>(
          context: context,
          builder: (_) => AlertDialog(
            title: const Text('Dialog / حوار'),
            content: const Text('Where does this land half-open?'),
            actions: [TextButton(onPressed: () {}, child: const Text('OK'))],
          ),
        );
      });
    }
  }

  String _insets(EdgeInsets e) =>
      'L${e.left.toStringAsFixed(0)} T${e.top.toStringAsFixed(0)} '
      'R${e.right.toStringAsFixed(0)} B${e.bottom.toStringAsFixed(0)}';

  List<String> _values(BuildContext context) {
    final mq = MediaQuery.of(context);
    final dispatcher = WidgetsBinding.instance.platformDispatcher;
    return [
      'locale=${Localizations.localeOf(context)} dir=${Directionality.of(context).name}',
      'size=${mq.size.width.toStringAsFixed(0)}x${mq.size.height.toStringAsFixed(0)} dpr=${mq.devicePixelRatio}',
      'viewPadding ${_insets(mq.viewPadding)}',
      'padding     ${_insets(mq.padding)}',
      'displayFeatures=${mq.displayFeatures.length} '
          '${mq.displayFeatures.map((f) => '${f.type.name}/${f.state.name}@${f.bounds}').join(', ')}',
      'displays=${dispatcher.displays.map((d) => '${d.id}:${d.size}').join(', ')}',
    ];
  }

  void _log(List<String> values) {
    final home = Platform.environment['HOME'];
    if (home == null) return;
    final file = File('$home/Documents/probe.log');
    file.parent.createSync(recursive: true);
    file.writeAsStringSync('${values.join('\n')}\n');
  }

  @override
  Widget build(BuildContext context) {
    final values = _values(context);
    _log(values);
    final list = ListView.builder(
      itemCount: 30,
      itemBuilder: (_, i) => Container(
        height: 44,
        color: i.isEven ? Colors.teal.shade100 : Colors.teal.shade200,
        padding: const EdgeInsetsDirectional.symmetric(horizontal: 8),
        child: Row(children: [
          Text('start $i'),
          const Spacer(),
          Text('end $i'),
        ]),
      ),
    );
    return Scaffold(
      appBar: AppBar(title: const Text('Duo probe · مسبار'), backgroundColor: Colors.amber),
      body: Stack(children: [
        Positioned.fill(child: safeList ? SafeArea(child: list) : list),
        // Physical edge markers: red on the left, blue on the right, never mirrored.
        const Positioned(left: 0, top: 0, bottom: 0, width: 6, child: ColoredBox(color: Colors.red)),
        const Positioned(right: 0, top: 0, bottom: 0, width: 6, child: ColoredBox(color: Colors.blue)),
        Positioned(
          left: 60,
          top: 120,
          child: Container(
            color: Colors.black87,
            padding: const EdgeInsets.all(8),
            child: Text(values.join('\n'),
                textDirection: TextDirection.ltr,
                style: const TextStyle(color: Colors.white, fontFamily: 'Menlo', fontSize: 12)),
          ),
        ),
      ]),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: tab,
        onTap: (i) => setState(() => tab = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.settings), label: 'Settings'),
        ],
      ),
    );
  }
}
