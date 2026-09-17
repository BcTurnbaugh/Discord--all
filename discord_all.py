import asyncio
import json
import time
import threading
import pyperclip
import websockets

from pynput.keyboard import Controller, Key
from pynput import keyboard as 키보드


호스트="127.0.0.1"
포트=8765

메시지당_구성원수=20

붙여넣기_지연=.08
공백_지연=.03
엔터_지연=.15

키보드제어기=Controller()
중지=threading.Event()
실행중=False


def 키누르기(키):
    키보드제어기.press(키)
    키보드제어기.release(키)


def 붙여넣기(내용):
    pyperclip.copy(내용)
    time.sleep(.02)

    키보드제어기.press(Key.ctrl)
    키보드제어기.press("v")

    키보드제어기.release("v")
    키보드제어기.release(Key.ctrl)


def 구성원이름입력(이름):
    이름=''.join(이름.split())

    if not 이름:
        return False

    붙여넣기("@" + 이름)

    time.sleep(붙여넣기_지연)

    if 중지.is_set():
        return False

    키누르기(Key.space)

    time.sleep(공백_지연)

    return True


def 구성원멘션(이름들):

    global 실행중

    실행중=True
    중지.clear()

    전체수=len(이름들)

    메시지수=(
        전체수+
        메시지당_구성원수-
        1
    )//메시지당_구성원수

    print()
    print("======================================")
    print(" 디스코드 @전체")
    print("======================================")
    print()

    print(f"찾은 구성원: {전체수}명")
    print(f"메시지당 구성원: {메시지당_구성원수}명")
    print(f"필요한 메시지: {메시지수}개")
    print()
    print("ESC를 누르면 중지됩니다.")
    print()

    try:

        for 메시지번호,시작위치 in enumerate(
            range(
                0,
                전체수,
                메시지당_구성원수
            ),
            1
        ):

            묶음=이름들[
                시작위치:
                시작위치+메시지당_구성원수
            ]

            if 중지.is_set():
                print("중지됨")
                return

            print()
            print(
                f"메시지 "
                f"{메시지번호}/"
                f"{메시지수} "
                f"({len(묶음)}명)"
            )

            for 묶음번호,이름 in enumerate(
                묶음,
                1
            ):

                if 중지.is_set():
                    print("중지됨")
                    return

                전체번호=시작위치+묶음번호

                print(
                    f"[{전체번호}/{전체수}] "
                    f"{이름}"
                )

                if not 구성원이름입력(이름):
                    print("중지됨")
                    return

            if 메시지번호<메시지수:

                print("엔터 입력")

                키누르기(Key.enter)

                time.sleep(엔터_지연)

    finally:

        실행중=False

    print()
    print("======================================")
    print("완료")
    print("======================================")
    print(f"총 구성원: {전체수}명")
    print(f"총 메시지: {메시지수}개")
    print()


def 키눌림(키):

    if 키==키보드.Key.esc and 실행중:

        print()
        print("ESC 입력 — 중지 중...")
        중지.set()


def 키보드감시():

    감시기=키보드.Listener(
        on_press=키눌림
    )

    감시기.daemon=True
    감시기.start()


async def 메시지처리(소켓):

    print("Tampermonkey 연결됨")

    async for 메시지 in 소켓:

        try:

            데이터=json.loads(메시지)

            if 데이터.get("action")!="mention":
                continue

            이름들=데이터.get(
                "names",
                []
            )

            if not 이름들:
                continue

            if 실행중:
                print("이미 실행 중입니다.")
                continue

            await asyncio.to_thread(
                구성원멘션,
                이름들
            )

        except Exception as 오류:

            print(
                "오류:",
                오류
            )


async def 메인():

    print(
        f"디스코드 @전체 도우미 "
        f"- ws://{호스트}:{포트}"
    )

    print(
        f"메시지당 {메시지당_구성원수}명"
    )

    print(
        "ESC = 중지"
    )

    print()

    키보드감시()

    async with websockets.serve(
        메시지처리,
        호스트,
        포트
    ):

        await asyncio.Future()


if __name__=="__main__":

    try:

        asyncio.run(
            메인()
        )

    except KeyboardInterrupt:

        print(
            "\n프로그램 종료"
        )