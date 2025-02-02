import requests
import json
import os
from pypushdeer import PushDeer

if __name__ == '__main__':
    sckey = os.environ.get("SENDKEY", "")
    title = ""
    success, fail, repeats = 0, 0, 0
    context = ""

    cookies = os.environ.get("COOKIES", "").split("&")
    if cookies[0] != "":
        check_in_url = "https://glados.space/api/user/checkin"
        status_url = "https://glados.space/api/user/status"
        referer = 'https://glados.space/console/checkin'
        origin = "https://glados.space"
        useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        payload = {'token': 'glados.one'}

        for cookie in cookies:
            checkin = requests.post(check_in_url, headers={
                'cookie': cookie,
                'referer': referer,
                'origin': origin,
                'user-agent': useragent,
                'content-type': 'application/json;charset=UTF-8'
            }, data=json.dumps(payload))

            state = requests.get(status_url, headers={
                'cookie': cookie,
                'referer': referer,
                'origin': origin,
                'user-agent': useragent
            })

            message_status = ""
            points = 0
            message_days = ""

            if checkin.status_code == 200 and state.status_code == 200:
                checkin_result = checkin.json()
                state_result = state.json()

                print("Checkin Response:", checkin_result)
                print("Status Response:", state_result)

                if 'data' not in state_result:
                    print("Error: 'data' field not found in status response!")
                    continue

                check_result = checkin_result.get('message')
                points = checkin_result.get('points', 0)
                leftdays = int(float(state_result['data']['leftDays']))
                email = state_result['data']['email']

                if "Checkin! Got" in check_result:
                    success += 1
                    message_status = "签到成功，会员点数 + " + str(points)
                elif "Checkin Repeats!" in check_result:
                    repeats += 1
                    message_status = "重复签到，明天再来"
                else:
                    fail += 1
                    message_status = "签到失败，请检查..."

                message_days = f"{leftdays} 天"
            else:
                email = ""
                message_status = "请求失败, 请检查..."
                message_days = "error"

            context += "账号: " + email + ", P: " + str(points) + ", 剩余: " + message_days + " | "

        title = f'Glados, 成功{success},失败{fail},重复{repeats}'
        print("Send Content:" + "\n", context)
    else:
        title = f'# 未找到 cookies!'

    print("sckey:", sckey)
    print("cookies:", cookies)

    if not sckey:
        print("Not push")
    else:
        pushdeer = PushDeer(pushkey=sckey)
        pushdeer.send_text(title, desp=context)
