import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class RegistrationScreen extends StatefulWidget {
  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _surnameController = TextEditingController();
  final TextEditingController _accessKeyController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController = TextEditingController();

  String? errorMessage;

  void _tryRegister() async { 
    final name = _nameController.text.trim();
    final surname = _surnameController.text.trim();
    final accessKey = _accessKeyController.text.trim();
    final password = _passwordController.text.trim();
    final confirmPassword = _confirmPasswordController.text.trim();

    setState(() => errorMessage = null);

    if (name.isEmpty || surname.isEmpty || accessKey.isEmpty || password.isEmpty || confirmPassword.isEmpty) {
      setState(() => errorMessage = "Please fill in all fields");
      return;
    } 

    if (password != confirmPassword) {
      setState(() => errorMessage = "Passwords do not match");
      return;
    }

    try { 
      final response = await http.post(
        Uri.parse("http://127.0.0.1:5000/register"), 
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "name": name,
          "surname": surname,
          "access_key": accessKey,
          "password": password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data["success"] == true) { 
          Navigator.pushReplacementNamed(context, "/login");
        } else {
          setState(() => errorMessage = data["message"]);
        }
      } else {
        setState(() => errorMessage = "Server error, please try again later");
      }
    } catch (e) {
      setState(() => errorMessage = "Server is unavailable, please try again later");
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _surnameController.dispose();
    _accessKeyController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 171, 194, 242),
      appBar: AppBar(
        title: const Text(
          "Registration",
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Color.fromARGB(255, 4, 23, 116),
            fontFamily: "AristotelicaPro",
          ),
        ),
        backgroundColor: const Color.fromARGB(255, 171, 194, 242),
        elevation: 0,
        iconTheme: const IconThemeData(color: Color.fromARGB(255, 4, 23, 116)),
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 400),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextField(
                  controller: _nameController,
                  style: const TextStyle(fontFamily: "AristotelicaPro"),
                  decoration: InputDecoration(
                    labelText: "Name", 
                    hintText: "Enter your name",
                    filled: true,                
                    fillColor: Colors.white,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _surnameController,
                  style: const TextStyle(fontFamily: "AristotelicaPro"),
                  decoration: InputDecoration(
                    labelText: "Surname", 
                    hintText: "Enter your surname",
                    filled: true,                
                    fillColor: Colors.white,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _accessKeyController,
                  obscureText: true,
                  style: const TextStyle(fontFamily: "AristotelicaPro"),
                  decoration: InputDecoration(
                    labelText: "Access key", 
                    hintText: "Enter your access key",
                    filled: true,                
                    fillColor: Colors.white,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  style: const TextStyle(fontFamily: "AristotelicaPro"),
                  decoration: InputDecoration(
                    labelText: "Password", 
                    hintText: "Enter your password",
                    filled: true,                
                    fillColor: Colors.white,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _confirmPasswordController,
                  obscureText: true,
                  style: const TextStyle(fontFamily: "AristotelicaPro"),
                  decoration: InputDecoration(
                    labelText: "Confirm Password", 
                    hintText: "Confirm your password",
                    filled: true,                
                    fillColor: Colors.white,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                ),
                const SizedBox(height: 16),
                if (errorMessage != null)
                  Text(
                    errorMessage!, 
                    style: const TextStyle(color: Colors.red, fontFamily: "AristotelicaPro"),
                    textAlign: TextAlign.center,
                  ),
                const SizedBox(height: 24),
                SizedBox(
                  height: 48,
                  child: ElevatedButton(
                    onPressed: _tryRegister,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color.fromARGB(255, 190, 210, 245),
                      foregroundColor: const Color.fromARGB(255, 4, 23, 116),
                      side: const BorderSide(color: Colors.white),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    ),
                    child: const Text(
                      "Create an Account",
                      style: TextStyle(fontWeight: FontWeight.bold, fontFamily: "AristotelicaPro"),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
