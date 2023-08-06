// Nathaniel Green for ParkUT Senior Design Project at UToledo.
// Uses a sample from The Flutter team under an unrestricted license. Original header below.
// Copyright 2019 The Flutter team. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file in the samples home folder.

import 'dart:async';
import 'dart:math';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:google_maps_webservice/places.dart';

import 'api_key.dart';
import 'firebase_options.dart';

// Center of the Google Map
const initialPosition = LatLng(41.658183, -83.615252);
// Hue used by the Google Map Markers to match the theme
const _greenHue = 120.0;
const _yellowHue = 30.0;
const _redHue = 0.0;
const _blueHue = 240.0;
// Places API client used for Place Photos
final _placesApiClient = GoogleMapsPlaces(apiKey: googleMapsApiKey);

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const App());
}

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ParkUT',
      home: const HomePage(title: 'ParkUT'),
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: Colors.white,
      ),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({required this.title, super.key});
  final String title;

  @override
  State<StatefulWidget> createState() {
    return _HomePageState();
  }
}

class _HomePageState extends State<HomePage> {
  late Stream<QuerySnapshot> _iceCreamStores;
  final Completer<GoogleMapController> _mapController = Completer();

  @override
  void initState() {
    super.initState();
    _iceCreamStores = FirebaseFirestore.instance
        .collection('ParkingPlaces')
        .orderBy('name')
        .snapshots();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      //appBar: AppBar(
      //  title: Text(widget.title),
      //),

      body: StreamBuilder<QuerySnapshot>(
        stream: _iceCreamStores,
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          if (!snapshot.hasData) {
            return const Center(child: Text('Loading...'));
          }

          var predictions = <String, String>{};
          for (var item in snapshot.data!.docs) {
            var now = DateTime.now();
            now = now.subtract(Duration(minutes: now.minute % 15));
            var futureTime = now.add(const Duration(hours: 1));
            var g0 =
                '${now.weekday - 1} ${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}:00';
            var g1 =
                '${futureTime.weekday - 1} ${futureTime.hour.toString().padLeft(2, '0')}:${futureTime.minute.toString().padLeft(2, '0')}:00';
            var currHour = item[g0] as List<dynamic>;
            var occHour = item[g1] as List<dynamic>;
            var r0 = currHour.indexOf(-1);
            var r1 = occHour.indexOf(-1);
            var hourPred = 0.0;
            var diff = 0.0;
            var predict = "";
            if (r1 == 0) {
              predict = "N/A";
            } else {
              if (r1 == -1) {
                r1 = currHour.length;
              }
              for (var i = 0; i < r1; i++) {
                hourPred += occHour.elementAt(i) as int;
              }
              hourPred = hourPred / r1 / (item['capacity'] as int) * 100;
              if (r0 != 0) {
                if (r0 == -1) {
                  r0 = currHour.length;
                }
                for (var i = 0; i < r0; i++) {
                  diff += currHour.elementAt(i) as int;
                }
                diff = ((item['spotsfilled'] as int) * 1.0) - (diff / r0);
                diff = diff / (item['capacity'] as int) * 100;
              }
              hourPred += diff;
              hourPred = max(hourPred, 0);
              hourPred = min(hourPred, 100);
              predict = "${hourPred.toStringAsFixed(0)}%";
            }

            predictions[item.id] = predict;
          }

          return Stack(
            children: [
              StoreMap(
                documents: snapshot.data!.docs,
                initialPosition: initialPosition,
                mapController: _mapController,
                predDict: predictions,
              ),
              StoreCarousel(
                mapController: _mapController,
                documents: snapshot.data!.docs,
                predDict: predictions,
              ),
            ],
          );
        },
      ),
    );
  }
}

class StoreCarousel extends StatelessWidget {
  const StoreCarousel({
    super.key,
    required this.documents,
    required this.mapController,
    required this.predDict,
  });

  final List<DocumentSnapshot> documents;
  final Completer<GoogleMapController> mapController;
  final Map<String, String> predDict;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.topLeft,
      child: Padding(
        padding: const EdgeInsets.only(top: 25),
        child: SizedBox(
          height: 90,
          child: StoreCarouselList(
            documents: documents,
            mapController: mapController,
            predDict: predDict,
          ),
        ),
      ),
    );
  }
}

class StoreCarouselList extends StatelessWidget {
  const StoreCarouselList({
    super.key,
    required this.documents,
    required this.mapController,
    required this.predDict,
  });

  final Map<String, String> predDict;
  final List<DocumentSnapshot> documents;
  final Completer<GoogleMapController> mapController;

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      scrollDirection: Axis.horizontal,
      itemCount: documents.length,
      itemBuilder: (context, index) {
        return SizedBox(
          width: 180,
          child: Padding(
            padding: const EdgeInsets.only(left: 8),
            child: Card(
              child: Center(
                child: StoreListTile(
                  document: documents[index],
                  mapController: mapController,
                  predDict: predDict,
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class StoreListTile extends StatefulWidget {
  const StoreListTile({
    super.key,
    required this.document,
    required this.mapController,
    required this.predDict,
  });

  final DocumentSnapshot document;
  final Completer<GoogleMapController> mapController;
  final Map<String, String> predDict;

  @override
  State<StatefulWidget> createState() {
    return _StoreListTileState();
  }
}

class _StoreListTileState extends State<StoreListTile> {
  String _placePhotoUrl = '';
  bool _disposed = false;

  @override
  void initState() {
    super.initState();
    _retrievePlacesDetails();
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }

  Future<void> _retrievePlacesDetails() async {}

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(widget.document['name'] as String),
      subtitle: Text((widget.document['closed'] as bool)
          ? '${widget.document['permits']}\nClosed'
          : '${widget.document['permits']}\n${((widget.document['spotsfilled'] / widget.document['capacity']) * 100).toStringAsFixed(0)}% Full\n${widget.predDict[widget.document.id]} in 1 hour'),
      onTap: () async {
        final controller = await widget.mapController.future;
        await controller.animateCamera(
          CameraUpdate.newCameraPosition(
            CameraPosition(
              target: LatLng(
                widget.document['coords'].latitude as double,
                widget.document['coords'].longitude as double,
              ),
              zoom: 16,
            ),
          ),
        );
      },
    );
  }
}

class StoreMap extends StatelessWidget {
  const StoreMap({
    super.key,
    required this.documents,
    required this.initialPosition,
    required this.mapController,
    required this.predDict,
  });

  final List<DocumentSnapshot> documents;
  final LatLng initialPosition;
  final Completer<GoogleMapController> mapController;
  final Map<String, String> predDict;

  @override
  Widget build(BuildContext context) {
    return GoogleMap(
      initialCameraPosition: CameraPosition(
        target: initialPosition,
        zoom: 15,
      ),
      markers: documents
          .map((document) => Marker(
                markerId: MarkerId(document.id),
                icon: BitmapDescriptor.defaultMarkerWithHue((document['closed']
                        as bool)
                    ? _blueHue
                    : ((((document['spotsfilled'] / document['capacity'])
                                as double) >=
                            0.85)
                        ? _redHue
                        : ((((document['spotsfilled'] / document['capacity'])
                                    as double) >=
                                0.50)
                            ? _yellowHue
                            : _greenHue))),
                position: LatLng(
                  document['coords'].latitude as double,
                  document['coords'].longitude as double,
                ),
                infoWindow: InfoWindow(
                  title: document['name'] as String?,
                  snippet: (document['closed'] as bool)
                      ? '${document['permits']} | Closed'
                      : '${document['permits']} | ${((document['spotsfilled'] / document['capacity']) * 100).toStringAsFixed(0)}% occupied | ${predDict[document.id]} in 1 hour',
                ),
              ))
          .toSet(),
      onMapCreated: (mapController) {
        this.mapController.complete(mapController);
      },
    );
  }
}
