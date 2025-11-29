import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class LoginScreen extends StatefulWidget {
  @override
  State<LoginScreen> createState() => _LoginScreenState(); 
}

class _LoginScreenState extends State<LoginScreen> { 
  final TextEditingController _loginController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController(); 

  String? errorMessage; 

  void _tryLogin() async {
    final login = _loginController.text.trim();
    final password = _passwordController.text.trim();

    if (login.isEmpty || password.isEmpty) {
      setState(() {
        errorMessage = "Enter your login and password";
      });
      return;
    }

    try {
      final response = await http.post(
        Uri.parse('http://10.0.2.2:5000/login'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"login": login, "password": password}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          setState(() => errorMessage = null);

          SharedPreferences prefs = await SharedPreferences.getInstance();
          await prefs.setBool('isLoggedIn', true);
          await prefs.setString('userLogin', login); 

          Navigator.pushReplacementNamed(
            context,
            '/home',
            arguments: {'token': login},
          );
        } else {
          setState(() {
            errorMessage = "Incorrect login or password, please try again.";
          });
        }
      } else {
        setState(() {
          errorMessage = "Server error, please try again later.";
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = "Server is unavailable, please try again later.";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Login",
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Color.fromARGB(255, 4, 23, 116),
            fontFamily: 'AristotelicaPro',
          ),
        ),
        backgroundColor: const Color.fromARGB(255, 171, 194, 242),
        elevation: 0,
        iconTheme: const IconThemeData(color: Color.fromARGB(255, 4, 23, 116)),
      ),
      backgroundColor: const Color.fromARGB(255, 171, 194, 242),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              TextField(
                controller: _loginController,
                style: const TextStyle(fontFamily: 'AristotelicaPro'),
                decoration: InputDecoration(
                  filled: true,
                  fillColor: Colors.white,
                  labelText: "Enter your login",
                  hintText: "Enter your name and surname",
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _passwordController,
                obscureText: true,
                style: const TextStyle(fontFamily: 'AristotelicaPro'),
                decoration: InputDecoration(
                  filled: true,
                  fillColor: Colors.white,
                  labelText: "Password",
                  hintText: "Enter your password",
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                ),
              ),
              const SizedBox(height: 16),
              if (errorMessage != null)
                Text(
                  errorMessage!,
                  style: const TextStyle(
                    color: Colors.red,
                    fontFamily: 'AristotelicaPro',
                  ),
                  textAlign: TextAlign.center,
                ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: ElevatedButton(
                  onPressed: _tryLogin,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color.fromARGB(255, 190, 210, 245),
                    foregroundColor: const Color.fromARGB(255, 4, 23, 116),
                    side: const BorderSide(color: Colors.white),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: const Text(
                    "Sign In",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontFamily: 'AristotelicaPro',
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

  @override
  void dispose() {
    _loginController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
}
