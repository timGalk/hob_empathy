import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../utils/phone_utils.dart';
import '../theme/theme_provider.dart';

class AlertHealthScreen extends StatelessWidget {
  const AlertHealthScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final themeProvider = context.watch<ThemeProvider>();
    final bool isDark = themeProvider.isDark;

    // Light mode colors
    final Color appBarBg = const Color.fromARGB(255, 242, 171, 171);
    final Color bgGradientStart = const Color.fromARGB(255, 250, 53, 53);
    final Color bgGradientEnd = const Color.fromARGB(115, 239, 217, 217);
    final Color boxBg = const Color.fromARGB(255, 250, 250, 248);
    final Color borderColor = const Color.fromARGB(255, 60, 10, 10);
    final Color textColor = const Color.fromARGB(255, 85, 15, 15);
    final Color accentColor = const Color.fromARGB(255, 85, 15, 15);

    // Dark mode colors (greyish-red tones)
    final Color darkAppBarBg = const Color.fromARGB(255, 100, 50, 50);
    final Color darkBgGradientStart = const Color.fromARGB(255, 110, 50, 50);
    final Color darkBgGradientEnd = const Color.fromARGB(255, 80, 35, 35);
    final Color darkBoxBg = const Color.fromARGB(255, 75, 45, 45);
    final Color darkBorderColor = const Color.fromARGB(255, 140, 70, 70);
    final Color darkTextColor = const Color.fromARGB(255, 220, 180, 180);
    final Color darkAccentColor = const Color.fromARGB(255, 180, 90, 90);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Health Alert',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: isDark ? darkTextColor : textColor,
            fontFamily: 'Montserrat',
            fontSize: 20,
          ),
        ),
        backgroundColor: isDark ? darkAppBarBg : appBarBg,
        elevation: 2,
        centerTitle: true,
      ),
      backgroundColor: isDark ? darkBgGradientStart : bgGradientStart,
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: isDark
                ? [darkBgGradientStart, darkBgGradientEnd]
                : [bgGradientStart, bgGradientEnd],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SafeArea(
          child: Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(20),
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: isDark ? darkBoxBg : boxBg,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: isDark ? darkBorderColor : borderColor,
                        width: 3,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: (isDark ? darkBorderColor : borderColor)
                              .withOpacity(0.3),
                          blurRadius: 12,
                          offset: const Offset(0, 6),
                        ),
                      ],
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Text(
                          'Health Alert',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: isDark ? darkAccentColor : accentColor,
                            fontFamily: 'Montserrat',
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Make sure everything\'s okay',
                          style: TextStyle(
                            fontSize: 16,
                            color: isDark ? darkTextColor : textColor,
                            fontFamily: 'Montserrat',
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 32),

                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: ElevatedButton(
                      onPressed: () async {
                        await makePhoneCall('911');
                        Navigator.pushReplacementNamed(context, '/home');
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: isDark ? darkAccentColor : accentColor,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: Text(
                        'CALL AN AMBULANCE',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          fontFamily: 'Montserrat',
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),

                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: OutlinedButton(
                      onPressed: () {
                        Navigator.pop(context);
                      },
                      style: OutlinedButton.styleFrom(
                        side: BorderSide(
                          color: isDark ? darkBorderColor : borderColor,
                          width: 2,
                        ),
                        backgroundColor: isDark
                            ? darkBoxBg.withOpacity(0.7)
                            : Colors.white.withOpacity(0.7),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: Text(
                        'EVERYTHING\'S FINE',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: isDark ? darkTextColor : textColor,
                          fontFamily: 'Montserrat',
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
