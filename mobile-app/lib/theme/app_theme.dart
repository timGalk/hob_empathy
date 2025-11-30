import 'package:flutter/material.dart';

class AppTheme {
  static final ThemeData lightTheme = ThemeData(
    brightness: Brightness.light,
    useMaterial3: true,
    fontFamily: 'Montserrat',
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
    scaffoldBackgroundColor: const Color(0xFF90A7DA),
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF325498),
      foregroundColor: Colors.white,
    ),
  );

  static final ThemeData darkTheme = ThemeData(
    brightness: Brightness.dark,
    useMaterial3: true,
    fontFamily: 'Montserrat',
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.blueGrey, brightness: Brightness.dark),
    scaffoldBackgroundColor: const Color.fromARGB(255, 30, 30, 66),
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF325498),
      foregroundColor: Colors.white,
    ),
  );
}
