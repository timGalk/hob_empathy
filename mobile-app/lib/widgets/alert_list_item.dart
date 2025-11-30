import 'package:flutter/material.dart';
import '../models/dashboard_models.dart';

class AlertListItem extends StatelessWidget {
  final AlertHistory alert;
  final VoidCallback onAcknowledge;

  const AlertListItem({
    super.key,
    required this.alert,
    required this.onAcknowledge,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: alert.severityColor.withOpacity(0.1),
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: alert.severityColor,
          child: Icon(alert.severityIcon, color: Colors.white),
        ),
        title: Text(
          alert.message,
          style: const TextStyle(fontSize: 14),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              _formatTimestamp(alert.timestamp),
              style: const TextStyle(fontSize: 12),
            ),
            if (alert.riskScore != null)
              Text(
                'Risk: ${(alert.riskScore! * 100).toInt()}%',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
              ),
          ],
        ),
        trailing: alert.acknowledged
            ? const Icon(Icons.check_circle, color: Colors.green)
            : IconButton(
                icon: const Icon(Icons.check),
                onPressed: onAcknowledge,
                tooltip: 'Acknowledge',
              ),
      ),
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final diff = now.difference(timestamp);

    if (diff.inMinutes < 1) {
      return 'Just now';
    } else if (diff.inMinutes < 60) {
      return '${diff.inMinutes}m ago';
    } else if (diff.inHours < 24) {
      return '${diff.inHours}h ago';
    } else {
      return '${diff.inDays}d ago';
    }
  }
}
