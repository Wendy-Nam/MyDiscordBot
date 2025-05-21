#!/bin/bash

# 항상 run.sh가 있는 디렉토리 기준으로 동작하도록 설정
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 스크립트 설정
PYTHON_SCRIPT="main.py"
LOG_DIR="./logs"
PYTHON_EXECUTABLE="python3" # python 3.12.2
PID_FILE="./bot.pid" # 봇 프로세스 PID를 저장할 파일

# 현재 환경 변수 초기화 (특정 변수만)
unset DISCORD_BOT_TOKEN
unset OPENAI_API_KEY
unset IGNORED_ROLE_IDS

# .env 파일 로드
set -o allexport
if [ -f ".env" ]; then
  source .env
  echo ".env 파일의 환경 변수를 로드했습니다."
else
  echo "경고: .env 파일을 찾을 수 없습니다. 환경 변수가 올바르게 설정되었는지 확인하세요."
  # .env 파일이 필수적이라면, 여기서 exit 1을 추가하여 스크립트 실행을 중단할 수 있습니다.
  # exit 1
fi
set +o allexport

# 로그 디렉토리 생성 (없으면)
mkdir -p "$LOG_DIR"

# 현재 일자, 시점 기반의 로그 파일 이름 생성
TIMESTAMP=$(date "+%Y%m%d-%H%M%S")
LOG_FILE="$LOG_DIR/$TIMESTAMP-$$.log" # run.sh의 PID를 포함한 로그 파일 이름

# 트랩 설정: run.sh 스크립트 자체의 종료 신호 처리
cleanup() {
  echo "run.sh 스크립트 종료 신호 감지 또는 오류 발생." >> "$LOG_FILE"
  # 여기서 봇 프로세스를 직접 종료하지 않습니다.
  # 봇 프로세스는 nohup에 의해 독립적으로 실행되고, stop.sh 스크립트로 제어됩니다.
  exit 0
}

trap cleanup SIGINT SIGTERM ERR

echo "run.sh 스크립트 시작 (PID: $$), 로그 파일: $LOG_FILE" >> "$LOG_FILE"

# requirements.txt가 있는 경우, 패키지 설치
if [ -f "requirements.txt" ]; then
  echo "requirements.txt 파일을 찾았습니다. 필요한 패키지를 설치합니다..." >> "$LOG_FILE"
  "$PYTHON_EXECUTABLE" -m pip install -r requirements.txt >> "$LOG_FILE" 2>&1
  if [ $? -ne 0 ]; then
    echo "오류: pip 설치 실패. 스크립트를 종료합니다." >> "$LOG_FILE"
    exit 1
  fi
  echo "필요한 패키지 설치 완료." >> "$LOG_FILE"
fi

# 기존에 실행 중인 봇 프로세스가 있다면 종료 (재시작 시 유용)
if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE")
  if ps -p "$OLD_PID" > /dev/null; then
    echo "기존 봇 프로세스 (PID: $OLD_PID) 종료 시도..." >> "$LOG_FILE"
    kill "$OLD_PID"
    sleep 5 # 종료 대기
    if ps -p "$OLD_PID" > /dev/null; then
      echo "기존 봇 프로세스 (PID: $OLD_PID) 강제 종료 시도..." >> "$LOG_FILE"
      kill -9 "$OLD_PID"
    fi
  fi
  rm -f "$PID_FILE" # PID 파일 삭제
fi


# Python 스크립트(main.py)를 nohup을 사용하여 백그라운드에서 실행
# 이 명령어는 main.py를 독립적인 프로세스로 만들고, run.sh가 종료되어도 계속 실행되게 합니다.
# 봇의 출력은 지정된 LOG_FILE로 리다이렉션됩니다.
nohup "$PYTHON_EXECUTABLE" "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1 &

# nohup으로 실행된 백엔드 파이썬 프로세스의 PID를 캡처
BACKEND_PID=$!
echo "$BACKEND_PID" > "$PID_FILE" # PID를 파일에 저장

echo "백엔드 파이썬 프로세스 PID: $BACKEND_PID" >> "$LOG_FILE"
echo "백엔드 프로세스가 nohup으로 백그라운드에서 실행 중입니다. 로그는 $LOG_FILE에 기록됩니다." >> "$LOG_FILE"
echo "봇 프로세스 PID가 $PID_FILE에 저장되었습니다." >> "$LOG_FILE"

# run.sh 스크립트 완료 후 즉시 종료
echo "run.sh 스크립트 완료. 봇은 백그라운드에서 실행 중입니다." >> "$LOG_FILE"
exit 0
