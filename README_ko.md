# Lingo Bot: 실시간 AI 기반 한-영 상호 통역 Discord 봇

![Image](/docs/thumbnail.png)

AI 기반 번역 및 맞춤형 프롬프트를 통해 한국어의 맥락과 특징을 살려 자연스럽고 가독성 높은 번역문을 제공합니다. 봇은 사용자의 메시지 발송 즉시 상대방 언어로 번역을 덧붙여 실시간 소통과 내용 파악을 돕습니다.

## 🚧 진행도 (Lingo V2 / 2025 ver.)

- **현재 상태**: GCP Terraform 리소스 구성 및 GitHub Actions CI/CD 구축 완료. 배포 테스트 완료

- **V2 개선 사항**:
  - 디스코드 앱 슬래시 커맨드 도입 (기존 멘션/텍스트 명령어 대체).
  - `langdetect` 패키지 활용으로 언어 감지 오류 감소.
- **향후 계획**: `CI/CD 기술 문서` 및 `설치/사용 매뉴얼` 빠른 시일 내 제공 (별도 README 업데이트 예정)

---

## 🗓️ 개발 배경 (Lingo V1 / 2024 ver.)

Lingo Bot(V1)은 2024년 9월 해외 게임잼 프로젝트에서 한국어-영어 사용자 간의 언어 장벽으로 인한 소통 문제를 해결하기 위해 개발되었습니다. 개발 결과, 팀 협업 및 분위기 개선에 즉각적으로 효과를 주었고 매우 긍정적인 반응을 얻었습니다.

### 자세한 후기 : [Lingo V1 기준 - 실제 팀 도입 사례](https://educated-tarsier-f16.notion.site/GCP-IaaS-1f79bf46184a8021a6b0d52d1aee06f3?pvs=74)


## ✨ 주요 기능
* **실시간 한-영 상호 통역:** 채널 내 메시지 자동 번역 후 원문 아래 표시. (`0.5 ~ 1.5초` 내외의 즉각적인 처리)
* **AI 기반 번역:** GPT 모델 및 맞춤형 프롬프트로 자연스러운 번역.
* **채널 관리 명령어:** `!add_channel`, `!del_channel` 또는 슬래시 app command로 번역 대상 채널 및 스레드 id 관리 및 각 등록에 대한 비동기 처리.
* **텍스트 전처리:** 정규식 사용, URL 마스킹, 긴 메시지 분할.
* **디스코드 포맷팅 유지, 봇 충돌 방지.**

## 사전 준비물
- `Discord 봇 토큰`: 디스코드 Developer Portal에서 수동 생성 필요.
- `OpenAI API 토큰`: 별도 준비 필요.

## 활용 예시

> `docs/` 디렉토리의 스크린샷 참조

비즈니스, 문학, 슬랭, 관용어구, 일상 대화 등의 다양한 한-영 번역 테스트 사례를 `docs/lingoV2/`에서 스크린샷으로 확인할 수 있습니다. 오랜 **한국어 강사 경험**을 바탕으로, 자연스러운 한국어 맥락을 위해 프롬프트 조정 및 광범위한 문장 테스트를 거쳤습니다.

---

## GitHub Secrets

| Secret Name            | 용도 |
|------------------------|------|
| DISCORD_BOT_TOKEN      | Discord 봇 인증 토큰 |
| OPENAI_API_KEY         | GPT API 사용을 위한 OpenAI API 키 |
| GCP_SA_KEY             | GCP Compute Engine 접근을 위한 서비스 계정 키 |
| IGNORED_ROLE_IDS       | 번역에서 제외할 Discord 역할(role) ID 목록 |
| REMOTE_SSH_HOST        | 배포 대상 VM의 호스트 주소 |
| REMOTE_SSH_USERNAME    | VM 접근용 SSH 사용자명 |
| REMOTE_SSH_KEY         | 배포용 SSH 개인 키 |
| REMOTE_SSH_PASSPHRASE  | SSH 키 비밀번호 (passphrase) |

## 현재 한계 및 향후 개선 계획

- 현재는 **한국어 ↔ 영어 양방향 실시간 번역**만 지원합니다.
- 향후 개선 예정 사항:
    - 한국어-영어 이외의 다국어 지원
    - 채널별로 사용자 정의 가능한 번역 언어 설정 기능
    - Terraform 리모트 상태(remote state) 관리를 통한 안전한 인프라 업데이트 지원
    - 로그 관리 및 모니터링 고도화

---

## Lingo Bot V1 vs V2 비교

| 특징 | V1 | V2 |
|---|---|---|
|   **사용자 인터페이스** |   텍스트 기반 명령어 (`!add_channel`, `!del_channel`)   |   앱 슬래시 커맨드 추가 (`/add_channel`, `/del_channel`)   |
|   **언어 감지** |   기본적인 한국어 문자 포함 여부 확인 (부정확할 수 있음)   |   `langdetect` 라이브러리를 사용한 정확한 언어 감지   |
|   **환경 설정** |   실행 시 코드 변수 수정 (관리 불편)   |   `.env` 파일을 통한 분리 및 관리 (더 안전하고 편리)   |
|   **배포** |   GCP Compute Engine Free Tier 활용   |   GCP Compute Engine Free Tier 활용, Terraform 및 Github Actions를 통한 인프라 배포   |

## ⚙️ Summa 기능 (보류)

팀 대화 요약 기능으로 개발 및 테스트 되었으나, 성능 및 일정 문제로 도입 보류. V2 이전의 커밋에서 찾을 수 있음.

---

## ⚠️ 주의사항

V2 이전 시기의 모든 커밋 내역은 2024년 9월 기반으로, key 값 제거 및 커밋 재정비로 인해 깃 히스토리가 재작성되었습니다.
