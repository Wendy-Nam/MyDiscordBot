# main.tf

# Google Cloud Provider 설정
provider "google" {
  project = "lingo-v2-460518" # GCP 프로젝트 ID
  region  = "asia-northeast3" # 리전 설정 (서울)  
  # Compute Instance 관리자 역할의 서비스 계정 키 (Github Actions에서 환경변수로 설정)
  # credentials = file("key.json") 
}
