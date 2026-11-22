"""Dashboard Hotel - studi kasus portofolio (dataset simulasi). Tema gelap, satu grafik = satu pertanyaan."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Dashboard Hotel", page_icon="🏨", layout="wide")
GOLD, NAVY, PANEL, CREAM, MUTED = "#D4AF37", "#0B1220", "#16213A", "#F2E9D0", "#9AA6BF"
GREEN, RED = "#4CC38A", "#F26B5B"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAYS_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
jt = lambda x: f"Rp {x/1e6:,.0f} juta".replace(",", ".")

st.markdown(f"""<style>
.stApp {{background:{NAVY}; color:{CREAM};}}
[data-testid="stSidebar"] {{background:#101A30;}}
.stApp h1, .stApp h2, .stApp h3, .stApp label, .stApp p, .stApp span, [data-testid="stMarkdownContainer"] {{color:{CREAM};}}
span[data-baseweb="tag"] {{background:{GOLD} !important; color:{NAVY} !important;}}
span[data-baseweb="tag"] span {{color:{NAVY} !important;}}
.hero {{border:1px solid {GOLD}66; border-radius:18px; padding:22px 28px; background:linear-gradient(135deg,#16213A,#0E1730); margin-bottom:14px;}}
.hero h1 {{font-family:Georgia,serif !important; font-size:2.4rem !important; color:{GOLD} !important; margin:0 !important; padding:0 !important;}}
.hero p {{color:{MUTED} !important; margin:4px 0 0 0;}}
.kpi {{border-radius:14px; padding:16px 18px; background:{PANEL}; border-top:4px solid {GOLD};}}
.kpi .l {{color:{MUTED}; font-size:.85rem;}} .kpi .v {{color:{CREAM}; font-size:1.7rem; font-weight:700; white-space:nowrap;}}
.kpi.red {{border-top-color:{RED};}} .kpi.green {{border-top-color:{GREEN};}}
.answer {{background:{PANEL}; border-left:5px solid {GOLD}; border-radius:10px; padding:12px 18px; margin:10px 0 16px; font-size:1.05rem;}}
.cap {{color:{MUTED}; font-size:.9rem; margin:-4px 0 8px;}}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load(path="data/hotel_booking_revenue_analysis_raw.csv"):
    df = pd.read_csv(path).drop_duplicates(subset="booking_id").copy()
    for c in ["booking_channel", "payment_method", "customer_type"]:
        df[c] = df[c].fillna("Unknown")
    df["check_in"] = pd.to_datetime(df["check_in"])
    df["month"] = df["check_in"].dt.to_period("M").astype(str)
    df["dow"] = df["check_in"].dt.day_name()
    df["cancelled"] = df["booking_status"].eq("Cancelled")
    df["potential"] = df["nights"] * df["nightly_rate"]
    return df


def dark(fig, h=360):
    fig.update_layout(template="plotly_dark", height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=10, r=10, t=10, b=10), font=dict(color=CREAM, size=14), showlegend=False)
    return fig


def kpi(col, label, value, cls=""):
    col.markdown(f'<div class="kpi {cls}"><div class="l">{label}</div><div class="v">{value}</div></div>', unsafe_allow_html=True)


def answer(t):
    st.markdown(f'<div class="answer">💬 {t}</div>', unsafe_allow_html=True)


def title(t, cap=None):
    st.markdown(f"**{t}**")
    if cap:
        st.markdown(f'<div class="cap">{cap}</div>', unsafe_allow_html=True)


df = load()
months = sorted(df["month"].unique())
st.sidebar.markdown("### 🏨 Filter")
sel = st.sidebar.multiselect("Bulan check-in", months, default=months)
st.sidebar.caption("Studi kasus portofolio · dataset simulasi\nDibuat oleh Ihsan Amiruddin")
f = df[df["month"].isin(sel)]
if f.empty:
    st.warning("Pilih minimal satu bulan di sidebar."); st.stop()
ok = f[~f["cancelled"]]
lost = f.loc[f["cancelled"], "potential"].sum()
total = ok["revenue"].sum() + lost

st.markdown('<div class="hero"><h1>🏨 Dashboard Pendapatan Hotel</h1><p>Booking, pendapatan, dan pembatalan · Januari–Juni 2026 · studi kasus dengan dataset simulasi</p></div>', unsafe_allow_html=True)
k = st.columns(4)
kpi(k[0], "Pendapatan terealisasi", jt(ok["revenue"].sum()), "green")
kpi(k[1], "Pendapatan hilang karena batal", jt(lost), "red")
kpi(k[2], "Booking dibatalkan", f"{f['cancelled'].mean()*100:.1f}%  ({int(f['cancelled'].sum())} dari {len(f)})", "red")
kpi(k[3], "Tarif rata-rata per malam", f"Rp {ok['nightly_rate'].mean()/1e3:,.0f} ribu".replace(",", "."))
st.write("")

page = st.radio("Pilih halaman", ["📊 Ringkasan", "❌ Pembatalan", "🛏️ Tipe Kamar", "👥 Lama Menginap & Kalender"], horizontal=True, label_visibility="collapsed")
st.write("")

if page.startswith("📊"):
    answer(f"Dari potensi pendapatan <b>{jt(total)}</b>, sebesar <b>{jt(lost)}</b> ({lost/total*100:.1f}%) hilang karena booking dibatalkan.")
    title("Potensi pendapatan: berapa yang terealisasi dan berapa yang hilang?", "Satuan: juta rupiah")
    fig = go.Figure()
    fig.add_bar(y=[""], x=[ok["revenue"].sum() / 1e6], orientation="h", marker_color=GREEN, text=[f"Terealisasi {ok['revenue'].sum()/1e6:,.0f} jt"], textposition="inside")
    fig.add_bar(y=[""], x=[lost / 1e6], orientation="h", marker_color=RED, text=[f"Hilang {lost/1e6:,.0f} jt"], textposition="inside")
    fig.update_layout(barmode="stack"); fig.update_xaxes(title="Juta rupiah")
    st.plotly_chart(dark(fig, 190), width="stretch")
    title("Pendapatan terealisasi per bulan", "Satuan: juta rupiah, berdasarkan bulan check-in")
    m = ok.groupby("month", as_index=False)["revenue"].sum(); m["jt"] = m["revenue"] / 1e6
    fig = px.bar(m, x="month", y="jt", text=m["jt"].round(0).astype(int).astype(str), color_discrete_sequence=[GOLD], labels={"month": "Bulan", "jt": "Juta rupiah"})
    fig.update_traces(textposition="outside", marker_cornerradius=6)
    st.plotly_chart(dark(fig, 340), width="stretch")

elif page.startswith("❌"):
    ch = f.groupby("booking_channel").agg(booking=("booking_id", "size"), batal=("cancelled", "mean"), hilang=("potential", lambda s: s[f.loc[s.index, "cancelled"]].sum())).reset_index()
    ch["batal"] *= 100; ch["hilang_jt"] = ch["hilang"] / 1e6
    worst = ch.sort_values("batal").iloc[-1]; big = ch.sort_values("hilang").iloc[-1]
    answer(f"Channel dengan pembatalan tertinggi adalah <b>{worst['booking_channel']}</b> ({worst['batal']:.1f}%). Kerugian rupiah terbesar juga datang dari <b>{big['booking_channel']}</b> ({big['hilang_jt']:,.0f} juta).")
    a, b = st.columns(2)
    with a:
        title("Berapa persen booking yang dibatalkan, per channel?", "Makin panjang = makin sering dibatalkan")
        d = ch.sort_values("batal")
        fig = px.bar(d, x="batal", y="booking_channel", orientation="h", text=d["batal"].round(1).astype(str) + "%", color_discrete_sequence=[RED], labels={"batal": "% dibatalkan", "booking_channel": ""})
        fig.update_traces(textposition="outside", marker_cornerradius=6)
        st.plotly_chart(dark(fig, 340), width="stretch")
    with b:
        title("Berapa pendapatan yang hilang, per channel?", "Satuan: juta rupiah")
        d = ch.sort_values("hilang_jt")
        fig = px.bar(d, x="hilang_jt", y="booking_channel", orientation="h", text=d["hilang_jt"].round(0).astype(int).astype(str), color_discrete_sequence=[GOLD], labels={"hilang_jt": "Juta rupiah", "booking_channel": ""})
        fig.update_traces(textposition="outside", marker_cornerradius=6)
        st.plotly_chart(dark(fig, 340), width="stretch")
    title("Persentase pembatalan per bulan", "Apakah pembatalan makin parah atau stabil?")
    cm = f.groupby("month", as_index=False)["cancelled"].mean(); cm["pct"] = cm["cancelled"] * 100
    fig = px.line(cm, x="month", y="pct", markers=True, text=cm["pct"].round(1).astype(str) + "%", color_discrete_sequence=[RED], labels={"month": "Bulan", "pct": "% dibatalkan"})
    fig.update_traces(textposition="top center"); fig.update_yaxes(range=[0, 16])
    st.plotly_chart(dark(fig, 300), width="stretch")

elif page.startswith("🛏️"):
    room = ok.groupby("room_type").agg(rev=("revenue", "sum"), tarif=("nightly_rate", "mean")).reset_index(); room["jt"] = room["rev"] / 1e6
    top = room.sort_values("rev").iloc[-1]
    answer(f"Tipe kamar dengan pendapatan terbesar adalah <b>{top['room_type']}</b> ({top['jt']:,.0f} juta). Kamar termahal per malam: <b>{room.sort_values('tarif').iloc[-1]['room_type']}</b>.")
    a, b = st.columns(2)
    with a:
        title("Pendapatan per tipe kamar", "Satuan: juta rupiah")
        d = room.sort_values("jt")
        fig = px.bar(d, x="jt", y="room_type", orientation="h", text=d["jt"].round(0).astype(int).astype(str), color_discrete_sequence=[GOLD], labels={"jt": "Juta rupiah", "room_type": ""})
        fig.update_traces(textposition="outside", marker_cornerradius=6)
        st.plotly_chart(dark(fig, 320), width="stretch")
    with b:
        title("Tarif rata-rata per malam", "Satuan: ribu rupiah")
        d = room.assign(rb=room["tarif"] / 1e3).sort_values("rb")
        fig = px.bar(d, x="rb", y="room_type", orientation="h", text=d["rb"].round(0).astype(int).astype(str), color_discrete_sequence=[GREEN], labels={"rb": "Ribu rupiah", "room_type": ""})
        fig.update_traces(textposition="outside", marker_cornerradius=6)
        st.plotly_chart(dark(fig, 320), width="stretch")
    title("Kombinasi kamar dan channel mana yang paling sering dibatalkan?", "Angka = % booking dibatalkan. Makin merah = makin berisiko.")
    g = f[f["booking_channel"] != "Unknown"]
    cr = (g.pivot_table(index="room_type", columns="booking_channel", values="cancelled", aggfunc="mean") * 100).round(1)
    fig = px.imshow(cr, text_auto=True, aspect="auto", color_continuous_scale=[GREEN, GOLD, RED], labels=dict(x="Channel", y="Kamar", color="% batal"))
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(dark(fig, 340), width="stretch")
    st.caption("Catatan (seluruh periode): Suite lewat Website hampir tidak pernah dibatalkan (±1,7%), sedangkan Suite lewat Online Travel Agent ±12,7%.")

else:
    long_ = ok[ok["nights"] >= 5]
    answer(f"Booking yang menginap <b>5 malam atau lebih</b> hanya {len(long_)/len(ok)*100:.1f}% dari total booking, tetapi menyumbang <b>{long_['revenue'].sum()/ok['revenue'].sum()*100:.1f}%</b> pendapatan.")
    a, b = st.columns(2)
    with a:
        title("Berapa booking untuk tiap lama menginap?", "Sumbu bawah = jumlah malam")
        n = f.groupby("nights", as_index=False).size()
        fig = px.bar(n, x="nights", y="size", text="size", color_discrete_sequence=[GOLD], labels={"nights": "Malam", "size": "Jumlah booking"})
        fig.update_traces(textposition="outside", marker_cornerradius=6)
        st.plotly_chart(dark(fig, 320), width="stretch")
    with b:
        title("Berapa pendapatan per booking?", "Satuan: juta rupiah")
        r = ok.groupby("nights", as_index=False)["revenue"].mean(); r["jt"] = r["revenue"] / 1e6
        fig = px.line(r, x="nights", y="jt", markers=True, color_discrete_sequence=[GREEN], labels={"nights": "Malam", "jt": "Juta rupiah per booking"})
        st.plotly_chart(dark(fig, 320), width="stretch")
    title("Kapan tamu paling banyak check-in?", "Angka = jumlah check-in. Makin terang = makin ramai.")
    hm = f.pivot_table(index="dow", columns="month", values="booking_id", aggfunc="count", fill_value=0).reindex(DAYS)
    hm.index = DAYS_ID
    fig = px.imshow(hm, text_auto=True, aspect="auto", color_continuous_scale=[PANEL, GOLD], labels=dict(x="Bulan", y="", color="Check-in"))
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(dark(fig, 380), width="stretch")
    st.caption("Check-in memuncak di Jumat dan Sabtu, tetapi tarif rata-rata dua hari itu hanya ±4% lebih tinggi dari hari lain.")

with st.expander("📋 Lihat data booking"):
    st.dataframe(f.drop(columns=["month", "dow", "cancelled", "potential"]), width="stretch")
