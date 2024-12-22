import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ModelApi {
  ModelApi();

  Future<Map<String, dynamic>> predict(String imagePath) async {
    final baseUrl = 'http://192.168.1.6:5001';

    final url = Uri.parse('$baseUrl/predict');
    final request = http.MultipartRequest('POST', url);

    try {
      // Check if the file exists
      final file = File(imagePath);
      if (!await file.exists()) {
        print('Image file does not exist at path: $imagePath');
        return {};
      }

      // Add image file to the request
      request.files.add(await http.MultipartFile.fromPath('image', imagePath));

      // Send the request
      final streamedResponse =
          await request.send().timeout(Duration(seconds: 10));

      // Get the response
      final response = await http.Response.fromStream(streamedResponse);

      print('Status Code: ${response.statusCode}');

      if (response.statusCode == 200) {
        // Decode and return JSON response
        return json.decode(response.body);
      } else {
        // Handle non-200 responses
        print('Failed to load predictions: ${response.statusCode}');
        print('Response Body: ${response.body}');
        return {};
      }
    } on SocketException catch (e) {
      print('SocketException: $e');
      return {};
    } on http.ClientException catch (e) {
      print('ClientException: $e');
      return {};
    } on TimeoutException catch (e) {
      print('TimeoutException: $e');
      return {};
    } catch (e) {
      // Handle other errors
      print('Error fetching prediction: $e');
      return {};
    }
  }
}
