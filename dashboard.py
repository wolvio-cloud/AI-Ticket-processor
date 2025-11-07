# dashboard.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from dashboard_utils import DashboardData, calculate_roi

# Page config
st.set_page_config(
    page_title="AI Ticket Processor Dashboard",
    page_icon="🎫",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .success { color: #00cc00; }
    .warning { color: #ff9900; }
    .danger { color: #ff0000; }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("🎫 AI Ticket Processor - Live Dashboard")
st.markdown("---")

# Load data
@st.cache_data(ttl=60)  # Cache for 1 minute
def load_data(days=7):
    data = DashboardData()
    return {
        'metrics': data.calculate_metrics(days),
        'categories': data.get_category_breakdown(days),
        'sentiment': data.get_sentiment_breakdown(days),
        'urgency': data.get_urgency_breakdown(days),
        'recent': data.get_recent_tickets(10)
    }

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    days = st.slider("Days to display", 1, 30, 7)
    st.markdown("---")
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **AI Ticket Processor v2.2**
    
    Automated ticket triage using AI
    
    - 99.1% time savings
    - 100% success rate
    - 3.5 sec/ticket
    """)

# Load data
data = load_data(days)
metrics = data['metrics']

# Top metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 Tickets Processed",
        value=f"{metrics['total_processed']:,}",
        delta=f"Last {days} days"
    )

with col2:
    success_rate = metrics['success_rate']
    st.metric(
        label="✅ Success Rate",
        value=f"{success_rate:.1f}%",
        delta="Target: 99.5%",
        delta_color="normal" if success_rate >= 99 else "inverse"
    )

with col3:
    avg_time = metrics['avg_time']
    st.metric(
        label="⚡ Avg Time",
        value=f"{avg_time:.1f}s",
        delta="Target: <10s",
        delta_color="normal" if avg_time < 10 else "inverse"
    )

with col4:
    st.metric(
        label="💰 Total Cost",
        value=f"${metrics['total_cost']:.2f}",
        delta=f"${metrics['total_cost']/metrics['total_processed']*1000:.3f}/1k tickets" if metrics['total_processed'] > 0 else "N/A"
    )

st.markdown("---")

# Charts row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Category Breakdown")
    
    if data['categories']:
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=list(data['categories'].keys()),
            values=list(data['categories'].values()),
            hole=.3
        )])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available")

with col2:
    st.subheader("😊 Sentiment Analysis")
    
    if data['sentiment']:
        # Color mapping
        colors = {
            'positive': '#00cc00',
            'neutral': '#999999',
            'negative': '#ff0000'
        }
        
        sentiment_data = data['sentiment']
        total = sum(sentiment_data.values())
        
        # Create horizontal bar chart
        fig = go.Figure(data=[
            go.Bar(
                y=list(sentiment_data.keys()),
                x=list(sentiment_data.values()),
                orientation='h',
                marker_color=[colors.get(k, '#666') for k in sentiment_data.keys()],
                text=[f"{v} ({v/total*100:.0f}%)" for v in sentiment_data.values()],
                textposition='auto',
            )
        ])
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Alert if high negative sentiment
        negative_pct = sentiment_data.get('negative', 0) / total * 100 if total > 0 else 0
        if negative_pct > 20:
            st.warning(f"⚠️ High negative sentiment: {negative_pct:.0f}% - Potential churn risk!")
    else:
        st.info("No data available")

st.markdown("---")

# Charts row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚡ Urgency Distribution")
    
    if data['urgency']:
        urgency_data = data['urgency']
        total = sum(urgency_data.values())
        
        # Create horizontal bar chart
        fig = go.Figure(data=[
            go.Bar(
                y=list(urgency_data.keys()),
                x=list(urgency_data.values()),
                orientation='h',
                marker_color=['#ff0000', '#ff9900', '#00cc00'],  # high, medium, low
                text=[f"{v} ({v/total*100:.0f}%)" for v in urgency_data.values()],
                textposition='auto',
            )
        ])
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Alert if many high-urgency tickets
        high_count = urgency_data.get('high', 0)
        if high_count > 5:
            st.warning(f"⚠️ {high_count} high-urgency tickets need attention!")
    else:
        st.info("No data available")

with col2:
    st.subheader("💰 ROI Calculator")
    
    tickets_per_month = st.number_input(
        "Tickets per month",
        min_value=100,
        max_value=10000,
        value=1200,
        step=100
    )
    
    roi = calculate_roi(tickets_per_month)
    
    st.markdown(f"""
    **Manual Processing:**
    - Time: {roi['manual_hours']} hours/month
    - Cost: ${roi['manual_cost']:,.2f}/month
    
    **AI Processing:**
    - Time: {roi['ai_hours']} hours/month
    - Cost: ${roi['ai_total_cost']:,.2f}/month
    
    ---
    
    **💰 Monthly Savings: ${roi['monthly_savings']:,.2f}**
    
    **💰 Annual Savings: ${roi['annual_savings']:,.2f}**
    
    **📅 Break-even: {roi['breakeven_months']:.1f} months**
    """)

st.markdown("---")

# Recent tickets table
st.subheader("📋 Recent Tickets")

if not data['recent'].empty:
    df = data['recent'].copy()
    
    # Format columns
    df['ticket_id'] = df['ticket_id'].astype(str)
    df['processing_time'] = df['processing_time'].apply(lambda x: f"{x:.1f}s")
    
    # Rename columns for display
    df = df.rename(columns={
        'ticket_id': 'Ticket #',
        'category': 'Category',
        'urgency': 'Urgency',
        'sentiment': 'Sentiment',
        'processing_time': 'Time',
        'summary': 'Summary'
    })
    
    # Display table
    st.dataframe(
        df[['Ticket #', 'Category', 'Urgency', 'Sentiment', 'Time', 'Summary']],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No recent tickets to display. Process some tickets first!")

st.markdown("---")

# Footer
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Export CSV"):
        if not data['recent'].empty:
            csv = data['recent'].to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"tickets_{days}days.csv",
                mime="text/csv"
            )
        else:
            st.warning("No data to export")

with col2:
    st.markdown(f"**Last updated:** {st.session_state.get('last_update', 'Never')}")

with col3:
    st.markdown("**Status:** 🟢 Operational")