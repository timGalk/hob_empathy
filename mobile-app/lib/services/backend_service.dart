import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/eeg_data.dart';
import '../utils/config.dart';
import 'auth_service.dart';

/// Service for communicating with backend API
class BackendService extends ChangeNotifier {
  final String _baseUrl = Config.backendUrl;
  final String _wsUrl = Config.wsUrl;
  final AuthService _authService;

  WebSocketChannel? _channel;
  PatientState? _latestState;
  bool _isConnected = false;

  PatientState? get latestState => _latestState;
  bool get isConnected => _isConnected;

  BackendService(this._authService);

  /// Send features to backend
  Future<bool> sendFeatures(FeaturePayload payload) async {
    try {
      final headers = {
        'Content-Type': 'application/json',
        ..._authService.getAuthHeaders(),
      };

      final response = await http.post(
        Uri.parse('$_baseUrl/api/v1/ingest'),
        headers: headers,
        body: jsonEncode(payload.toJson()),
      );

      if (response.statusCode == 201) {
        debugPrint('Features sent successfully');
        return true;
      } else if (response.statusCode == 401) {
        debugPrint('Unauthorized: Token may be expired');
        return false;
      } else {
        debugPrint('Failed to send features: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      debugPrint('Error sending features: $e');
      return false;
    }
  }

  /// Get patient state
  Future<PatientState?> getPatientState(String patientId) async {
    try {
      final headers = _authService.getAuthHeaders();

      final response = await http.get(
        Uri.parse('$_baseUrl/api/v1/patient/$patientId/state'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _latestState = PatientState.fromJson(data);
        notifyListeners();
        return _latestState;
      } else if (response.statusCode == 401) {
        debugPrint('Unauthorized: Token may be expired');
      }
    } catch (e) {
      debugPrint('Error getting patient state: $e');
    }
    return null;
  }

  /// Connect to WebSocket for real-time updates
  void connectWebSocket() {
    try {
      // Add token as query parameter for WebSocket authentication
      final token = _authService.accessToken;
      if (token == null) {
        debugPrint('Cannot connect WebSocket: Not authenticated');
        return;
      }

      _channel = WebSocketChannel.connect(
        Uri.parse('$_wsUrl/api/v1/stream?token=$token'),
      );

      _isConnected = true;
      notifyListeners();

      _channel!.stream.listen(
        (message) {
          final data = jsonDecode(message);

          if (data['type'] == 'prediction') {
            _latestState = PatientState.fromJson(data['prediction']);
            notifyListeners();
          }
        },
        onError: (error) {
          debugPrint('WebSocket error: $error');
          _isConnected = false;
          notifyListeners();
        },
        onDone: () {
          debugPrint('WebSocket closed');
          _isConnected = false;
          notifyListeners();
        },
      );
    } catch (e) {
      debugPrint('Error connecting to WebSocket: $e');
      _isConnected = false;
      notifyListeners();
    }
  }

  /// Disconnect WebSocket
  void disconnectWebSocket() {
    _channel?.sink.close();
    _channel = null;
    _isConnected = false;
    notifyListeners();
  }

  @override
  void dispose() {
    disconnectWebSocket();
    super.dispose();
  }
}
