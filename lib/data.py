import json, pathlib
import streamlit as st

_ROOT = pathlib.Path(__file__).parent.parent


def load_fixture() -> list[dict]:
    try:
        return json.loads((_ROOT / "data/fixture.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"Error cargando fixture.json: {e}")
        st.stop()


def load_teams() -> dict[str, dict]:
    """Devuelve teams indexados por id."""
    try:
        raw = json.loads((_ROOT / "data/teams.json").read_text(encoding="utf-8"))
        return {t["id"]: t for t in raw}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"Error cargando teams.json: {e}")
        st.stop()
