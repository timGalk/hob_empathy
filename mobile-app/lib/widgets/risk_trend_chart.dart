import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

class RiskTrendChart extends StatelessWidget {
  final List<double> riskData;

  const RiskTrendChart({super.key, required this.riskData});

  @override
  Widget build(BuildContext context) {
    if (riskData.isEmpty) {
      return const Center(
        child: Text('No data available'),
      );
    }

    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: 0.2,
          getDrawingHorizontalLine: (value) {
            return FlLine(
              color: Colors.grey.withOpacity(0.2),
              strokeWidth: 1,
            );
          },
        ),
        titlesData: FlTitlesData(
          show: true,
          rightTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          topTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 30,
              interval: (riskData.length / 5).ceil().toDouble(),
              getTitlesWidget: (value, meta) {
                if (value == meta.max || value == meta.min) {
                  return const SizedBox.shrink();
                }
                return Text(
                  '${value.toInt()}',
                  style: const TextStyle(fontSize: 10, color: Colors.grey),
                );
              },
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              interval: 0.2,
              reservedSize: 40,
              getTitlesWidget: (value, meta) {
                return Text(
                  '${(value * 100).toInt()}%',
                  style: const TextStyle(fontSize: 10, color: Colors.grey),
                );
              },
            ),
          ),
        ),
        borderData: FlBorderData(
          show: true,
          border: Border.all(color: Colors.grey.withOpacity(0.3)),
        ),
        minX: 0,
        maxX: (riskData.length - 1).toDouble(),
        minY: 0,
        maxY: 1.0,
        lineBarsData: [
          LineChartBarData(
            spots: List.generate(
              riskData.length,
              (index) => FlSpot(index.toDouble(), riskData[index]),
            ),
            isCurved: true,
            gradient: LinearGradient(
              colors: [
                Colors.green,
                Colors.orange,
                Colors.red,
              ],
            ),
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: FlDotData(
              show: true,
              getDotPainter: (spot, percent, barData, index) {
                Color color;
                if (spot.y < 0.3) {
                  color = Colors.green;
                } else if (spot.y < 0.6) {
                  color = Colors.orange;
                } else {
                  color = Colors.red;
                }
                return FlDotCirclePainter(
                  radius: 4,
                  color: color,
                  strokeWidth: 2,
                  strokeColor: Colors.white,
                );
              },
            ),
            belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(
                colors: [
                  Colors.green.withOpacity(0.1),
                  Colors.orange.withOpacity(0.1),
                  Colors.red.withOpacity(0.1),
                ],
              ),
            ),
          ),
        ],
        lineTouchData: LineTouchData(
          enabled: true,
          touchTooltipData: LineTouchTooltipData(
            getTooltipItems: (List<LineBarSpot> touchedBarSpots) {
              return touchedBarSpots.map((barSpot) {
                final risk = barSpot.y;
                String level;
                Color color;

                if (risk < 0.3) {
                  level = 'Normal';
                  color = Colors.green;
                } else if (risk < 0.6) {
                  level = 'Mild';
                  color = Colors.orange;
                } else {
                  level = 'High';
                  color = Colors.red;
                }

                return LineTooltipItem(
                  '${(risk * 100).toInt()}%\n$level',
                  TextStyle(
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                );
              }).toList();
            },
          ),
        ),
      ),
    );
  }
}
