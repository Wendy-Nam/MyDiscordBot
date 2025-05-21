# 인스턴스 외부 IP 주소 출력 (접속 확인용)
output "instance_external_ip" {
  value       = google_compute_instance.python_app_instance.network_interface[0].access_config[0].nat_ip
  description = "The external IP address of the Python application instance."
}