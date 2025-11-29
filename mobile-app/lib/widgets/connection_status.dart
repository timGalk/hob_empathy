import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/eeg_service.dart';
import '../services/backend_service.dart';

class ConnectionStatus extends StatelessWidget {
  const ConnectionStatus({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.grey[200],
        border: Border(
          bottom: BorderSide(color: Colors.grey[300]!),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatusIndicator(
            context,
            label: 'EEG Device',
            selector: (BuildContext context, EEGService service) =>
                service.isConnected,
          ),
          _buildStatusIndicator(
            context,
            label: 'Backend',
            selector: (BuildContext context, BackendService service) =>
                service.isConnected,
          ),
        ],
      ),
    );
  }

  Widget _buildStatusIndicator<T extends ChangeNotifier>(
    BuildContext context, {
    required String label,
    required bool Function(BuildContext, T) selector,
  }) {
    return Consumer<T>(
      builder: (context, service, child) {
        final isConnected = selector(context, service);
        return Row(
          children: [
            Container(
              width: 10,
              height: 10,
              decoration: BoxDecoration(
                color: isConnected ? Colors.green : Colors.red,
                shape: BoxShape.circle,
                boxShadow: isConnected
                    ? [
                        BoxShadow(
                          color: Colors.green.withOpacity(0.5),
                          blurRadius: 4,
                          spreadRadius: 1,
                        ),
                      ]
                    : null,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              label,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: Colors.grey[800],
              ),
            ),
          ],
        );
      },
    );
  }
}
