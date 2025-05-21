#!/bin/bash

# 스크립트 설정
PYTHON_SCRIPT="main.py"
LOG_DIR="./logs"
PYTHON_EXECUTABLE="python3" # python 3.12.2

# 현재 환경 변수 초기화 (특정 변수만)
unset DISCORD_BOT_TOKEN
unset OPENAI_API_KEY
unset IGNORED_ROLE_IDS

# .env 파일 로드
set -o allexport
if [ -f ".env" ]; then
  source .env
  echo ".env 파일의 환경 변수를 로드했습니다."
fi
set +o allexport

# 로그 디렉토리 생성 (없으면)
mkdir -p "$LOG_DIR"

# 현재 일자, 시점 기반의 로그 파일 이름 생성 및 PID 포함
TIMESTAMP=$(date "+%Y%m%d-%H%M%S")
PID=$$
LOG_FILE="$LOG_DIR/$TIMESTAMP-$PID.log"

# 트랩 설정: 종료 신호(SIGINT, SIGTERM) 및 예상치 못한 오류 시 안전하게 종료
cleanup() {
  echo "종료 신호 감지 또는 오류 발생. 백엔드 프로세스 안전하게 종료 시도..."
  if [ -n "$BACKEND_PID" ]; then
    echo "백엔드 프로세스 (PID: $BACKEND_PID)에 종료 신호 보냄..."
    kill "$BACKEND_PID"
    sleep 1 # 잠시 기다린 후 강제 종료 시도
    if ps -p "$BACKEND_PID" > /dev/null; then
      echo "백엔드 프로세스가 아직 실행 중입니다. 강제 종료 시도..."
      kill -9 "$BACKEND_PID"
    fi
    echo "백엔드 프로세스 종료 시도 완료."
  fi
  exit 0
}

trap cleanup SIGINT SIGTERM ERR

echo "백엔드 프로세스 시작 (PID: $PID), 로그 파일: $LOG_FILE"

# requirements.txt가 있는 경우, 패키지 설치
if [ -f "requirements.txt" ]; then
  echo "requirements.txt 파일을 찾았습니다. 필요한 패키지를 설치합니다..."
  "$PYTHON_EXECUTABLE" -m pip install -r requirements.txt
  if [ $? -ne 0 ]; then
    echo "오류: pip 설치 실패. 스크립트를 종료합니다."
    exit 1
  fi
  echo "필요한 패키지 설치 완료."
fi

# nohup을 사용하여 백그라운드 실행 및 로그 저장
nohup "$PYTHON_EXECUTABLE" "$PYTHON_SCRIPT" > "$LOG_FILE" 2>&1 &

BACKEND_PID=$!
echo "백엔드 파이썬 프로세스 PID: $BACKEND_PID"
echo "백엔드 프로세스가 nohup으로 백그라운드에서 실행 중입니다. 로그는 $LOG_FILE에 기록됩니다."
tail -f "$LOG_FILE"
# 스크립트가 종료되지 않도록 백엔드 프로세스 대기
wait "$BACKEND_PID"

echo "백엔드 프로세스 종료 감지. 쉘 스크립트 종료."

exit 0