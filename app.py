"""Dashboard Hotel - studi kasus portofolio (dataset simulasi). Tema gelap-mewah, navigasi per halaman."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Hotel Revenue Studio", page_icon="🏨", layout="wide")
GOLD, NAVY, CREAM, MUTED = "#D4AF37", "#0B1220", "#F2E9D0", "#8F9BB3"
rupiah = lambda x: f"Rp {x:,.0f}".replace(",", ".")
juta = lambda x: f"Rp {x/1e6:,.0f} jt".replace(",", ".")
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

st.markdown(f"""<style>
.title {{font-family: Georgia, serif; font-size: 2.3rem; color:{GOLD}; letter-spacing:1px; margin:0;}}
.sub {{color:{MUTED}; margin:0 0 10px 0; letter-spacing:2px; font-size:.8rem; text-transform:uppercase;}}
.card {{border:1px solid {GOLD}55; border-radius:14px; padding:16px 18px; background:linear-gradient(160deg,#16213A,#0E1730);}}
.card .l {{color:{MUTED}; font-size:.75rem; letter-spacing:1.5px; text-transform:uppercase;}}
.card .v {{color:{GOLD}; font-family: Georgia, serif; font-size:1.7rem; white-space:nowrap;}}
.note {{border-left:3px solid {GOLD}; padding:8px 14px; margin:8px 0 14px; color:{CREAM}; background:#16213A;}}
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


def dark(fig, h=380):
    fig.update_layout(template="plotly_dark", height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=10, r=10, t=30, b=10), font=dict(color=CREAM), legend_title_text="")
    return fig


def card(col, label, value):
    col.markdown(f'<div class="card"><div class="l">{label}</div><div class="v">{value}</div></div>', unsafe_allow_html=True)


def note(t):
    st.markdown(f'<div class="note">✦ {t}</div>', unsafe_allow_html=True)


df = load()
st.sidebar.markdown(f"### 🏨 Hotel Revenue Studio")
page = st.sidebar.radio("Halaman", ["1 · Kebocoran Pendapatan", "2 · Kamar × Channel", "3 · Lama Menginap", "4 · Kalender Check-in"])
months = sorted(df["month"].unique())
sel = st.sidebar.multiselect("Bulan", months, default=months)
st.sidebar.caption("Studi kasus portofolio · dataset simulasi\nDibuat oleh Ihsan Amiruddin")
f = df[df["month"].isin(sel)]
if f.empty:
    st.warning("Pilih minimal satu bulan."); st.stop()
ok = f[~f["cancelled"]]
lost = f.loc[f["cancelled"], "potential"].sum()

st.markdown('<p class="title">Hotel Revenue Studio</p><p class="sub">Booking · Pendapatan · Pembatalan — Jan–Jun 2026</p>', unsafe_allow_html=True)
k = st.columns(4)
card(k[0], "Pendapatan terealisasi", juta(ok["revenue"].sum()))
card(k[1], "Pendapatan hilang (batal)", juta(lost))
card(k[2], "Tingkat pembatalan", f"{f['cancelled'].mean()*100:.1f}%")
card(k[3], "Tarif rata-rata / malam", rupiah(ok["nightly_rate"].mean()))
st.write("")

if page.startswith("1"):
    st.subheader("Dari mana pendapatan 'bocor'?")
    a, b = st.columns([3, 2])
    with a:
        total = ok["revenue"].sum() + lost
        fig = go.Figure(go.Waterfall(x=["Potensi pendapatan", "Hilang karena batal", "Terealisasi"], measure=["absolute", "relative", "total"],
                                     y=[total, -lost, 0], text=[juta(total), "-" + juta(lost), juta(total - lost)], textposition="outside",
                                     increasing=dict(marker=dict(color=GOLD)), decreasing=dict(marker=dict(color="#E4572E")), totals=dict(marker=dict(color="#4C9F70"))))
        st.plotly_chart(dark(fig), width="stretch")
    with b:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=f["cancelled"].mean() * 100, number=dict(suffix="%", font=dict(color=GOLD)),
                        title=dict(text="Tingkat pembatalan"), gauge=dict(axis=dict(range=[0, 25]), bar=dict(color=GOLD),
                        steps=[dict(range=[0, 8], color="#1E3A2F"), dict(range=[8, 12], color="#4A3F1A"), dict(range=[12, 25], color="#4A1F1A")])))
        st.plotly_chart(dark(fig), width="stretch")
    c = f.groupby("booking_channel").agg(n=("booking_id", "size"), batal=("cancelled", "mean"), hilang=("potential", lambda s: s[f.loc[s.index, "cancelled"]].sum())).reset_index()
    c["batal"] *= 100
    fig = px.bar(c.sort_values("hilang"), x="hilang", y="booking_channel", orientation="h", color="batal", color_continuous_scale=["#4C9F70", GOLD, "#E4572E"],
                 text=c.sort_values("hilang")["batal"].round(1).astype(str) + "% batal", labels={"hilang": "Pendapatan hilang (Rp)", "booking_channel": "", "batal": "% batal"})
    st.plotly_chart(dark(fig, 320), width="stretch")
    note("Channel OTA menyumbang kerugian terbesar karena volumenya besar dan pembatalannya tertinggi (±13,7%).")

elif page.startswith("2"):
    st.subheader("Kombinasi kamar × channel mana yang paling untung dan paling berisiko?")
    g = f[f["booking_channel"] != "Unknown"]
    a, b = st.columns(2)
    with a:
        rv = g[~g["cancelled"]].pivot_table(index="room_type", columns="booking_channel", values="revenue", aggfunc="sum") / 1e6
        st.markdown("**Pendapatan (juta Rp)**")
        st.plotly_chart(dark(px.imshow(rv.round(0), text_auto=True, aspect="auto", color_continuous_scale=["#16213A", GOLD], labels=dict(color="Juta Rp", x="", y=""))), width="stretch")
    with b:
        cr = g.pivot_table(index="room_type", columns="booking_channel", values="cancelled", aggfunc="mean") * 100
        st.markdown("**Tingkat pembatalan (%)**")
        st.plotly_chart(dark(px.imshow(cr.round(1), text_auto=True, aspect="auto", color_continuous_scale=["#1E3A2F", GOLD, "#E4572E"], labels=dict(color="% batal", x="", y=""))), width="stretch")
    note("OTA unggul di semua tipe kamar. Menariknya, Suite via Website hampir tidak pernah dibatalkan (±1,7%), sedangkan Suite via OTA ±12,7%.")
    st.subheader("Struktur pendapatan")
    s = ok.assign(channel=ok["booking_channel"]).groupby(["room_type", "channel"], as_index=False)["revenue"].sum()
    st.plotly_chart(dark(px.sunburst(s, path=["room_type", "channel"], values="revenue", color_discrete_sequence=px.colors.sequential.YlOrBr_r), 460), width="stretch")

elif page.startswith("3"):
    st.subheader("Apakah tamu yang menginap lebih lama lebih bernilai?")
    n = f.groupby("nights").agg(booking=("booking_id", "size")).reset_index()
    rb = ok.groupby("nights", as_index=False)["revenue"].mean()
    a, b = st.columns(2)
    with a:
        st.plotly_chart(dark(px.bar(n, x="nights", y="booking", color_discrete_sequence=[GOLD], labels={"nights": "Malam", "booking": "Jumlah booking"})), width="stretch")
    with b:
        st.plotly_chart(dark(px.line(rb, x="nights", y="revenue", markers=True, color_discrete_sequence=[GOLD], labels={"nights": "Malam", "revenue": "Pendapatan rata-rata / booking (Rp)"})), width="stretch")
    long_ = ok[ok["nights"] >= 5]
    c = st.columns(3)
    card(c[0], "Booking ≥ 5 malam", f"{len(long_)/len(ok)*100:.1f}% dari booking")
    card(c[1], "Kontribusi pendapatan", f"{long_['revenue'].sum()/ok['revenue'].sum()*100:.1f}%")
    card(c[2], "Rata-rata booking ≥ 5 malam", juta(long_["revenue"].mean()))
    note("Menginap 5 malam atau lebih hanya ±12,6% dari booking, tetapi menyumbang ±27,8% pendapatan. Paket menginap panjang layak didorong.")

else:
    st.subheader("Kapan tamu paling banyak datang?")
    hm = f.pivot_table(index="dow", columns="month", values="booking_id", aggfunc="count", fill_value=0).reindex(DAYS)
    st.plotly_chart(dark(px.imshow(hm, text_auto=True, aspect="auto", color_continuous_scale=["#16213A", GOLD], labels=dict(x="Bulan", y="", color="Check-in")), 420), width="stretch")
    wk = ok.assign(grp=ok["check_in"].dt.dayofweek.isin([4, 5]).map({True: "Jumat–Sabtu", False: "Hari lain"})).groupby("grp", as_index=False)["nightly_rate"].mean()
    a, b = st.columns(2)
    with a:
        st.plotly_chart(dark(px.bar(wk, x="grp", y="nightly_rate", text_auto=",.0f", color_discrete_sequence=[GOLD], labels={"grp": "", "nightly_rate": "Tarif rata-rata / malam (Rp)"}), 320), width="stretch")
    with b:
        mm = f.groupby("month", as_index=False).agg(b=("booking_id", "size"))
        st.plotly_chart(dark(px.line(mm, x="month", y="b", markers=True, color_discrete_sequence=[GOLD], labels={"month": "", "b": "Booking"}), 320), width="stretch")
    note("Check-in memuncak di Jumat–Sabtu, dan tarif rata-rata di dua hari itu hanya ±4% lebih tinggi. Ada ruang untuk harga akhir pekan yang lebih dinamis.")

with st.expander("📋 Data booking"):
    st.dataframe(f.drop(columns=["month", "dow", "cancelled", "potential"]), width="stretch")
