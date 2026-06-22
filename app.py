import streamlit as st
import plotly.graph_objects as go
from data_fetch import get_ohlcv, get_support_resistance
from ai_brain import chat
from memory import get_memory_summary, load_memory, save_memory
from journal import load_journal, save_journal, add_trade, get_journal_summary

st.set_page_config(page_title="Trading Mentor", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Trading Mentor")

col1, col2 = st.columns([2, 1])

with col1:
    symbol = st.text_input("Symbol", value="BTC/USDT")
    timeframe = st.selectbox("Timeframe", ["15m", "1h", "4h", "1d"], index=1)
    show_sr = st.checkbox("Show Support & Resistance", value=True)
    try:
        df = get_ohlcv(symbol, timeframe)
        fig = go.Figure(data=[go.Candlestick(
            x=df["timestamp"], open=df["open"], high=df["high"],
            low=df["low"], close=df["close"]
        )])
        if show_sr:
            levels = get_support_resistance(df)
            for s in levels["support"]:
                fig.add_hline(y=s, line_dash="dash", line_color="green", line_width=1,
                    annotation_text=f"S {s}", annotation_position="left",
                    annotation_font_color="green")
            for r in levels["resistance"]:
                fig.add_hline(y=r, line_dash="dash", line_color="red", line_width=1,
                    annotation_text=f"R {r}", annotation_position="left",
                    annotation_font_color="red")
        journal = load_journal()
        for trade in journal:
            if trade["symbol"] == symbol.upper():
                color = "green" if trade["direction"] == "long" else "red"
                fig.add_hline(y=trade["entry"], line_dash="solid", line_color=color,
                    line_width=2, annotation_text=f"{trade['direction'].upper()} entry",
                    annotation_position="right")
                fig.add_hline(y=trade["exit"], line_dash="dot", line_color="white",
                    line_width=1, annotation_text=f"Exit PnL:{trade['pnl']}",
                    annotation_position="right")
        fig.update_layout(height=600, xaxis_rangeslider_visible=False,
            paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
        if show_sr:
            st.caption(f"Support: {levels['support']} | Resistance: {levels['resistance']}")
    except Exception as e:
        st.error(f"Couldn't load chart data: {e}")

with col2:
    tab1, tab2, tab3 = st.tabs(["Chat", "My Strategy", "Journal"])

    with tab1:
        st.subheader("Ask your mentor")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        user_input = st.chat_input("Ask about this chart or your strategy...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    if show_sr:
                        levels = get_support_resistance(df)
                        context = f"{user_input}\n\nChart levels — Support: {levels['support']} Resistance: {levels['resistance']}"
                    else:
                        context = user_input
                    msgs = st.session_state.messages[:-1] + [{"role": "user", "content": context}]
                    reply = chat(msgs, symbol)
                    st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

    with tab2:
        st.subheader("Your Strategy Memory")
        memory = load_memory()
        st.markdown("**Your Trading Rules:**")
        if memory["rules"]:
            for i, rule in enumerate(memory["rules"]):
                col_a, col_b = st.columns([5, 1])
                with col_a:
                    st.write(f"• {rule}")
                with col_b:
                    if st.button("X", key=f"del_{i}"):
                        memory["rules"].remove(rule)
                        save_memory(memory)
                        st.rerun()
        else:
            st.write("No rules saved yet - just chat and mention your strategy!")
        st.markdown("---")
        new_rule = st.text_input("Add a rule manually:")
        if st.button("Add Rule"):
            if new_rule:
                memory["rules"].append(new_rule)
                save_memory(memory)
                st.rerun()

    with tab3:
        st.subheader("Trade Journal")
        with st.expander("Log a new trade"):
            t_symbol = st.text_input("Symbol", value="BTC/USDT", key="t_symbol")
            t_direction = st.selectbox("Direction", ["long", "short"])
            t_entry = st.number_input("Entry Price", value=0.0)
            t_exit = st.number_input("Exit Price", value=0.0)
            t_size = st.number_input("Size (units)", value=1.0)
            t_notes = st.text_area("Notes")
            if st.button("Save Trade"):
                if t_entry > 0 and t_exit > 0:
                    trade = add_trade(t_symbol, t_direction, t_entry, t_exit, t_size, t_notes)
                    st.success(f"Trade saved! PnL: {trade['pnl']}")
                    st.rerun()
                else:
                    st.warning("Please enter valid entry and exit prices.")
        st.markdown("---")
        st.markdown("**Past Trades:**")