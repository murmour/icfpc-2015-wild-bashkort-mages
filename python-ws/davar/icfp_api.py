
import subprocess


team_id = 42
team_token = ":C0x3lXwXH12jFaTOA1LEKRHycE9aeXAsaAmm8UPFlPE="


def send_solution(json) -> bool:
    res = subprocess.call(
        ["curl",
         "--user", team_token,
         "-X", "POST",
         "-H", "Content-Type: application/json",
         "-d", json,
         "https://davar.icfpcontest.org/teams/%s/solutions" % team_id ])

    return (res == 0)
