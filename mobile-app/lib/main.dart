import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';
import 'services/eeg_service.dart';
import 'services/processing_service.dart';
import 'services/backend_service.dart';

void main() {
  runApp(const EEGMonitorApp());
}

class EEGMonitorApp extends StatelessWidget {
  const EEGMonitorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => EEGService()),
        ChangeNotifierProvider(create: (_) => ProcessingService()),
        ChangeNotifierProvider(create: (_) => BackendService()),
      ],
      child: MaterialApp(
        title: 'EEG Monitor',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
          useMaterial3: true,
        ),
        home: const HomeScreen(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
