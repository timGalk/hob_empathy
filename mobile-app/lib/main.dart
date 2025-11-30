import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'screens/splash_screen.dart';
import 'screens/alert_health_screen.dart';
import 'screens/alert_check_screen.dart';
import 'services/eeg_service.dart';
import 'services/processing_service.dart';
import 'services/backend_service.dart';
import 'services/auth_service.dart';
import 'theme/theme_provider.dart'; // <-- добавляем ThemeProvider
import 'theme/app_theme.dart';

void main() {
  runApp(const EEGMonitorApp());
}

class EEGMonitorApp extends StatelessWidget {
  const EEGMonitorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthService()),
        ChangeNotifierProvider(create: (_) => EEGService()),
        ChangeNotifierProvider(create: (_) => ProcessingService()),
        ChangeNotifierProvider(create: (_) => ThemeProvider()), // <-- добавили
        ChangeNotifierProxyProvider<AuthService, BackendService>(
          create: (context) => BackendService(context.read<AuthService>()),
          update: (context, authService, backendService) =>
              backendService ?? BackendService(authService),
        ),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, theme, child) {
          return MaterialApp(
            title: 'EEG Monitor',
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: theme.isDark ? ThemeMode.dark : ThemeMode.light,
            routes: {
              '/': (context) => const AuthWrapper(),
              '/splash': (context) => const SplashScreen(),
              '/login': (context) => const LoginScreen(),
              '/home': (context) => const HomeScreen(),
              '/alert_health': (context) => AlertHealthScreen(),
              '/alert_check': (context) => AlertCheckScreen(),
            },
            initialRoute: '/splash',
            debugShowCheckedModeBanner: false,
          );
        },
      ),
    );
  }
}

/// Wrapper to handle authentication state and routing
class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializeAuth();
  }

  Future<void> _initializeAuth() async {
    final authService = context.read<AuthService>();
    await authService.init();
    setState(() {
      _isInitialized = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized) {
      return const SplashScreen();
    }

    return Consumer<AuthService>(
      builder: (context, authService, child) {
        if (authService.isLoading) {
          return const SplashScreen();
        }

        if (authService.isAuthenticated) {
          return const HomeScreen();
        }

        return const LoginScreen();
      },
    );
  }
}
