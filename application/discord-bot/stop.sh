#!/bin/bash

PID_FILE="./bot.pid"
LOG_DIR="./logs" # run.sh와 동일한 로그 디렉토리 사용
TIMESTAMP=$(date "+%Y%m%d-%H%M%S")
STOP_LOG_FILE="$LOG_DIR/stop-$TIMESTAMP.log" # 종료 로그 파일

echo "봇 종료 스크립트 시작" >> "$STOP_LOG_FILE"

if [ -f "$PID_FILE" ]; then
  BOT_PID=$(cat "$PID_FILE")
  if ps -p "$BOT_PID" > /dev/null; then
    echo "봇 프로세스 (PID: $BOT_PID) 종료 시도..." >> "$STOP_LOG_FILE"
    kill "$BOT_PID" # SIGTERM (정상 종료 신호) 전송
    sleep 10 # 봇이 종료될 시간을 충분히 줍니다. (봇의 종료 로직에 따라 조절)

    if ps -p "$BOT_PID" > /dev/null; then
      echo "봇 프로세스 (PID: $BOT_PID)가 아직 실행 중입니다. 강제 종료 시도..." >> "$STOP_LOG_FILE"
      kill -9 "$BOT_PID" # SIGKILL (강제 종료) 전송
    fi
    echo "봇 프로세스 종료 시도 완료." >> "$STOP_LOG_FILE"
  else
    echo "PID 파일은 존재하지만, 해당 PID ($BOT_PID)의 프로세스가 실행 중이지 않습니다." >> "$STOP_LOG_FILE"
  fi
  rm -f "$PID_FILE" # PID 파일 삭제
else
  echo "PID 파일 ($PID_FILE)을 찾을 수 없습니다. 봇이 실행 중이지 않거나 PID 파일이 없습니다." >> "$STOP_LOG_FILE"
fi

echo "봇 종료 스크립트 완료" >> "$STOP_LOG_FILE"
exit 0