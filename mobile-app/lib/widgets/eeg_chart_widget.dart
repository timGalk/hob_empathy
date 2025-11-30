import 'dart:async';
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../models/eeg_data.dart';
import '../utils/config.dart';

class EEGChartWidget extends StatefulWidget {
  final Stream<EEGSample> dataStream;

  const EEGChartWidget({super.key, required this.dataStream});

  @override
  State<EEGChartWidget> createState() => _EEGChartWidgetState();
}

class _EEGChartWidgetState extends State<EEGChartWidget> {
  final List<List<FlSpot>> _channelData = List.generate(4, (_) => []);
  StreamSubscription? _subscription;
  int _dataPointCount = 0;

  @override
  void initState() {
    super.initState();
    _subscription = widget.dataStream.listen(_addDataPoint);
  }

  void _addDataPoint(EEGSample sample) {
    setState(() {
      // Only show first 4 channels for clarity
      for (int i = 0; i < 4 && i < sample.channels.length; i++) {
        _channelData[i].add(
          FlSpot(
            _dataPointCount.toDouble(),
            sample.channels[i],
          ),
        );

        // Keep only recent points
        if (_channelData[i].length > Config.maxChartPoints) {
          _channelData[i].removeAt(0);
        }
      }
      _dataPointCount++;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_channelData[0].isEmpty) {
      return const Center(
        child: Text(
          'Waiting for EEG data...',
          style: TextStyle(fontSize: 16, color: Colors.grey),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'EEG Signal (4 channels)',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: LineChart(
                LineChartData(
                  minY: -300,
                  maxY: 300,
                  lineBarsData: [
                    _createLineData(0, Colors.blue),
                    _createLineData(1, Colors.green),
                    _createLineData(2, Colors.orange),
                    _createLineData(3, Colors.red),
                  ],
                  titlesData: FlTitlesData(
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 40,
                        getTitlesWidget: (value, meta) {
                          return Text(
                            value.toInt().toString(),
                            style: const TextStyle(fontSize: 10),
                          );
                        },
                      ),
                    ),
                    topTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                  ),
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    horizontalInterval: 100,
                  ),
                  borderData: FlBorderData(show: true),
                ),
              ),
            ),
            const SizedBox(height: 8),
            _buildLegend(),
          ],
        ),
      ),
    );
  }

  LineChartBarData _createLineData(int channelIndex, Color color) {
    return LineChartBarData(
      spots: _channelData[channelIndex],
      isCurved: false,
      color: color,
      barWidth: 1.5,
      dotData: FlDotData(show: false),
    );
  }

  Widget _buildLegend() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _legendItem('Ch1', Colors.blue),
        _legendItem('Ch2', Colors.green),
        _legendItem('Ch3', Colors.orange),
        _legendItem('Ch4', Colors.red),
      ],
    );
  }

  Widget _legendItem(String label, Color color) {
    return Row(
      children: [
        Container(
          width: 16,
          height: 3,
          color: color,
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: const TextStyle(fontSize: 12),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }
}
