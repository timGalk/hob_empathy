import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../theme/theme_provider.dart';

class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final themeProvider = context.watch<ThemeProvider>();
    final bool isDark = themeProvider.isDark;

    // Increased contrast: slightly darker start, lighter end
    final Color bgGradientStart = const Color.fromARGB(255, 110, 140, 200);
    final Color bgGradientEnd = const Color.fromARGB(255, 180, 210, 255);
    // Dark mode adjusted for clearer separation
    final Color darkBgGradientStart = const Color.fromARGB(255, 40, 55, 95);
    final Color darkBgGradientEnd = const Color.fromARGB(255, 18, 30, 60);

    return Scaffold(
      backgroundColor: isDark ? darkBgGradientStart : bgGradientStart,
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: isDark ? [darkBgGradientStart, darkBgGradientEnd] : [bgGradientStart, bgGradientEnd],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.only(top: 24.0),
                child: Image.asset(
                  isDark ? 'assets/images/LogoBlackTheme.png' : 'assets/icons/LogoWhiteTheme.png',
                  width: 120,
                  height: 120,
                ),
              ),
              Expanded(
                child: Center(
                  child: Container(
                    margin: const EdgeInsets.symmetric(horizontal: 24),
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: isDark ? const Color(0xFF1F1F2E) : Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.08),
                          blurRadius: 12,
                          offset: const Offset(0, 6),
                        ),
                      ],
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'Welcome to EmpathyApp..',
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                                fontFamily: 'Montserrat',
                                color: isDark ? Colors.white : const Color(0xFF325498),
                              ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Monitoring and support for patients',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                fontFamily: 'Montserrat',
                                color: isDark ? Colors.grey[300] : Colors.grey[700],
                              ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              Padding(
                // Reduce top spacing so the button sits higher on screen
                // and account for device bottom inset to avoid overlap
                padding: EdgeInsets.fromLTRB(24, 8, 24, 24 + MediaQuery.of(context).padding.bottom),
                child: SizedBox(
                  width: double.infinity,
                  height: 64,
                  child: ElevatedButton(
                    onPressed: () => Navigator.of(context).pushNamed('/login'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: isDark ? const Color(0xFF325498) : const Color.fromARGB(255, 25, 60, 130),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(
                      'Log in',
                      style: TextStyle(
                        fontFamily: 'Montserrat',
                        fontSize: 18,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}


