import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import '../theme/theme_provider.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  final _emailController = TextEditingController();
  final _fullNameController = TextEditingController();
  bool _isPasswordVisible = false;
  bool _isLoginMode = true;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    _emailController.dispose();
    _fullNameController.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    final authService = context.read<AuthService>();
    bool success;

    if (_isLoginMode) {
      success = await authService.login(
        _usernameController.text.trim(),
        _passwordController.text.trim(),
      );
    } else {
      success = await authService.register(
        username: _usernameController.text.trim(),
        email: _emailController.text.trim(),
        password: _passwordController.text.trim(),
        fullName: _fullNameController.text.trim().isNotEmpty
            ? _fullNameController.text.trim()
            : null,
        role: "clinician",
      );
    }

    if (mounted) {
      if (success) {
        Navigator.of(context).pushReplacementNamed('/home');
      } else {
        final message = authService.error ?? 'Authentication failed';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(message)),
        );
      }
    }
  }

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
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 28),
              child: Consumer<AuthService>(
                builder: (context, authService, child) {
                  return Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          _isLoginMode ? "Log In" : "Registration",
                          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                                fontFamily: 'Montserrat',
                                color: const Color(0xFF325498),
                              ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 40),
                        _field(
                          controller: _usernameController,
                          label: "Name*",
                          validator: (v) => v == null || v.trim().isEmpty ? "Required field" : null,
                        ),
                        const SizedBox(height: 16),
                        if (!_isLoginMode) ...[
                          _field(
                            controller: _fullNameController,
                            label: "Surname*",
                            validator: (v) => v == null || v.trim().isEmpty ? "Required field" : null,
                          ),
                          const SizedBox(height: 16),
                          _field(
                            controller: _emailController,
                            label: "Email*",
                            validator: (v) {
                              if (v == null || v.trim().isEmpty) {
                                return "Required field";
                              }
                              if (!v.contains('@')) {
                                return "Enter a valid email";
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 16),
                        ],
                        TextFormField(
                          controller: _passwordController,
                          obscureText: !_isPasswordVisible,
                          style: const TextStyle(
                            fontFamily: 'Montserrat',
                            color: Color(0xFF325498),
                          ),
                          decoration: InputDecoration(
                            filled: true,
                            fillColor: Colors.white,
                            labelText: "Password*",
                            labelStyle: const TextStyle(
                              fontFamily: 'Montserrat',
                              color: Color(0xFF325498),
                            ),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                              borderSide: const BorderSide(color: Color(0xFFA3B8E0)),
                            ),
                            suffixIcon: IconButton(
                              icon: Icon(
                                _isPasswordVisible ? Icons.visibility : Icons.visibility_off,
                                color: const Color(0xFF325498),
                              ),
                              onPressed: () => setState(() => _isPasswordVisible = !_isPasswordVisible),
                            ),
                          ),
                          validator: (v) => v == null || v.isEmpty ? "Required field" : null,
                        ),
                        if (!_isLoginMode) ...[
                          const SizedBox(height: 16),
                          TextFormField(
                            obscureText: true,
                            style: const TextStyle(
                              fontFamily: 'Montserrat',
                              color: Color(0xFF325498),
                            ),
                            decoration: InputDecoration(
                              filled: true,
                              fillColor: Colors.white,
                              labelText: "Repeat password*",
                              labelStyle: const TextStyle(
                                fontFamily: 'Montserrat',
                                color: Color(0xFF325498),
                              ),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(8),
                                borderSide: const BorderSide(color: Color(0xFFA3B8E0)),
                              ),
                            ),
                            validator: (v) {
                              if (!_isLoginMode && v != _passwordController.text) {
                                return "Passwords do not match";
                              }
                              return null;
                            },
                          ),
                        ],
                        const SizedBox(height: 24),
                        if (authService.error != null) ...[
                          Text(
                            authService.error!,
                            style: const TextStyle(color: Colors.red, fontFamily: 'Montserrat'),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 12),
                        ],
                        ElevatedButton(
                          onPressed: authService.isLoading ? null : _handleSubmit,
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            minimumSize: const Size(double.infinity, 55),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                            backgroundColor: const Color(0xFF325498),
                          ),
                          child: authService.isLoading
                              ? const CircularProgressIndicator(color: Colors.white)
                              : const Text(
                                  "Sign in",
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontFamily: 'Montserrat',
                                    color: Colors.white,
                                  ),
                                ),
                        ),
                        const SizedBox(height: 16),
                        TextButton(
                          onPressed: () {
                            setState(() {
                              _isLoginMode = !_isLoginMode;
                              authService.clearError();
                            });
                          },
                          child: Text(
                            _isLoginMode ? "Create an account" : "Back to login",
                            style: const TextStyle(
                              fontFamily: 'Montserrat',
                              color: Color(0xFF325498),
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _field({
    required TextEditingController controller,
    required String label,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      validator: validator,
      style: const TextStyle(
        fontFamily: 'Montserrat',
        color: Color(0xFF325498),
      ),
      decoration: InputDecoration(
        filled: true,
        fillColor: Colors.white,
        labelText: label,
        labelStyle: const TextStyle(
          fontFamily: 'Montserrat',
          color: Color(0xFF325498),
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Color(0xFFA3B8E0)),
        ),
      ),
    );
  }
}
