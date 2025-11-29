import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

Future<void> makePhoneCall(String phoneNumber) async { /*Асинхронная функция. Ее крутость в том, 
что она не блокирует пока не выполнится другие процессы. Future<void> - значит, что функция обещает однажды выполниться и 
ничего не возвращает, но мы можем ждать ее выполнения с помощью await. */
  final Uri launchUri = Uri( //Юри - это не про аниме-тяночек, а импортированный мной выше класс, содержащий адрес ссылки
  //Тут я создаю объект типа Юри, который будет содержать путь для перехода к телефонному звонку
    scheme: 'tel', //один из имеющихся схем Юри, который указывает, что мы хотим открыть звонилку
    path: phoneNumber, //путь - это собственно номер телефона, который мы передаем в функцию при вызове
  );

  if (!await launchUrl( //launchUrl - функция из пакета url_launcher, которая открывает указанный ссыль, эвэйт чтобы не полетело пока мы не убедились что звонок прошел
    launchUri, //передаем наш юри объект
    mode: LaunchMode.platformDefault, //запускаем на указанной нами платформе, в частности тут дроид звонилОчка
  )) {
    throw 'Could not launch $phoneNumber'; //если все пошло по жопе выбрасываем ошибку
    //ВАЖНО ДОПИСАТЬ УТРОМ: Если что-то полетело, надо сделать доп экран который попросит набрать вручную потому что иначе юзер будет с приложением возиться столько что бабка уже помрет
  }
}

class AlertScreen1 extends StatelessWidget {
  const AlertScreen1 ({Key? key}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color.fromARGB(255, 233, 111, 111),
      body: Container (
         decoration: BoxDecoration(gradient: LinearGradient(
        colors: [Color.fromARGB(255, 233, 111, 111), const Color.fromARGB(115, 239, 217, 217)],
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
                            'Alert',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: Color.fromARGB(255, 250, 53, 53),
                            ),
                          ),
                          SizedBox(height: 16),
                          Text(
                            'This is the first alert screen мы тут чет напишем хз.',
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
                   onPressed: () async {  // снова ассинхрон, птому что а черт знает пройдет ли звонок
                   await makePhoneCall('123456789'); //отсюда и эвейт
                   Navigator.pushReplacementNamed(context, '/alert2'); 
                  },

                    child: const Text('MAKE A CALL'),
                    ),
                  ),

                  const SizedBox(height: 28),

                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton(
                      onPressed: null,
                      child: const Text('CHECK LOCATION'),
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
