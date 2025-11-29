import 'dart:async';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key); // убираем token из конструктора

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String caregiverName = "";
  int healthState = 0;
  Timer? timer;
  FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();
  String? token;

  @override
  void initState() {
    super.initState();
    _initNotifications();
    _loadUser();
    // не запускаем healthCheck здесь, тк token пока null
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Получаем token из аргументов после построения контекста
    final args = ModalRoute.of(context)!.settings.arguments as Map?;
    token = args != null ? args['token'] : null;

    if (token != null) {
      _startHealthCheck();
    }
  }

  Future<void> _initNotifications() async {
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const InitializationSettings initializationSettings =
        InitializationSettings(android: initializationSettingsAndroid);

    await flutterLocalNotificationsPlugin.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: (details) {
        Navigator.pushNamed(context, '/alert1'); // Первый алерт экран
      },
    );
  }

  Future<void> _loadUser() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      caregiverName = prefs.getString('caregiverName') ?? 'Опекаемый';
    });
  }

  void _startHealthCheck() {
    timer = Timer.periodic(Duration(seconds: 5), (_) async {
      if (token == null) return;

      try {
        final response = await http.get(Uri.parse(
            'http://localhost:8000/health?token=$token')); // адаптировать под твой сервер
        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          int newHealth = data['health'] ?? 0;

          setState(() => healthState = newHealth);

          if (newHealth >= 98) {
            _showCriticalNotification();
          }
        }
      } catch (e) {
        print("Ошибка обновления здоровья: $e");
      }
    });
  }

  Future<void> _showCriticalNotification() async {
    const AndroidNotificationDetails androidDetails =
        AndroidNotificationDetails(
      'critical_health_channel',
      'Critical Health Alerts',
      importance: Importance.max,
      priority: Priority.high,
      playSound: true,
      // sound: RawResourceAndroidNotificationSound('alert'), // если есть свой mp3
    );

    const NotificationDetails platformDetails =
        NotificationDetails(android: androidDetails);

    await flutterLocalNotificationsPlugin.show(
      0,
      'Критическое состояние!',
      'Состояние здоровья $caregiverName = $healthState',
      platformDetails,
    );
  }

  void _makeCall() async {
    final Uri launchUri = Uri(scheme: 'tel', path: '123456789');
    if (await canLaunchUrl(launchUri)) {
      await launchUrl(launchUri);
    }
  }

  void _exit() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    Navigator.pushReplacementNamed(context, '/login');
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color.fromARGB(255, 171, 194, 242),
      appBar: AppBar(title: Text(caregiverName)),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Container(
              padding: EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  Text(
                    'Состояние здоровья',
                    style: TextStyle(fontSize: 20),
                  ),
                  SizedBox(height: 12),
                  Text(
                    '$healthState',
                    style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: _makeCall,
              child: Text("Make a Call"),
            ),
            SizedBox(height: 12),
            ElevatedButton(
              onPressed: _exit,
              child: Text("Exit"),
            ),
          ],
        ),
      ),
    );
  }
}
