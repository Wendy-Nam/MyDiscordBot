# Compute Engine 인스턴스 생성
resource "google_compute_instance" "python_app_instance" {
  name         = "python-app-instance"
  machine_type = "e2-micro" # GCP 프리티어 머신 타입
  zone         = "asia-northeast3-a" # 리전 내의 특정 존을 지정 (예: asia-east1-a)

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts" # Ubuntu 20.04 LTS 이미지
    }
  }

  network_interface {
    network = "default" # 기본 VPC 네트워크 사용
    access_config {
      # 외부 IP 주소 할당 (기본)
    }
  }

  # Discord 봇은 일반적으로 HTTP/HTTPS 트래픽을 직접 서비스하지 않으므로, 관련 태그와 방화벽 규칙은 제거
  # 만약 봇이 웹 대시보드나 웹훅을 수신해야 한다면, 해당 포트를 허용하는 규칙을 추가해야 함
  # tags = ["http-server", "https-server"] # 제거됨

  # 최초 부팅 시 python3, pip, git 설치만 수행
  metadata_startup_script = <<-EOF
    #!/bin/bash
    exec > /var/log/startup-script.log 2>&1
    set -x

    apt update -y
    apt install -y python3 python3-pip git
  EOF

  # 인스턴스 삭제 시 부팅 디스크도 함께 삭제
  deletion_protection = false
}
