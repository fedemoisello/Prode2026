def flag_img(team: dict, size: int = 20) -> str:
    iso2 = team.get("iso2", "")
    if not iso2:
        return team.get("flag", "")
    return f'<img src="https://flagcdn.com/w{size}/{iso2}.png" height="{size}" style="vertical-align:middle;margin-right:4px">'


def team_label(team: dict) -> str:
    return f'{flag_img(team)}{team["nombre"]}'
