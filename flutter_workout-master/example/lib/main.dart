import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_sensors/flutter_sensors.dart';
import 'package:http/http.dart';

void main() => runApp(const MyApp());

class MyApp extends StatefulWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  String messageTitle = 'Empty';
  String notificationAlert = 'alert';
  FirebaseMessaging _firebaseMessaging = FirebaseMessaging();

  bool _accelAvailable = false;
  List<double> _accelData = List.filled(3, 0.0);
  StreamSubscription? _accelSubscription;
  
  @override
  void initState() {

    _firebaseMessaging.subscribeToTopic('News');
    _firebaseMessaging.configure(
      //onBackgroundMessage: myBackgroundMessageHandler,
      onMessage: (message) async {
        print(message);
        setState(() {
          messageTitle = message['notification']['title'];
          notificationAlert = 'New Notification Alert';
        });
      },
      onResume: (message) async {
        setState(() {
          messageTitle = message['data']['title'];
          notificationAlert = 'Application opened from Notification';
        });
      },
    );
    _checkAccelerometerStatus();
    super.initState();
  }

  @override
  void dispose() {
    _stopAccelerometer();
    super.dispose();
  }

  void _checkAccelerometerStatus() async {
    await SensorManager().isSensorAvailable(21).then((result) {
      setState(() {
        _accelAvailable = result;
      });
    });
  }

  Future<void> _startAccelerometer() async {
    if (_accelSubscription != null) return;
    if (_accelAvailable) {
      final stream = await SensorManager().sensorUpdates(
        sensorId: 21,
        interval: Sensors.SENSOR_DELAY_NORMAL,
      );
      _accelSubscription = stream.listen((sensorEvent) async {
        Map<String, String> data = {
          'time': DateTime.now().toString(),
          'value': sensorEvent.data[0].toString()
        };
        var body = json.encode(data);

        if (sensorEvent.data != 0.0) {
          Response r = await post(
            Uri.http('5f1d-213-22-132-79.ngrok.io', '/api/add_value/'),
            headers: {'Content-Type': 'application/json'},
            body: body,
          );
          print(r.statusCode);
        }
        print(sensorEvent.data);
        setState(() {
          _accelData = sensorEvent.data;
        });
      });
    }
  }

  void _stopAccelerometer() {
    if (_accelSubscription == null) return;
    _accelSubscription?.cancel();
    _accelSubscription = null;
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: Container(
          alignment: AlignmentDirectional.topCenter,
          child: Column(
            children: <Widget>[
              const Padding(padding: EdgeInsets.only(top: 35.0)),
              const Text(
                'BPM ',
                textAlign: TextAlign.center,
              ),
              Text(
                'BPM Enabled: $_accelAvailable',
                textAlign: TextAlign.center,
              ),
              Text(
                '${_accelData[0]}',
                textAlign: TextAlign.center,
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  MaterialButton(
                    child: const Text('Start'),
                    color: Colors.green,
                    onPressed:
                        _accelAvailable ? () => _startAccelerometer() : null,
                  ),
                  MaterialButton(
                    child: const Text('Stop'),
                    color: Colors.red,
                    onPressed:
                        _accelAvailable ? () => _stopAccelerometer() : null,
                  ),
                ],
              ),
              Center(
                  child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  Text(
                    notificationAlert,
                  ),
                  Text(
                    messageTitle,
                    style: Theme.of(context).textTheme.headline4,
                  ),
                ],
              ))
            ],
          ),
        ),
      ),
    );
  }
}/*
import 'package:flutter/material.dart';
import 'package:workout/workout.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  final workout = Workout();

  final exerciseType = ExerciseType.walking;
  final features = [
    WorkoutFeature.heartRate,
    WorkoutFeature.calories,
    WorkoutFeature.steps,
    WorkoutFeature.distance,
    WorkoutFeature.speed,
  ];
  final enableGps = true;

  double heartRate = 0;
  double calories = 0;
  double steps = 0;
  double distance = 0;
  double speed = 0;
  bool started = false;

  _MyAppState() {
    workout.stream.listen((event) {
      // ignore: avoid_print
      print('${event.feature}: ${event.value} (${event.timestamp})');
      switch (event.feature) {
        case WorkoutFeature.unknown:
          return;
        case WorkoutFeature.heartRate:
          setState(() {
            heartRate = event.value;
          });
          break;
        case WorkoutFeature.calories:
          setState(() {
            calories = event.value;
          });
          break;
        case WorkoutFeature.steps:
          setState(() {
            steps = event.value;
          });
          break;
        case WorkoutFeature.distance:
          setState(() {
            distance = event.value;
          });
          break;
        case WorkoutFeature.speed:
          setState(() {
            speed = event.value;
          });
          break;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData.dark().copyWith(scaffoldBackgroundColor: Colors.black),
      home: Scaffold(
        body: Center(
          child: Column(
            children: [
              const Spacer(),
              Text('Heart rate: $heartRate'),
              Text('Calories: $calories'),
              Text('Steps: $steps'),
              Text('Distance: $distance'),
              Text('Speed: $speed'),
              const Spacer(),
              TextButton(
                onPressed: toggleExerciseState,
                child: Text(started ? 'Stop' : 'Start'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void toggleExerciseState() async {
    setState(() {
      started = !started;
    });

    if (started) {
      final supportedExerciseTypes = await workout.getSupportedExerciseTypes();
      // ignore: avoid_print
      print('Supported exercise types: ${supportedExerciseTypes.length}');

      final result = await workout.start(
        // In a real application, check the supported exercise types first
        exerciseType: exerciseType,
        features: features,
        enableGps: enableGps,
      );

      if (result.unsupportedFeatures.isNotEmpty) {
        // ignore: avoid_print
        print('Unsupported features: ${result.unsupportedFeatures}');
        // In a real application, update the UI to match
      } else {
        // ignore: avoid_print
        print('All requested features supported');
      }
    } else {
      await workout.stop();
    }
  }
}*/