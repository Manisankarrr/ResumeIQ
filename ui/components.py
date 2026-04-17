import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_kpi_row(results, jd_skills):
    col1, col2, col3, col4 = st.columns(4)
    if not results:
        col1.metric("Top Score", "0%")
        col2.metric("Avg Score", "0%")
        col3.metric("Shortlisted", 0)
        col4.metric("JD Skills", len(jd_skills))
        return
        
    scores = [r.score for r in results]
    top_score = max(scores)
    avg_score = sum(scores) / len(scores)
    shortlisted = sum(1 for s in scores if s >= 0.70)
    
    col1.metric("Top Score", f"{top_score:.0%}")
    col2.metric("Avg Score", f"{avg_score:.0%}")
    col3.metric("Shortlisted", shortlisted)
    col4.metric("JD Skills", len(jd_skills))

def render_score_ranking(results):
    sorted_results = sorted(results, key=lambda x: x.score)
    names = [r.candidate_name for r in sorted_results]
    scores = [r.score for r in sorted_results]
    
    colors = []
    for s in scores:
        if s >= 0.7:
            colors.append("#3B6D11")
        elif s >= 0.4:
            colors.append("#BA7517")
        else:
            colors.append("#E24B4A")
            
    fig = go.Figure(go.Bar(
        x=scores,
        y=names,
        orientation='h',
        marker_color=colors
    ))
    
    fig.add_vline(x=0.70, line_dash="dash", line_color="gray")
    fig.update_layout(
        xaxis=dict(showgrid=False, range=[0, 1], tickformat=".0%"),
        yaxis=dict(showgrid=False),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return fig

def render_candidate_card(result, rank):
    label = f"#{rank} {result.candidate_name} — {result.score:.0%}"
    with st.expander(label):
        # Progress bound safely between 0-1
        safe_score = max(0.0, min(1.0, float(result.score)))
        st.progress(safe_score)
        
        col_left, col_right = st.columns(2)
        with col_left:
            st.write("**Matched skills**")
            html_matched = "".join(
                [f'<span style="background-color:#3B6D11; color:white; padding: 2px 8px; border-radius:12px; margin-right:4px; margin-bottom:4px; display:inline-block; font-size:0.8rem;">{str(s)}</span>' for s in result.matched_skills]
            )
            if html_matched:
                st.markdown(html_matched, unsafe_allow_html=True)
            else:
                st.write("None")
                
        with col_right:
            st.write("**Missing skills**")
            html_missing = "".join(
                [f'<span style="background-color:#E24B4A; color:white; padding: 2px 8px; border-radius:12px; margin-right:4px; margin-bottom:4px; display:inline-block; font-size:0.8rem;">{str(s)}</span>' for s in result.missing_skills]
            )
            if html_missing:
                st.markdown(html_missing, unsafe_allow_html=True)
            else:
                st.write("None")
            
        st.write("---")
        c1, c2, c3, c4 = st.columns(4)
        
        total_extracted_jd = len(result.matched_skills) + len(result.missing_skills)
        c1.metric("Skills matched", f"{len(result.matched_skills)}/{total_extracted_jd}")
        c2.metric("Similarity score", f"{result.score:.3f}")
        c3.metric("Skills extracted", len(result.matched_skills) + len(result.missing_skills))
        
        if result.score >= 0.7:
            verdict = "Shortlist"
        elif result.score >= 0.4:
            verdict = "Maybe"
        else:
            verdict = "Reject"
            
        c4.metric("Verdict", verdict)

def render_skill_matrix(results, jd_skills):
    if not results or not jd_skills:
        st.write("No sufficient data to build a matrix.")
        return
        
    data = {}
    for skill in jd_skills:
        data[skill] = {}
        for r in results:
            data[skill][r.candidate_name] = "Yes" if skill in r.matched_skills else "No"
            
    df = pd.DataFrame(data).T
    
    coverage = {}
    for r in results:
        matched_count = sum(1 for s in jd_skills if s in r.matched_skills)
        cov_pct = f"{matched_count / len(jd_skills):.0%}"
        coverage[r.candidate_name] = cov_pct
        
    df.loc["Coverage %"] = pd.Series(coverage)
    
    def style_cells(val):
        if val == "Yes":
            return 'color: #3B6D11; font-weight: bold'
        elif val == "No":
            return 'color: #E24B4A; font-weight: bold'
        return ''
        
    styled_df = df.style.map(style_cells)
    
    st.dataframe(styled_df, use_container_width=True)

def render_gap_alert(results, jd_skills):
    if not results or not jd_skills:
        return
        
    universal_gaps = []
    for skill in jd_skills:
        missing_everywhere = all(skill not in r.matched_skills for r in results)
        if missing_everywhere:
            universal_gaps.append(skill)
            
    if universal_gaps:
        gaps_str = ', '.join(universal_gaps)
        st.warning(f"These skills are missing from every candidate: {gaps_str}. Consider whether they are truly required or can be trained on the job.")

def render_common_skills_heatmap(results, jd_skills):
    skill_counts = []
    for skill in jd_skills:
        count = sum(1 for r in results if skill in r.matched_skills)
        skill_counts.append((skill, count))
        
    skill_counts.sort(key=lambda x: x[1])
    
    skills = [x[0] for x in skill_counts]
    counts = [x[1] for x in skill_counts]
    
    total_candidates = len(results)
    colors = []
    for c in counts:
        if c == total_candidates and total_candidates > 0:
            colors.append("#3B6D11")
        elif c == 0:
            colors.append("#E24B4A")
        else:
            colors.append("#BA7517")
            
    fig = go.Figure(go.Bar(
        x=counts,
        y=skills,
        orientation='h',
        marker_color=colors
    ))
    
    fig.update_layout(
        title="Skill coverage across candidates",
        xaxis=dict(showgrid=False, dtick=1),
        yaxis=dict(showgrid=False),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
