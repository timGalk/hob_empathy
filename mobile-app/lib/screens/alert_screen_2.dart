import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

Future<void> makePhoneCall(String phoneNumber) async {
  final Uri launchUri = Uri(
    scheme: 'tel',
    path: phoneNumber,
  );

  if (!await launchUrl(
    launchUri,
    mode: LaunchMode.platformDefault,
  )) {
    throw 'Could not launch $phoneNumber';
  }
}

class AlertScreen2 extends StatelessWidget {
  const AlertScreen2 ({Key? key}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
        title: const Text(
          "Allert Screen",
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Color.fromARGB(255, 113, 8, 8),
            fontFamily: 'AristotelicaPro',
          ),
        ),
        backgroundColor: const Color.fromARGB(255, 242, 171, 171),
        elevation: 0,
        iconTheme: const IconThemeData(color: Color.fromARGB(255, 250, 53, 53))
      ),
      backgroundColor: const Color.fromARGB(255, 250, 53, 53),
      body: Container (
         decoration: BoxDecoration(gradient: LinearGradient(
        colors: [Color.fromARGB(255, 250, 53, 53), const Color.fromARGB(115, 239, 217, 217)],
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
         ),
         ),
          child: Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column (
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Container(
                      padding: EdgeInsets.all(16),
                      height: 240,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: const Color.fromARGB(255, 250, 250, 248),
                          borderRadius: BorderRadius.circular(20), // скругление углов
                          border: Border.all(
                          color: Color.fromARGB(255, 85, 15, 15),  // цвет обводки
                          width: 10,             // толщина обводки
                          ),
                        boxShadow: [
                          BoxShadow(
                            color: const Color.fromARGB(255, 85, 15, 15),
                            blurRadius: 10,
                            offset: Offset(0, 4),
                          ),
                        ]
                      ),
                      child: const Center(
                       child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          Text(
                            'Is everything alright?',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: Color.fromARGB(255, 85, 15, 15),
                            ),
                          ),
                          SizedBox(height: 16),
                          Text(
                            'This is the second alert screen мы тут чет напишем хз.',
                            style: TextStyle(
                              fontSize: 16,
                              color: Color.fromARGB(255, 85, 15, 15),
                            ),
                          ),
                        ],
                       ),
                      ),
                    ),

                  const SizedBox(height: 28),

                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton(
                    onPressed: () async {  // <- async здесь!
                    await makePhoneCall('911');
                    Navigator.pushReplacementNamed(context, '/home');
                    },
                      child: const Text('CALL AN AMBULANCE'),
                    ),
                  ),

                  const SizedBox(height: 28),

                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.pop(context);
                      },
                      child: const Text('Exit'),
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
