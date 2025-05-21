# Terraform 변수 정의: terraform.tfvars 파일을 사용

variable "discord_bot_token" {
  description = "Discord bot token"
  type        = string
  sensitive   = true # 민감한 정보 - 출력 시 숨겨짐
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true # 민감한 정보 - 출력 시 숨겨짐
}

variable "ignored_role_id" {
  description = "Discord role IDs to ignore (comma-separated)"
  type        = string
  sensitive   = true # 민감한 정보 - 출력 시 숨겨짐
}

variable "github_repo_url" {
  description = "URL of the GitHub repository containing your Python code"
  type        = string
}

variable "startup_script_name" {
  description = "Name of the shell script to execute within the cloned directory (e.g., run.sh)"
  type        = string
}