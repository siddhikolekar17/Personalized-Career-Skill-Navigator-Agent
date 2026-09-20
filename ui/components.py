"""Reusable UI pieces and the app's CSS.

Visual idea: a career navigator should feel like wayfinding. The destination role
appears on a green highway-style sign, the route bar shows how far along you are,
and each roadmap phase is a small road sign. Everything else stays quiet.

All HTML is built as single-line strings on purpose: Streamlit's markdown parser
treats indented lines as code blocks.
"""
from __future__ import annotations

from html import escape

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Condensed:wght@500;600;700&display=swap');
:root{--ink:#1D2B33;--muted:#5B6B73;--paper:#F2F5F3;--sign:#0E5A45;--amber:#F5B700;--route:#2F6DB5;
--alert:#B93A24;--ok:#1E8E5A;--line:#D3DCD7;--panel:#FFFFFF;}
html,body,.stApp{font-family:'Barlow',system-ui,sans-serif;color:var(--ink);}
.stApp{background:var(--paper);}
.block-container{max-width:1180px;padding-top:4rem;}
.stApp h1,.stApp h2,.stApp h3,.stApp h4{font-family:'Barlow Condensed',system-ui,sans-serif;font-weight:600;color:var(--ink);letter-spacing:.005em;}
.stApp h2{font-size:1.7rem;} .stApp h3{font-size:1.35rem;}
.stTabs [data-baseweb="tab"]{font-family:'Barlow Condensed',sans-serif;font-size:1.15rem;font-weight:600;}
.sign{background:var(--sign);color:#fff;border-radius:18px;padding:26px 32px 20px;margin-bottom:16px;
box-shadow:inset 0 0 0 4px var(--sign),inset 0 0 0 7px rgba(255,255,255,.92);}
.sign-title{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:3rem;line-height:1.02;}
.sign-sub{font-size:1.05rem;opacity:.93;max-width:62ch;margin-top:6px;}
.route{position:relative;height:12px;margin:24px 6px 12px;border-radius:6px;
background:repeating-linear-gradient(90deg,rgba(255,255,255,.55) 0 14px,transparent 14px 24px);}
.route-fill{position:absolute;left:0;top:0;height:100%;background:var(--amber);border-radius:6px;}
.route-pin{position:absolute;top:50%;width:22px;height:22px;border-radius:50%;background:var(--amber);
border:3px solid #fff;transform:translate(-50%,-50%);}
.route-caption{display:flex;justify-content:space-between;gap:12px;font-size:.98rem;flex-wrap:wrap;}
.strip{display:grid;grid-template-columns:repeat(4,1fr);background:var(--panel);border:1px solid var(--line);
border-radius:12px;margin-bottom:18px;}
.strip-cell{padding:14px 18px;border-right:1px solid var(--line);}
.strip-cell:last-child{border-right:none;}
.strip-label{color:var(--muted);font-size:.92rem;}
.strip-value{font-family:'Barlow Condensed',sans-serif;font-size:2.1rem;font-weight:600;line-height:1.1;}
.strip-sub{color:var(--muted);font-size:.86rem;}
@media(max-width:800px){.strip{grid-template-columns:repeat(2,1fr);}.strip-cell{border-bottom:1px solid var(--line);}
.sign-title{font-size:2.2rem;}}
.plate{display:inline-block;background:var(--sign);color:#fff;border-radius:8px;padding:5px 16px;margin-top:10px;
font-family:'Barlow Condensed',sans-serif;font-size:1.3rem;font-weight:600;
box-shadow:inset 0 0 0 2px var(--sign),inset 0 0 0 3.5px rgba(255,255,255,.9);}
.plate-desc{color:var(--muted);margin:4px 0 10px;}
.stop-title{font-weight:600;font-size:1.05rem;}
.stop-meta{color:var(--muted);font-size:.92rem;margin-top:2px;}
.stop-meta span+span{margin-left:10px;padding-left:10px;border-left:1px solid var(--line);}
.stop-meta a{margin-left:12px;}
.tag{display:inline-block;font-size:.8rem;font-weight:600;border-radius:4px;padding:1px 8px;margin-right:8px;vertical-align:middle;}
.tag-course{background:#DCE9F7;color:#1D4E89;} .tag-project{background:#DDF1E6;color:#17603B;}
.tag-certification{background:#FBEBB8;color:#6B4E00;} .tag-activity{background:#ECEDEE;color:#444;}
.badge{display:inline-block;font-size:.82rem;font-weight:600;border-radius:999px;padding:1px 10px;}
.badge-missing{background:#F6D9D3;color:#8C2A17;} .badge-underdeveloped{background:#FBEBB8;color:#6B4E00;}
.badge-met{background:#D6EEDF;color:#17603B;}
.career{border:1px solid var(--line);background:var(--panel);border-radius:10px;padding:12px 16px;margin-bottom:10px;}
.career.selected{border-color:var(--sign);box-shadow:inset 4px 0 0 var(--sign);}
.career-name{font-family:'Barlow Condensed',sans-serif;font-size:1.3rem;font-weight:600;}
.career-meta{color:var(--muted);font-size:.9rem;margin-top:4px;}
.meter{height:8px;background:#E3E9E6;border-radius:4px;overflow:hidden;margin-top:6px;}
.meter>div{height:100%;background:var(--sign);}
.note{border-left:4px solid var(--route);background:var(--panel);padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;}
.note-progress,.note-done{border-color:var(--ok);} .note-market,.note-slight{border-color:var(--amber);} .note-behind{border-color:var(--alert);}
.skillrow{display:grid;grid-template-columns:200px 1fr 90px;gap:12px;align-items:center;margin-bottom:8px;}
.skillrow .meter{margin-top:0;height:10px;}
.skillrow-pct{color:var(--muted);text-align:right;font-size:.92rem;}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(name: str, role: str, match: float, readiness: str, weeks: int, weekly_hours: int) -> None:
    pct = max(0.0, min(100.0, match))
    eta = f"about {weeks} weeks at {weekly_hours} hours a week" if weeks else "no learning steps left"
    st.markdown(
        f'<div class="sign"><div class="sign-title">{escape(role)}</div>'
        f'<div class="sign-sub">{escape(name)}, here is your route: {eta}.</div>'
        f'<div class="route"><div class="route-fill" style="width:{pct}%"></div>'
        f'<div class="route-pin" style="left:{pct}%"></div></div>'
        f'<div class="route-caption"><span>You already cover {pct:.0f}% of what this role needs</span>'
        f"<span>{escape(readiness)}</span></div></div>",
        unsafe_allow_html=True,
    )


def metric_strip(items: list[tuple[str, str, str]]) -> None:
    cells = "".join(
        f'<div class="strip-cell"><div class="strip-label">{escape(label)}</div>'
        f'<div class="strip-value">{escape(value)}</div><div class="strip-sub">{escape(sub)}</div></div>'
        for label, value, sub in items
    )
    st.markdown(f'<div class="strip">{cells}</div>', unsafe_allow_html=True)


def plate(title: str, description: str) -> None:
    st.markdown(
        f'<div class="plate">{escape(title)}</div><div class="plate-desc">{escape(description)}</div>',
        unsafe_allow_html=True,
    )


def stop_html(item: dict, type_label: str) -> str:
    link = (
        f' <a href="{escape(item["link"])}" target="_blank" rel="noopener">Find it</a>' if item.get("link") else ""
    )
    return (
        f'<div class="stop-title"><span class="tag tag-{item["type"]}">{escape(type_label)}</span>'
        f'{escape(item["title"])}</div>'
        f'<div class="stop-meta"><span>{escape(item["skill"])}</span><span>{escape(item["provider"])}</span>'
        f'<span>{item["hours"]} h</span><span>weeks {item["start_week"]} to {item["end_week"]}</span>{link}</div>'
    )


def badge(text: str) -> str:
    return f'<span class="badge badge-{text.lower()}">{escape(text)}</span>'


def career_card(c: dict, selected: bool) -> None:
    interests = (
        f"Matches your interest in {escape(', '.join(c['matched_interests']))}. " if c["matched_interests"] else ""
    )
    st.markdown(
        f'<div class="career{" selected" if selected else ""}">'
        f'<div class="career-name">{escape(c["name"])}{" (your target)" if selected else ""}</div>'
        f'<div class="meter"><div style="width:{c["fit"]}%"></div></div>'
        f'<div class="career-meta">{c["fit"]:.0f}% fit. {c["match"]:.0f}% of skills covered. {interests}</div></div>',
        unsafe_allow_html=True,
    )


def note(kind: str, text: str) -> None:
    st.markdown(f'<div class="note note-{kind}">{escape(text)}</div>', unsafe_allow_html=True)


def skill_meter(label: str, pct: float, right: str) -> None:
    pct = max(0.0, min(100.0, pct))
    st.markdown(
        f'<div class="skillrow"><div>{escape(label)}</div><div class="meter"><div style="width:{pct}%"></div></div>'
        f'<div class="skillrow-pct">{escape(right)}</div></div>',
        unsafe_allow_html=True,
    )
