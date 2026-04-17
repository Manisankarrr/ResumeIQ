def get_colors(dark: bool) -> dict:
    """Return hardcoded theme colors based on the mode."""
    if not dark:
        return {
            "bg": "#ffffff",
            "bg2": "#f8f8f6",
            "bg3": "#f0f0ec",
            "bg4": "#eceae3",
            "text": "#111110",
            "text2": "#5c5b57",
            "text3": "#999890",
            "border": "rgba(0,0,0,.09)",
            "border2": "rgba(0,0,0,.14)",
            "accent": "#534AB7",
            "accent_bg": "#EEEDFE",
            "green": "#27500A",
            "green_bg": "#EAF3DE",
            "green_bar": "#639922",
            "red": "#791F1F",
            "red_bg": "#FCEBEB",
            "red_bar": "#E24B4A",
            "amber": "#633806",
            "amber_bg": "#FAEEDA",
            "amber_bar": "#BA7517",
        }
    else:
        return {
            "bg": "#141413",
            "bg2": "#1e1e1c",
            "bg3": "#282826",
            "bg4": "#2a2a27",
            "text": "#eeecea",
            "text2": "#9e9c96",
            "text3": "#65635e",
            "border": "rgba(255,255,255,.08)",
            "border2": "rgba(255,255,255,.13)",
            "accent": "#7F77DD",
            "accent_bg": "#26215C",
            "green": "#C0DD97",
            "green_bg": "#173404",
            "green_bar": "#639922",
            "red": "#F7C1C1",
            "red_bg": "#501313",
            "red_bar": "#E24B4A",
            "amber": "#FAC775",
            "amber_bg": "#412402",
            "amber_bar": "#BA7517",
        }

def score_color(score: float, c: dict) -> tuple[str, str]:
    """Returns (text_color, bg_color) based on score."""
    if score >= 0.70:
        return (c["green"], c["green_bg"])
    elif score >= 0.40:
        return (c["amber"], c["amber_bg"])
    else:
        return (c["red"], c["red_bg"])

def verdict_label(score: float) -> str:
    """Returns verdict string based on score."""
    if score >= 0.70:
        return "Shortlist"
    elif score >= 0.40:
        return "Maybe"
    else:
        return "Reject"

def build_metrics_html(results: list, jd_skills: list[str], dark: bool) -> str:
    """Builds the 4 main metrics as HTML to allow strict color control."""
    c = get_colors(dark)
    if not results:
        return ""
    
    top_candidate = max(results, key=lambda x: getattr(x, 'score', 0.0), default=None)
    top_score = getattr(top_candidate, 'score', 0.0) if top_candidate else 0.0
    top_name = getattr(top_candidate, 'candidate_name', 'None') if top_candidate else 'None'
    
    avg_score = sum(getattr(r, 'score', 0.0) for r in results) / len(results) if results else 0.0
    shortlisted = sum(1 for r in results if getattr(r, 'score', 0.0) >= 0.7)
    
    html = f"""
    <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:16px; margin-bottom:24px; font-family:'Inter', system-ui, sans-serif;">
      
      <!-- Top Score -->
      <div style="background:{c['bg3']}; border:1px solid {c['border']}; border-radius:12px; padding:12px 16px;">
        <div style="font-size:10px; font-weight:600; color:{c['text3']}; text-transform:uppercase; letter-spacing:.07em; margin-bottom:4px;">Top score</div>
        <div style="font-size:24px; font-weight:700; color:{c['green']}; line-height:1.2;">{top_score*100:.0f}%</div>
        <div style="font-size:13px; font-weight:400; color:{c['text2']}; margin-top:4px;">{top_name}</div>
      </div>
      
      <!-- Avg Score -->
      <div style="background:{c['bg3']}; border:1px solid {c['border']}; border-radius:12px; padding:12px 16px;">
        <div style="font-size:10px; font-weight:600; color:{c['text3']}; text-transform:uppercase; letter-spacing:.07em; margin-bottom:4px;">Avg score</div>
        <div style="font-size:24px; font-weight:700; color:{c['text']}; line-height:1.2;">{avg_score*100:.0f}%</div>
        <div style="font-size:13px; font-weight:400; color:{c['text2']}; margin-top:4px;">across {len(results)} candidates</div>
      </div>
      
      <!-- Shortlisted -->
      <div style="background:{c['bg3']}; border:1px solid {c['border']}; border-radius:12px; padding:12px 16px;">
        <div style="font-size:10px; font-weight:600; color:{c['text3']}; text-transform:uppercase; letter-spacing:.07em; margin-bottom:4px;">Shortlisted</div>
        <div style="font-size:24px; font-weight:700; color:{c['amber']}; line-height:1.2;">{shortlisted} / {len(results)}</div>
        <div style="font-size:13px; font-weight:400; color:{c['text2']}; margin-top:4px;">score &ge; 70%</div>
      </div>
      
      <!-- JD Skills -->
      <div style="background:{c['bg3']}; border:1px solid {c['border']}; border-radius:12px; padding:12px 16px;">
        <div style="font-size:10px; font-weight:600; color:{c['text3']}; text-transform:uppercase; letter-spacing:.07em; margin-bottom:4px;">JD skills found</div>
        <div style="font-size:24px; font-weight:700; color:{c['text']}; line-height:1.2;">{len(jd_skills)}</div>
        <div style="font-size:13px; font-weight:400; color:{c['text2']}; margin-top:4px;">required skills</div>
      </div>
    </div>
    """
    return html

def build_candidate_card_html(result, rank: int, jd_skills: list[str], dark: bool) -> str:
    """Builds and returns a full HTML string for one candidate card."""
    c = get_colors(dark)
    score = getattr(result, "score", 0.0)
    name = getattr(result, "candidate_name", "Unknown")
    matched = getattr(result, "matched_skills", [])
    missing = getattr(result, "missing_skills", [])
    
    t_color, b_color = score_color(score, c)
    verdict = verdict_label(score)
    
    parts = name.split()
    initials = "".join([p[0].upper() for p in parts if p])[:2] if parts else "?"
    
    total_skills = len(jd_skills) if jd_skills else (len(matched) + len(missing))
    if total_skills == 0:
        total_skills = 1
    match_pct = min(100.0, (len(matched) / total_skills) * 100.0)
    
    matched_html = "".join([
        f'<span style="font-size:11px; font-weight:500; padding:3px 11px; border-radius:20px; background:{c["green_bg"]}; color:{c["green"]}; margin:0 6px 6px 0; display:inline-block;">{s}</span>'
        for s in matched
    ])
    missing_html = "".join([
        f'<span style="font-size:11px; font-weight:500; padding:3px 11px; border-radius:20px; background:{c["red_bg"]}; color:{c["red"]}; margin:0 6px 6px 0; display:inline-block;">{s}</span>'
        for s in missing
    ])
    
    html = f"""
    <div style="border-radius:14px; border:1px solid {c['border']}; background:{c['bg']}; padding:16px 18px; margin-bottom:12px; font-family:'Inter', system-ui, sans-serif;">
      
      <div style="display:flex; align-items:center; gap:12px;">
        <div style="width:38px; height:38px; border-radius:50%; background:{c['accent_bg']}; color:{c['accent']}; font-weight:600; font-size:13px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
          {initials}
        </div>
        <div>
          <div style="font-size:14px; font-weight:600; color:{c['text']}; line-height:1.2;">{name}</div>
          <div style="font-size:13px; font-weight:400; color:{c['text3']}; margin-top:2px;">Rank #{rank} &middot; {name}</div>
        </div>
        
        <div style="margin-left:auto; display:flex; align-items:center; gap:8px;">
          <span style="font-size:13px; font-weight:700; background:{b_color}; color:{t_color}; padding:4px 12px; border-radius:20px;">
            {score * 100:.0f}%
          </span>
          <span style="font-size:10px; font-weight:700; letter-spacing:0.06em; background:{b_color}; color:{t_color}; padding:3px 10px; border-radius:4px; text-transform:uppercase;">
            {verdict}
          </span>
        </div>
      </div>
      
      <div style="margin-top:14px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:400; color:{c['text2']}; margin-bottom:6px;">
          <span>Skill fit</span>
          <span>{len(matched)}/{total_skills} skills</span>
        </div>
        <div style="height:8px; background:{c['bg4']}; border-radius:4px; overflow:hidden;">
          <div style="width:{match_pct}%; height:8px; background:{c['green_bar'] if score >= 0.7 else c['amber_bar'] if score >= 0.4 else c['red_bar']}; border-radius:4px;"></div>
        </div>
      </div>
      
      <div style="margin-top:14px; display:flex; gap:14px; flex-wrap:wrap;">
        <div style="flex:1; min-width:200px;">
          <div style="font-size:10px; font-weight:600; color:{c['text3']}; text-transform:uppercase; letter-spacing:.07em; margin-bottom:6px;">Matched skills</div>
          <div style="display:flex; flex-wrap:wrap;">
            {matched_html if matched_html else f'<span style="font-size:13px; font-weight:400; color:{c["text3"]};">None</span>'}
          </div>
        </div>
        <div style="flex:1; min-width:200px;">
          <div style="font-size:10px; font-weight:600; color:{c['text3']}; text-transform:uppercase; letter-spacing:.07em; margin-bottom:6px;">Missing skills</div>
          <div style="display:flex; flex-wrap:wrap;">
            {missing_html if missing_html else f'<span style="font-size:13px; font-weight:400; color:{c["text3"]};">None</span>'}
          </div>
        </div>
      </div>
      
      <div style="margin-top:14px; display:grid; grid-template-columns:repeat(4, 1fr); gap:10px;">
        <div style="background:{c['bg2']}; border-radius:8px; padding:8px 10px;">
          <div style="font-size:10px; font-weight:600; color:{c['text3']}; text-transform:uppercase; letter-spacing:.07em;">Matched</div>
          <div style="font-size:13px; font-weight:400; line-height:1.6; color:{c['text2']}; margin-top:2px;">{len(matched)}</div>
        </div>
        <div style="background:{c['bg2']}; border-radius:8px; padding:8px 10px;">
          <div style="font-size:10px; font-weight:600; color:{c['text3']}; text-transform:uppercase; letter-spacing:.07em;">Missing</div>
          <div style="font-size:13px; font-weight:400; line-height:1.6; color:{c['text2']}; margin-top:2px;">{len(missing)}</div>
        </div>
        <div style="background:{c['bg2']}; border-radius:8px; padding:8px 10px;">
          <div style="font-size:10px; font-weight:600; color:{c['text3']}; text-transform:uppercase; letter-spacing:.07em;">Similarity</div>
          <div style="font-size:13px; font-weight:400; line-height:1.6; color:{c['text2']}; margin-top:2px;">{score:.3f}</div>
        </div>
        <div style="background:{c['bg2']}; border-radius:8px; padding:8px 10px;">
          <div style="font-size:10px; font-weight:600; color:{c['text3']}; text-transform:uppercase; letter-spacing:.07em;">Verdict</div>
          <div style="font-size:13px; font-weight:400; line-height:1.6; color:{c['text2']}; margin-top:2px;">{verdict}</div>
        </div>
      </div>
      
    </div>
    """
    return html

def build_ranking_chart_html(results: list, dark: bool) -> str:
    """Builds a pure HTML/CSS ranking chart matching the design specs."""
    c = get_colors(dark)
    
    # Sort descending so highest rank (1) is at top
    sorted_results = sorted(results, key=lambda x: getattr(x, 'score', 0.0), reverse=True)
    
    html = f"""
    <div style="background:{c['bg2']}; border-radius:14px; padding:18px 20px; font-family:'Inter', system-ui, sans-serif; width:100%; box-sizing:border-box;">
      <div style="font-size:12px; font-weight:600; color:{c['text2']}; letter-spacing:.02em; margin-bottom:14px;">Score ranking</div>
      
      <div style="position:relative; width:100%;">
    """
    
    for rank0, res in enumerate(sorted_results):
        rank = rank0 + 1
        score = getattr(res, "score", 0.0)
        name = getattr(res, "candidate_name", "Unknown")
        
        if score >= 0.70:
            bar_color = c["green_bar"]
            text_color = c["green"]
        elif score >= 0.40:
            bar_color = c["amber_bar"]
            text_color = c["amber"]
        else:
            bar_color = c["red_bar"]
            text_color = c["red"]
            
        html += f"""
        <div style="display:flex; align-items:center; gap:0; margin-bottom:10px; position:relative;">
          <div style="width:96px; flex-shrink:0; text-align:right; padding-right:12px; font-size:12px; font-weight:500; color:{c['text']}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; box-sizing:border-box;">
            #{rank} {name}
          </div>
          <div style="flex:1; position:relative; height:32px;">
            <div style="position:absolute; top:50%; transform:translateY(-50%); left:0; right:0; height:10px; border-radius:5px; background:{c['bg4']};"></div>
            <div style="position:absolute; top:50%; transform:translateY(-50%); left:0; height:10px; border-radius:5px; transition:width .5s ease; width:{score*100:.1f}%; background:{bar_color};"></div>
            <span style="position:absolute; top:50%; transform:translateY(-50%); left:{score*100+1:.1f}%; font-size:11px; font-weight:700; color:{text_color}; pointer-events:none;">{score:.0%}</span>
          </div>
        </div>
        """
        
    # Threshold line as absolute overlay
    html += f"""
        <div style="position:absolute; top:0; bottom:0; left:0; right:0; display:flex; pointer-events:none;">
          <div style="width:96px; flex-shrink:0;"></div>
          <div style="flex:1; position:relative;">
            <div style="position:absolute; top:-20px; bottom:8px; left:70%; width:1.5px; border-left:1.5px dashed {c['text3']}; opacity:0.35;"></div>
            <div style="position:absolute; top:-30px; left:70%; transform:translateX(-50%); font-size:9px; font-weight:600; color:{c['text3']}; text-transform:uppercase; letter-spacing:.05em; white-space:nowrap;">70%</div>
          </div>
        </div>
      </div>
      
      <div style="display:flex; gap:14px; margin-top:10px;">
        <div style="font-size:10px; color:{c['text3']}; display:flex; align-items:center; gap:4px;">
          <div style="width:10px; height:10px; border-radius:50%; background:{c['green_bar']};"></div>
          Shortlist &ge;70%
        </div>
        <div style="font-size:10px; color:{c['text3']}; display:flex; align-items:center; gap:4px;">
          <div style="width:10px; height:10px; border-radius:50%; background:{c['amber_bar']};"></div>
          Maybe 40&ndash;69%
        </div>
        <div style="font-size:10px; color:{c['text3']}; display:flex; align-items:center; gap:4px;">
          <div style="width:10px; height:10px; border-radius:50%; background:{c['red_bar']};"></div>
          Reject &lt;40%
        </div>
      </div>
    </div>
    """
    return html

def build_skill_matrix_html(results: list, jd_skills: list[str], dark: bool) -> str:
    """Builds an HTML table string acting as a skills matrix."""
    c = get_colors(dark)
    
    html = f'<div style="border-radius:14px; border:1px solid {c["border"]}; background:{c["bg"]}; overflow:hidden; font-family:\'Inter\', system-ui, sans-serif;">'
    html += f'<table style="width:100%; border-collapse:collapse; font-size:13px; font-weight:400; color:{c["text2"]}; text-align:left; line-height:1.6;">'
    
    # Header
    html += f'<tr style="background:{c["bg3"]}; color:{c["text"]}; font-weight:600; font-size:13px; border-bottom:1px solid {c["border"]};">'
    html += f'<th style="padding:10px 14px;">Skill</th>'
    for res in results:
        name = getattr(res, "candidate_name", "Unknown")
        parts = name.split()
        initials = "".join([p[0].upper() for p in parts])[:2] if parts else name[:2].upper()
        html += f'<th style="padding:10px 14px; text-align:center;" title="{name}">{initials}</th>'
    html += '</tr>'
    
    # Rows
    for i, skill in enumerate(jd_skills):
        row_bg = c["bg"] if i % 2 == 0 else c["bg4"]
        html += f'<tr style="background:{row_bg}; border-bottom:1px solid {c["border"]};">'
        html += f'<td style="padding:9px 14px; font-weight:400; color:{c["text2"]};">{skill}</td>'
        
        for res in results:
            matched = getattr(res, "matched_skills", [])
            has_skill = skill in matched
            if has_skill:
                circle = f'<div style="background:{c["green_bg"]}; color:{c["green"]}; padding:3px 11px; border-radius:20px; font-size:11px; font-weight:500; display:inline-block; text-align:center;">Yes</div>'
            else:
                circle = f'<div style="background:{c["red_bg"]}; color:{c["red"]}; padding:3px 11px; border-radius:20px; font-size:11px; font-weight:500; display:inline-block; text-align:center;">No</div>'
            html += f'<td style="padding:9px 14px; text-align:center;">{circle}</td>'
        html += '</tr>'
        
    # Footer
    html += f'<tr style="background:{c["bg3"]}; color:{c["accent"]}; font-weight:600; font-size:13px;">'
    html += f'<td style="padding:10px 14px;">Coverage %</td>'
    for res in results:
        matched = getattr(res, "matched_skills", [])
        jd_match_count = sum(1 for s in jd_skills if s in matched)
        total = len(jd_skills) if jd_skills else 1
        html += f'<td style="padding:10px 14px; text-align:center;">{jd_match_count}/{total}</td>'
    html += '</tr>'
        
    html += '</table></div>'
    return html
