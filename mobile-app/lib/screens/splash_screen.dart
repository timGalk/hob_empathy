import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {

  @override
  void initState() { 
    super.initState(); 
    _checkLoginStatus(); 
  }

  Future<void> _checkLoginStatus() async { 
    final prefs = await SharedPreferences.getInstance(); 
    final isLoggedIn = prefs.getBool('isLoggedIn') ?? false;
    final userLogin = prefs.getString('userLogin') ?? '';

    await Future.delayed(const Duration(seconds: 2)); 

    if (isLoggedIn) {
      Navigator.pushReplacementNamed(
        context,
        '/home',
        arguments: {'token': userLogin},
      );
    } else {
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 171, 194, 242),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            children: [
              Column(
                children: [
                  const SizedBox(height: 40),
                  Container(
                    width: 240,
                    height: 240,
                    decoration: BoxDecoration(
                      color: Colors.transparent,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.grey.shade300, width: 1.2),
                    ),
                    child: const Center(
                      child: Text(
                        'Logo',
                        style: TextStyle(
                          color: Color.fromARGB(255, 4, 23, 116),
                          fontFamily: 'AristotelicaPro',
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 28),
                  Container(
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.blueAccent,
                          blurRadius: 10,
                          offset: Offset(0, 4),
                        ),
                      ],
                    ),
                    padding: const EdgeInsets.all(16),
                    child: const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Welcome to EmpathyApp',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            fontFamily: 'AristotelicaPro',
                          ),
                        ),
                        SizedBox(height: 8),
                        Text(
                          'Краткое описание приложения. Здесь мы расскажем, что делает приложение и почему оно будет полезно пользователю.',
                          style: TextStyle(
                            fontSize: 14,
                            height: 1.4,
                            color: Colors.black87,
                            fontFamily: 'AristotelicaPro',
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const Spacer(),
              Column(
                children: [
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.pushNamed(context, '/login');
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: Colors.black,
                      ),
                      child: const Text(
                        'Log In',
                        style: TextStyle(fontFamily: 'AristotelicaPro'),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.pushNamed(context, '/registration');
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Color.fromARGB(255, 4, 23, 116),
                        foregroundColor: Colors.white,
                      ),
                      child: const Text(
                        'Create an Account',
                        style: TextStyle(fontFamily: 'AristotelicaPro'),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
