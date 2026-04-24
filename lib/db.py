import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def query(table: str, filters: dict = None, columns: str = "*"):
    sb = get_client()
    q = sb.table(table).select(columns)
    if filters:
        for k, v in filters.items():
            q = q.eq(k, v)
    return q.execute().data


def upsert(table: str, data: dict | list):
    sb = get_client()
    return sb.table(table).upsert(data).execute().data


def insert(table: str, data: dict | list):
    sb = get_client()
    return sb.table(table).insert(data).execute().data


def update(table: str, match: dict, data: dict):
    sb = get_client()
    q = sb.table(table).update(data)
    for k, v in match.items():
        q = q.eq(k, v)
    return q.execute().data


def get_config(key: str) -> str:
    rows = query("config", {"key": key})
    return rows[0]["value"] if rows else None
