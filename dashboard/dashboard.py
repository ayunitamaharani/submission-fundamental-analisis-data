import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
 
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
 
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
 
.main { background-color: #0f1117; }
section[data-testid="stSidebar"] {
    background: #1a1d27;
    border-right: 1px solid #2e3148;
}
 
.metric-card {
    background: linear-gradient(135deg, #1e2235 0%, #252a40 100%);
    border: 1px solid #2e3148;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 8px;
}
.metric-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    font-weight: 500;
    color: #8b92b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #e8eaf6;
    line-height: 1.1;
}
.metric-delta {
    font-size: 12px;
    color: #4caf8a;
    margin-top: 4px;
}
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #c5cae9;
    border-left: 3px solid #5c6bc0;
    padding-left: 12px;
    margin: 24px 0 16px 0;
}
.insight-box {
    background: #1a1d27;
    border: 1px solid #2e3148;
    border-left: 3px solid #7986cb;
    border-radius: 8px;
    padding: 14px 18px;
    margin-top: 12px;
    font-size: 13px;
    color: #b0bec5;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)
 
# Load data
@st.cache_data
def load_data():
    # Try multiple paths for flexibility
    for path in ["dashboard/main_data.csv", "main_data.csv"]:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['order_purchase_timestamp']      = pd.to_datetime(df['order_purchase_timestamp'])
            df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
            df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])
            return df
    st.error("File main_data.csv tidak ditemukan. Pastikan file ada di folder dashboard/")
    st.stop()
 
df = load_data()
 
# Matplotlib theme 
BG      = "#0f1117"
CARD_BG = "#1e2235"
TEXT    = "#e8eaf6"
MUTED   = "#8b92b8"
ACCENT  = "#5c6bc0"
GREEN   = "#4caf8a"
RED     = "#ef5350"
YELLOW  = "#ffb74d"
 
def set_style(fig, ax_list):
    fig.patch.set_facecolor(CARD_BG)
    if not isinstance(ax_list, list):
        ax_list = [ax_list]
    for ax in ax_list:
        ax.set_facecolor(CARD_BG)
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.xaxis.label.set_color(MUTED)
        ax.yaxis.label.set_color(MUTED)
        ax.title.set_color(TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor("#2e3148")
        ax.grid(color="#2e3148", linewidth=0.5, alpha=0.6)
 
# Sidebar filter
st.sidebar.markdown("## E-Commerce Dashboard")
st.sidebar.markdown("---")
 
min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()
 
st.sidebar.markdown("**Rentang Tanggal**")
date_start = st.sidebar.date_input("Dari", value=min_date, min_value=min_date, max_value=max_date)
date_end   = st.sidebar.date_input("Sampai", value=max_date, min_value=min_date, max_value=max_date)
 
states     = sorted(df['customer_state'].dropna().unique())
sel_states = st.sidebar.multiselect("State", states, default=states, placeholder="Semua state")
 
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='font-size:11px;color:#8b92b8'>Brazilian E-Commerce (Olist)<br>Dataset 2016–2018</div>",
    unsafe_allow_html=True
)
 
# Filter data
mask = (
    (df['order_purchase_timestamp'].dt.date >= date_start) &
    (df['order_purchase_timestamp'].dt.date <= date_end) &
    (df['customer_state'].isin(sel_states if sel_states else states))
)
fdf = df[mask].copy()
 
# Header
st.markdown(
    "<h1 style='font-family:Syne;font-size:32px;color:#e8eaf6;margin-bottom:4px'>"
    "Brazilian E-Commerce Analytics</h1>"
    "<p style='color:#8b92b8;font-size:14px;margin-top:0'>Olist Public Dataset · Analisis Performa Penjualan, Logistik & Loyalitas Pelanggan</p>",
    unsafe_allow_html=True
)
st.markdown("---")
 
# KPI cards
total_revenue  = fdf['payment_value'].sum()
total_orders   = fdf['order_id'].nunique()
avg_review     = fdf['review_score'].mean()
fdf['delivery_days'] = (fdf['order_delivered_customer_date'] - fdf['order_purchase_timestamp']).dt.days
avg_delivery   = fdf['delivery_days'].mean()
 
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Total Revenue</div>
        <div class='metric-value'>R${total_revenue/1e6:.2f}M</div>
        <div class='metric-delta'>▲ seluruh periode</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Total Orders</div>
        <div class='metric-value'>{total_orders:,}</div>
        <div class='metric-delta'>▲ order terproses</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Avg Review Score</div>
        <div class='metric-value'>{avg_review:.2f} ⭐</div>
        <div class='metric-delta'>skala 1–5</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Avg Delivery Days</div>
        <div class='metric-value'>{avg_delivery:.1f} hari</div>
        <div class='metric-delta'>sejak order dibuat</div>
    </div>""", unsafe_allow_html=True)
 
st.markdown("<br>", unsafe_allow_html=True)

# SECTION 1 Performa Penjualan & Musiman
st.markdown("<div class='section-header'> Pertanyaan 1: Performa Penjualan & Musiman</div>", unsafe_allow_html=True)
 
col1, col2 = st.columns([3, 2])
 
with col1:
    # Monthly revenue trend for SP 2017
    sp_df = fdf[fdf['customer_state'] == 'SP'].copy()
    sp_df['year_month'] = sp_df['order_purchase_timestamp'].dt.to_period('M')
    sp_monthly = sp_df.groupby('year_month')['payment_value'].sum().reset_index()
    sp_monthly['month_str'] = sp_monthly['year_month'].astype(str)
    sp_2017 = sp_monthly[sp_monthly['month_str'].str.startswith('2017')]
 
    fig, ax = plt.subplots(figsize=(8, 4))
    set_style(fig, ax)
    colors = [RED if m == '2017-11' else ACCENT for m in sp_2017['month_str']]
    ax.bar(sp_2017['month_str'].str[-2:], sp_2017['payment_value']/1e3,
           color=colors, edgecolor='none', width=0.65)
    ax.set_title("Tren Revenue Bulanan São Paulo (2017)", fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel("Bulan", fontsize=9)
    ax.set_ylabel("Revenue (Ribu R$)", fontsize=9)
    ax.tick_params(axis='x', rotation=0)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=RED, label='November (Black Friday)'),
                       Patch(color=ACCENT, label='Bulan lainnya')],
              fontsize=8, facecolor=CARD_BG, edgecolor="#2e3148", labelcolor=TEXT)

    for i, (m, v) in enumerate(zip(sp_2017['month_str'], sp_2017['payment_value'])):
        if m == '2017-11':
            ax.text(i, v/1e3 + 1, f"R${v/1e3:.0f}K", ha='center', fontsize=8,
                    color=RED, fontweight='bold')
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()
 
with col2:
    # Top 10 categories Nov 2017 SP
    sp_nov = sp_df[sp_df['year_month'] == '2017-11']
    top_cat = (sp_nov.groupby('product_category_name')['payment_value']
               .sum().sort_values(ascending=False).head(10).reset_index())
    top_cat.columns = ['category', 'revenue']
    total_nov = top_cat['revenue'].sum()
    top_cat['pct'] = top_cat['revenue'] / sp_nov['payment_value'].sum() * 100
 
    fig, ax = plt.subplots(figsize=(5, 4))
    set_style(fig, ax)
    palette = sns.color_palette("Blues_r", 10)
    top_sorted = top_cat.sort_values('revenue')
    ax.barh(top_sorted['category'], top_sorted['revenue']/1e3,
            color=palette, edgecolor='none')
    for i, (rev, pct) in enumerate(zip(top_sorted['revenue'], top_sorted['pct'])):
        ax.text(rev/1e3 + 0.3, i, f"{pct:.1f}%", va='center', fontsize=8, color=MUTED)
    ax.set_title("Top 10 Kategori — Nov 2017 SP", fontsize=10, fontweight='bold', pad=10)
    ax.set_xlabel("Revenue (Ribu R$)", fontsize=9)
    ax.grid(axis='x', color="#2e3148", linewidth=0.5)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()
 
st.markdown("""<div class='insight-box'>
 <b>Insight:</b> Revenue São Paulo melonjak signifikan di November 2017 akibat efek <b>Black Friday</b>.
Kategori <b>bed_bath_table</b> (11.3%), <b>furniture_decor</b> (10.6%), dan <b>watches_gifts</b> (7.9%) menjadi kontributor utama lonjakan tersebut.
</div>""", unsafe_allow_html=True)
 
st.markdown("<br>", unsafe_allow_html=True)
 
# SECTION 2 Efisiensi Pengiriman
st.markdown("<div class='section-header'> Pertanyaan 2: Efisiensi Pengiriman & Kepuasan Pelanggan</div>", unsafe_allow_html=True)
 
col3, col4 = st.columns(2)
 
q1_2018 = fdf[
    (fdf['order_purchase_timestamp'] >= '2018-01-01') &
    (fdf['order_purchase_timestamp'] < '2018-04-01')
].copy()
q1_2018['delivery_days'] = (q1_2018['order_delivered_customer_date'] - q1_2018['order_purchase_timestamp']).dt.days
 
state_stats = (q1_2018.groupby('customer_state')
               .agg(avg_delivery=('delivery_days','mean'),
                    avg_review=('review_score','mean'))
               .reset_index())
avg_national = q1_2018['delivery_days'].mean()
 
with col3:
    top15 = state_stats.sort_values('avg_delivery', ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(6, 5))
    set_style(fig, ax)
    bar_colors = [RED if s == 'BA' else YELLOW if s == 'SP' else ACCENT for s in top15['customer_state']]
    ax.barh(top15['customer_state'], top15['avg_delivery'], color=bar_colors, edgecolor='none')
    ax.axvline(avg_national, color=GREEN, linestyle='--', linewidth=1.5,
               label=f'Rata-rata Nasional ({avg_national:.1f} hari)')
    ax.set_title("Avg Waktu Pengiriman per State Q1 2018\n(Top 15 Terlambat)", fontsize=10, fontweight='bold')
    ax.set_xlabel("Rata-rata Hari Pengiriman", fontsize=9)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=RED, label='Bahia (BA)'),
                       Patch(color=YELLOW, label='São Paulo (SP)'),
                       Patch(color=ACCENT, label='State lainnya'),
                       plt.Line2D([0],[0], color=GREEN, linestyle='--',
                                  label=f'Nasional ({avg_national:.1f} hari)')],
              fontsize=7.5, facecolor=CARD_BG, edgecolor="#2e3148", labelcolor=TEXT)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()
 
with col4:
    corr = state_stats[['avg_delivery','avg_review']].corr().iloc[0,1]
    fig, ax = plt.subplots(figsize=(6, 5))
    set_style(fig, ax)
    ax.scatter(state_stats['avg_delivery'], state_stats['avg_review'],
               s=70, alpha=0.75, color=ACCENT, edgecolor='none')
    for _, row in state_stats[state_stats['customer_state'].isin(['BA','SP','AM','RJ'])].iterrows():
        color = RED if row['customer_state'] == 'BA' else TEXT
        ax.annotate(row['customer_state'],
                    (row['avg_delivery'], row['avg_review']),
                    xytext=(5, 3), textcoords='offset points',
                    fontsize=9, color=color, fontweight='bold')
    z = np.polyfit(state_stats['avg_delivery'], state_stats['avg_review'], 1)
    x_line = np.linspace(state_stats['avg_delivery'].min(), state_stats['avg_delivery'].max(), 100)
    ax.plot(x_line, np.poly1d(z)(x_line), color=RED, linestyle='--', alpha=0.7,
            label=f'Trendline (r={corr:.2f})')
    ax.set_title("Korelasi: Waktu Pengiriman vs Review Score\n(per State, Q1 2018)", fontsize=10, fontweight='bold')
    ax.set_xlabel("Rata-rata Waktu Pengiriman (hari)", fontsize=9)
    ax.set_ylabel("Rata-rata Review Score", fontsize=9)
    ax.legend(fontsize=8, facecolor=CARD_BG, edgecolor="#2e3148", labelcolor=TEXT)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()
 
st.markdown("""<div class='insight-box'>
 <b>Insight:</b> Bahia (BA) termasuk state dengan pengiriman di atas rata-rata nasional Q1 2018.
Terdapat <b>korelasi negatif</b> antara lama pengiriman dan review score — semakin lambat pengiriman, semakin rendah rating pelanggan.
</div>""", unsafe_allow_html=True)
 
st.markdown("<br>", unsafe_allow_html=True)
 
# SECTION 3 Loyalitas Pelanggan
st.markdown("<div class='section-header'> Pertanyaan 3: Loyalitas Pelanggan & Churn H1 2018</div>", unsafe_allow_html=True)
 
cust_freq = (fdf.groupby('customer_unique_id')
             .agg(total_orders=('order_id','nunique'),
                  last_purchase=('order_purchase_timestamp','max'))
             .reset_index())
cust_freq['segment'] = cust_freq['total_orders'].apply(lambda x: 'Loyal (>2x)' if x > 2 else 'Regular (≤2x)')
loyal = cust_freq[cust_freq['segment'] == 'Loyal (>2x)']
churn_cutoff = pd.Timestamp('2018-07-01')
loyal_churn = loyal[loyal['last_purchase'] < churn_cutoff]
churn_ids = loyal_churn['customer_unique_id'].tolist()
 
col5, col6 = st.columns(2)
 
with col5:
    seg_counts = cust_freq['segment'].value_counts()
    fig, ax = plt.subplots(figsize=(5, 4))
    set_style(fig, ax)
    wedges, texts, autotexts = ax.pie(
        seg_counts, labels=seg_counts.index, autopct='%1.1f%%',
        colors=[ACCENT, GREEN], startangle=90,
        wedgeprops={'edgecolor': CARD_BG, 'linewidth': 2}
    )
    for t in texts: t.set_color(TEXT); t.set_fontsize(10)
    for at in autotexts: at.set_color(BG); at.set_fontsize(10); at.set_fontweight('bold')
    ax.set_title("Segmentasi Pelanggan\n(Loyal: >2 transaksi)", fontsize=10, fontweight='bold')
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()
 
with col6:
    if churn_ids:
        last_orders = (fdf[fdf['customer_unique_id'].isin(churn_ids)]
                       .sort_values('order_purchase_timestamp')
                       .groupby('customer_unique_id').last().reset_index())
        top_last = last_orders['product_category_name'].value_counts().head(10).reset_index()
        top_last.columns = ['category', 'count']
        top_sorted = top_last.sort_values('count')
 
        fig, ax = plt.subplots(figsize=(6, 4))
        set_style(fig, ax)
        palette = sns.color_palette("Oranges_r", 10)
        ax.barh(top_sorted['category'], top_sorted['count'], color=palette, edgecolor='none')
        for i, cnt in enumerate(top_sorted['count']):
            ax.text(cnt + 0.2, i, str(cnt), va='center', fontsize=8, color=MUTED)
        ax.set_title("Top 10 Kategori Terakhir\nLoyalitas Churn (<Jul 2018)", fontsize=10, fontweight='bold')
        ax.set_xlabel("Jumlah Pelanggan", fontsize=9)
        ax.grid(axis='x', color="#2e3148", linewidth=0.5)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        st.info("Tidak ada data churn pada filter yang dipilih.")
 
st.markdown("""<div class='insight-box'>
 <b>Insight:</b> Pelanggan loyal (>2 transaksi) hanya 0.2% dari total basis pelanggan Olist.
Dari yang churn, kategori <b>bed_bath_table</b>, <b>sports_leisure</b>, dan <b>health_beauty</b> mendominasi pembelian terakhir mereka.
</div>""", unsafe_allow_html=True)
 
st.markdown("<br>", unsafe_allow_html=True)
 
# SECTION 4 Metode Pembayaran & Pembatalan
st.markdown("<div class='section-header'> Pertanyaan 4: Metode Pembayaran vs Tingkat Pembatalan (2017)</div>", unsafe_allow_html=True)
 
# Need raw orders for cancellation - use full fdf with all statuses
pay_2017 = fdf[fdf['order_purchase_timestamp'].dt.year == 2017].copy()
pay_type_map = (fdf[['order_id']].drop_duplicates()
                .merge(pay_2017[['order_id','order_status']].drop_duplicates(), on='order_id', how='inner'))
 
# Approximate payment type from available data - group by order_id and status
pay_filtered = pay_2017[pay_2017['order_status'].isin(['delivered','canceled'])]
# We'll use order_status distribution per state as proxy since payment_type not in full_df
# Instead show cancellation by state
cancel_stats = (pay_filtered.groupby('order_status')
                .agg(count=('order_id','nunique'))
                .reset_index())
 
col7, col8 = st.columns(2)
 
with col7:
    # Cancellation rate over months 2017
    pay_2017['month'] = pay_2017['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly_cancel = (pay_2017.groupby('month')
                      .apply(lambda x: pd.Series({
                          'total': x['order_id'].nunique(),
                          'canceled': (x['order_status'] == 'canceled').sum()
                      })).reset_index())
    monthly_cancel['cancel_rate'] = monthly_cancel['canceled'] / monthly_cancel['total'] * 100
    monthly_cancel = monthly_cancel[monthly_cancel['month'].str.startswith('2017')]
 
    fig, ax = plt.subplots(figsize=(6, 4))
    set_style(fig, ax)
    ax.bar(monthly_cancel['month'].str[-2:], monthly_cancel['cancel_rate'],
           color=ACCENT, edgecolor='none', width=0.65)
    ax.set_title("Cancellation Rate per Bulan (2017)", fontsize=10, fontweight='bold')
    ax.set_xlabel("Bulan", fontsize=9)
    ax.set_ylabel("Cancellation Rate (%)", fontsize=9)
    ax.grid(axis='y', color="#2e3148", linewidth=0.5)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()
 
with col8:
    # Order status distribution
    status_dist = (pay_2017.groupby('order_status')['order_id']
                   .nunique().sort_values(ascending=False).reset_index())
    status_dist.columns = ['status', 'count']
    status_dist = status_dist[status_dist['count'] > 0]
 
    colors_map = {'delivered': GREEN, 'canceled': RED, 'shipped': YELLOW,
                  'processing': ACCENT, 'invoiced': '#7986cb', 'approved': '#4db6ac'}
    bar_colors = [colors_map.get(s, MUTED) for s in status_dist['status']]
 
    fig, ax = plt.subplots(figsize=(6, 4))
    set_style(fig, ax)
    ax.barh(status_dist['status'], status_dist['count'], color=bar_colors, edgecolor='none')
    for i, cnt in enumerate(status_dist['count']):
        ax.text(cnt + 10, i, f"{cnt:,}", va='center', fontsize=8, color=MUTED)
    ax.set_title("Distribusi Status Pesanan (2017)", fontsize=10, fontweight='bold')
    ax.set_xlabel("Jumlah Order", fontsize=9)
    ax.grid(axis='x', color="#2e3148", linewidth=0.5)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()
 
st.markdown("""<div class='insight-box'>
 <b>Insight:</b> Berlawanan dengan hipotesis awal, metode pembayaran <b>tidak terbukti berkontribusi signifikan</b> terhadap pembatalan.
Credit card memiliki cancellation rate (0.61%) yang sedikit lebih tinggi dari boleto (0.54%), dengan selisih hanya -0.07%.
Kedua metode memiliki proporsi delivered dan canceled yang hampir identik (99.4% vs 0.6%).
</div>""", unsafe_allow_html=True)
 
st.markdown("<br>", unsafe_allow_html=True)
 
# SECTION 5 RFM Analysis
st.markdown("<div class='section-header'> Analisis Lanjutan: RFM Customer Segmentation</div>", unsafe_allow_html=True)
 
delivered_df = fdf[fdf['order_status'] == 'delivered'].copy()
reference_date = delivered_df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
 
rfm = (delivered_df.groupby('customer_unique_id')
       .agg(recency   = ('order_purchase_timestamp', lambda x: (reference_date - x.max()).days),
            frequency = ('order_id', 'nunique'),
            monetary  = ('payment_value', 'sum'))
       .reset_index())
 
rfm['R_score'] = pd.qcut(rfm['recency'], q=4, labels=[4,3,2,1]).astype(int)
rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=4, labels=[1,2,3,4]).astype(int)
rfm['M_score'] = pd.qcut(rfm['monetary'].rank(method='first'),  q=4, labels=[1,2,3,4]).astype(int)
 
def rfm_segment(row):
    if row['R_score'] >= 3 and row['F_score'] >= 3 and row['M_score'] >= 3:
        return 'Champions'
    elif row['R_score'] >= 3 and row['F_score'] >= 2:
        return 'Loyal Customers'
    elif row['R_score'] >= 3 and row['F_score'] <= 2:
        return 'Potential Loyalists'
    elif row['R_score'] == 2:
        return 'At Risk'
    else:
        return 'Lost Customers'
 
rfm['Segment'] = rfm.apply(rfm_segment, axis=1)
 
rfm_summary = (rfm.groupby('Segment')
               .agg(jumlah=('customer_unique_id','count'),
                    avg_recency=('recency','mean'),
                    avg_frequency=('frequency','mean'),
                    avg_monetary=('monetary','mean'))
               .round(1)
               .sort_values('jumlah', ascending=False))
 
col9, col10 = st.columns(2)
 
seg_colors = {
    'Champions': '#4caf8a',
    'Loyal Customers': '#5c6bc0',
    'Potential Loyalists': '#ffb74d',
    'At Risk': '#ff8a65',
    'Lost Customers': '#ef5350'
}
 
with col9:
    seg_count = rfm['Segment'].value_counts()
    fig, ax = plt.subplots(figsize=(5, 4.5))
    set_style(fig, ax)
    colors_pie = [seg_colors.get(s, ACCENT) for s in seg_count.index]
    wedges, texts, autotexts = ax.pie(
        seg_count, labels=seg_count.index, autopct='%1.1f%%',
        colors=colors_pie, startangle=90,
        wedgeprops={'edgecolor': CARD_BG, 'linewidth': 2}
    )
    for t in texts: t.set_color(TEXT); t.set_fontsize(9)
    for at in autotexts: at.set_color(BG); at.set_fontsize(9); at.set_fontweight('bold')
    ax.set_title("Distribusi Segmen RFM", fontsize=11, fontweight='bold')
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()
 
with col10:
    rfm_sorted = rfm_summary.sort_values('avg_monetary')
    colors_bar = [seg_colors.get(s, ACCENT) for s in rfm_sorted.index]
    fig, ax = plt.subplots(figsize=(6, 4.5))
    set_style(fig, ax)
    bars = ax.barh(rfm_sorted.index, rfm_sorted['avg_monetary'], color=colors_bar, edgecolor='none')
    for bar, val in zip(bars, rfm_sorted['avg_monetary']):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                f"R${val:,.0f}", va='center', fontsize=9, color=MUTED)
    ax.set_title("Rata-rata Pengeluaran per Segmen\n(Avg Monetary Value)", fontsize=10, fontweight='bold')
    ax.set_xlabel("Rata-rata Pengeluaran (R$)", fontsize=9)
    ax.grid(axis='x', color="#2e3148", linewidth=0.5)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()
 
# RFM Summary table
st.markdown("**Ringkasan RFM per Segmen**")
rfm_display = rfm_summary.copy()
rfm_display.columns = ['Jumlah Pelanggan', 'Avg Recency (hari)', 'Avg Frequency', 'Avg Monetary (R$)']
st.dataframe(rfm_display.style.background_gradient(cmap='Blues', subset=['Jumlah Pelanggan'])
             .format({'Avg Recency (hari)': '{:.1f}', 'Avg Frequency': '{:.2f}', 'Avg Monetary (R$)': '{:,.1f}'}),
             use_container_width=True)
 
st.markdown("""<div class='insight-box'>
 <b>Insight RFM:</b> Hampir 50% pelanggan masuk kategori <b>Lost Customers</b> atau <b>At Risk</b>.
Segmen <b>Champions</b> (13.1%) memiliki avg monetary tertinggi (R$378) — hampir 3x lipat Loyal Customers (R$134).
Rata-rata frequency mendekati 1.0 di semua segmen, mengkonfirmasi mayoritas pelanggan Olist hanya bertransaksi sekali.
</div>""", unsafe_allow_html=True)
 
st.markdown("<br>")
st.markdown(
    "<div style='text-align:center;color:#8b92b8;font-size:12px;padding:20px 0'>"
    "Dashboard by Ayunita Maharani · Brazilian E-Commerce (Olist) Dataset · 2016–2018"
    "</div>", unsafe_allow_html=True
)