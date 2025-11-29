import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:jwt_decoder/jwt_decoder.dart';
import '../models/auth_models.dart';
import '../utils/config.dart';

/// Authentication service managing user login, registration, and token storage
class AuthService extends ChangeNotifier {
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  User? _currentUser;
  String? _accessToken;
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _error;

  // Getters
  User? get currentUser => _currentUser;
  String? get accessToken => _accessToken;
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Storage keys
  static const String _tokenKey = 'access_token';
  static const String _userKey = 'user_data';

  /// Initialize auth service - load saved token and user data
  Future<void> init() async {
    _isLoading = true;

    try {
      // Try to load saved token
      _accessToken = await _secureStorage.read(key: _tokenKey);

      if (_accessToken != null) {
        // Check if token is expired
        if (JwtDecoder.isExpired(_accessToken!)) {
          // Token expired, clear auth
          await logout();
        } else {
          // Token valid, load user data
          final userData = await _secureStorage.read(key: _userKey);
          if (userData != null) {
            _currentUser = User.fromJson(jsonDecode(userData));
            _isAuthenticated = true;
          }
        }
      }
    } catch (e) {
      debugPrint('Error initializing auth: $e');
      _error = 'Failed to initialize authentication';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Login with username and password
  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final url = Uri.parse('${Config.backendUrl}/api/v1/auth/login');

      // FastAPI OAuth2PasswordRequestForm expects form data
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': username,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final authToken = AuthToken.fromJson(jsonDecode(response.body));

        // Save token and user data
        await _secureStorage.write(key: _tokenKey, value: authToken.accessToken);
        await _secureStorage.write(key: _userKey, value: jsonEncode(authToken.user.toJson()));

        _accessToken = authToken.accessToken;
        _currentUser = authToken.user;
        _isAuthenticated = true;
        _error = null;

        notifyListeners();
        return true;
      } else {
        final errorData = jsonDecode(response.body);
        _error = errorData['detail'] ?? 'Login failed';
        _isAuthenticated = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      debugPrint('Login error: $e');
      _error = 'Network error. Please check your connection.';
      _isAuthenticated = false;
      notifyListeners();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Register a new user
  Future<bool> register({
    required String username,
    required String email,
    required String password,
    String? fullName,
    String? role,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final url = Uri.parse('${Config.backendUrl}/api/v1/auth/register');

      final registerRequest = RegisterRequest(
        username: username,
        email: email,
        password: password,
        fullName: fullName,
        role: role,
      );

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(registerRequest.toJson()),
      );

      if (response.statusCode == 201) {
        final authToken = AuthToken.fromJson(jsonDecode(response.body));

        // Save token and user data
        await _secureStorage.write(key: _tokenKey, value: authToken.accessToken);
        await _secureStorage.write(key: _userKey, value: jsonEncode(authToken.user.toJson()));

        _accessToken = authToken.accessToken;
        _currentUser = authToken.user;
        _isAuthenticated = true;
        _error = null;

        notifyListeners();
        return true;
      } else {
        final errorData = jsonDecode(response.body);
        _error = errorData['detail'] ?? 'Registration failed';
        _isAuthenticated = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      debugPrint('Registration error: $e');
      _error = 'Network error. Please check your connection.';
      _isAuthenticated = false;
      notifyListeners();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Logout and clear stored credentials
  Future<void> logout() async {
    await _secureStorage.delete(key: _tokenKey);
    await _secureStorage.delete(key: _userKey);

    _accessToken = null;
    _currentUser = null;
    _isAuthenticated = false;
    _error = null;

    notifyListeners();
  }

  /// Clear error message
  void clearError() {
    _error = null;
    notifyListeners();
  }

  /// Check if token is still valid
  bool isTokenValid() {
    if (_accessToken == null) return false;
    return !JwtDecoder.isExpired(_accessToken!);
  }

  /// Get authorization header for API requests
  Map<String, String> getAuthHeaders() {
    if (_accessToken == null) return {};
    return {
      'Authorization': 'Bearer $_accessToken',
    };
  }
}
