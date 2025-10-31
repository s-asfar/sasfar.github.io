import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from collections import Counter

pio.templates.default = "plotly_white"

pokemon_types = {
    'Great Tusk': ['Ground', 'Fighting'], 'Kingambit': ['Dark', 'Steel'],
    'Gholdengo': ['Steel', 'Ghost'], 'Dragonite': ['Dragon', 'Flying'],
    'Dragapult': ['Dragon', 'Ghost'], 'Ogerpon-Wellspring': ['Grass', 'Water'],
    'Iron Valiant': ['Fairy', 'Fighting'], 'Raging Bolt': ['Electric', 'Dragon'],
    'Zamazenta': ['Fighting', 'Steel'], 'Slowking-Galar': ['Poison', 'Psychic'],
    'Landorus-Therian': ['Ground', 'Flying'], 'Hatterene': ['Psychic', 'Fairy'],
    'Corviknight': ['Flying', 'Steel'], 'Gliscor': ['Ground', 'Flying'],
    'Cinderace': ['Fire', None], 'Iron Moth': ['Fire', 'Poison'],
    'Ting-Lu': ['Dark', 'Ground'], 'Iron Treads': ['Ground', 'Steel'],
    'Samurott-Hisui': ['Water', 'Dark'], 'Ceruledge': ['Fire', 'Ghost']
}

type_colors = {
    'Steel': '#B8B8D0', 'Dark': '#705848', 'Ground': '#E0C068',
    'Ghost': '#705898', 'Dragon': '#7038F8', 'Fighting': '#C03028',
    'Water': '#6890F0', 'Fairy': '#EE99AC', 'Flying': '#A890F0',
    'Grass': '#78C850', 'Fire': '#F08030', 'Poison': '#A040A0',
    'Psychic': '#F85888', 'Electric': '#F8D030', 'Rock': '#B8A038',
    'Ice': '#98D8D8', 'Bug': '#A8B820', 'Normal': '#A8A878'
}

def parse_smogon_data(filepath):
    """Parse the Smogon usage stats text file"""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                if '|' not in line or 'Rank' in line or '+-' in line:
                    continue
                parts = line.split('|')
                if len(parts) > 4:
                    try:
                        rank = int(parts[1].strip())
                        name = parts[2].strip()
                        usage_str = parts[3].strip()
                        usage_pct = float(usage_str.rstrip('%'))
                        data.append({
                            'rank': rank,
                            'name': name,
                            'usage_percent': usage_pct
                        })
                    except (ValueError, IndexError):
                        continue
    except FileNotFoundError:
        print(f"Error: Data file '{filepath}' not found.")
        print("Please download the file from the URL in your report and place it in this directory.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
        
    return pd.DataFrame(data)

df = parse_smogon_data('gen9ou-0.txt')

if df is not None and not df.empty:
    df['cumulative_percent'] = df['usage_percent'].cumsum() 

    def get_types(name):
        if name in pokemon_types:
            types = pokemon_types[name]
            return types[0], types[1] if types[1] else None
        return None, None

    df[['type1', 'type2']] = df['name'].apply(lambda x: pd.Series(get_types(x)))
    
    print(f"Successfully loaded and processed {len(df)} Pokémon.")

    # --- Visualization 1: The Cliff ---
    fig1 = go.Figure()
    df_top50 = df.iloc[:50]
    fig1.add_trace(go.Scatter(
        x=df_top50['rank'], 
        y=df_top50['usage_percent'],
        mode='lines+markers',
        line=dict(color='#2886AB', width=3),
        marker=dict(size=5),
        fill='tozeroy',
        fillcolor='rgba(40, 134, 171, 0.2)',
        name='Usage',
        hovertext=df_top50['name'],
        hovertemplate='<b>%{hovertext}</b><br>Rank: %{x}<br>Usage: %{y:.1f}%<extra></extra>'
    ))
    fig1.add_annotation(
        x=1, y=df.iloc[0]['usage_percent'],
        text=f"<b>#1: {df.iloc[0]['usage_percent']:.1f}%</b><br>{df.iloc[0]['name']}",
        showarrow=True, arrowhead=2, arrowcolor='#AB2C28', ax=50, ay=-70,
        font=dict(color="#AB2C28", size=12, family="Lato, sans-serif")
    )
    fig1.add_annotation(
        x=10, y=df.iloc[9]['usage_percent'],
        text=f"<b>#10: {df.iloc[9]['usage_percent']:.1f}%</b><br>{df.iloc[9]['name']}",
        showarrow=True, arrowhead=2, arrowcolor="#AB2C28", ax=50, ay=-50,
        font=dict(color='#AB2C28', size=12, family="Lato, sans-serif")
    )
    fig1.update_layout(
        title=None,
        xaxis_title="Pokémon Popularity Rank",
        yaxis_title="Team Usage Rate (%)",
        margin=dict(t=20, b=40, l=40, r=20),
        font=dict(family="Lato, sans-serif"),
        hovermode="x unified"
    )
    fig1.write_html("plot1.html", include_plotlyjs='cdn', full_html=False)
    print("Generated plot1.html")

    # --- Visualization 2: The Top 20 (with Type Colors) ---
    top_20 = df.head(20).copy()
    
    fig2 = go.Figure()
    
    for i, row in top_20.iterrows():
        color1 = type_colors.get(row['type1'], '#808080')
        
        if pd.notna(row['type2']):
            color2 = type_colors.get(row['type2'], '#808080')
            
            color2_rgb = tuple(int(color2.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            color2_rgba = f'rgba({color2_rgb[0]}, {color2_rgb[1]}, {color2_rgb[2]}, 0.5)'
            
            fig2.add_trace(go.Bar(
                x=[row['name']],
                y=[row['usage_percent']],
                marker=dict(
                    color=color1,
                    line=dict(color=color2_rgba, width=4)
                ),
                text=[round(row['usage_percent'], 1)],
                textposition='outside',
                textfont=dict(family="Lato, sans-serif", size=10, color='black'),
                hovertemplate=f'<b>{row["name"]}</b><br>Usage: {row["usage_percent"]:.1f}%<br>Type: {row["type1"]}/{row["type2"]}<extra></extra>',
                showlegend=False,
                width=0.7
            ))
        else:
            fig2.add_trace(go.Bar(
                x=[row['name']],
                y=[row['usage_percent']],
                marker_color=color1,
                text=[round(row['usage_percent'], 1)],
                textposition='outside',
                textfont=dict(family="Lato, sans-serif", size=10, color='black'),
                hovertemplate=f'<b>{row["name"]}</b><br>Usage: {row["usage_percent"]:.1f}%<br>Type: {row["type1"]}<extra></extra>',
                showlegend=False,
                width=0.7
            ))
    
    fig2.update_layout(
        title=None,
        yaxis_title="Usage Rate (%)",
        xaxis_title=None,
        xaxis_tickangle=-45,
        margin=dict(t=30, b=40, l=40, r=20),
        font=dict(family="Lato, sans-serif"),
        yaxis=dict(range=[0, top_20['usage_percent'].max() * 1.15]) 
    )
    fig2.write_html("plot2.html", include_plotlyjs='cdn', full_html=False)
    print("Generated plot2.html")

    # --- Visualization 3: Cumulative Usage Curve (Simplified) ---
    fig3 = go.Figure()
    df_top150 = df.iloc[:150]
    
    fig3.add_trace(go.Scatter(
        x=df_top150['rank'], 
        y=df_top150['cumulative_percent'],
        mode='lines',
        line=dict(color='#3498db', width=3),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.1)',
        name='Cumulative Usage',
        hovertemplate='<b>Top %{x} Pokémon</b><br>Account for %{y:.1f}% of all usage<extra></extra>'
    ))
    
    for pct in [25, 50, 75]:
        fig3.add_hline(
            y=pct, 
            line_dash="dot", 
            line_color="rgba(150, 150, 150, 0.3)",
            line_width=1
        )
    
    fig3.update_layout(
        title=None,
        xaxis_title="Number of Pokémon (by Rank)",
        yaxis_title="Cumulative Usage (%)",
        margin=dict(t=20, b=40, l=40, r=20),
        font=dict(family="Lato, sans-serif", size=12),
        plot_bgcolor='white',
        yaxis=dict(
            gridcolor='rgba(230, 230, 230, 0.5)',
            range=[0, 100],
            ticksuffix="%",
            dtick=50,
            fixedrange=False
        ),
        xaxis=dict(
            gridcolor='rgba(230, 230, 230, 0.5)',
            range=[0, 150],
            fixedrange=False
        ),
        showlegend=False,
        autosize=True
    )
    fig3.write_html("plot3.html", include_plotlyjs='cdn', full_html=False, config={'displayModeBar': True, 'displaylogo': False})
    print("Generated plot3.html")

    # --- Visualization 4: Type Distribution ---
    type_counts = Counter()
    for _, row in df.head(50).iterrows(): 
        if pd.notna(row['type1']):
            type_counts[row['type1']] += 1 
        if pd.notna(row['type2']):
            type_counts[row['type2']] += 1 

    sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True) 
    types, counts = zip(*sorted_types)
    colors = [type_colors.get(t, '#808080') for t in types] 

    fig4 = go.Figure(go.Bar(
        x=types,
        y=counts,
        marker_color=colors,
        text=counts,
        textposition='outside',
        textfont=dict(family="Lato, sans-serif", size=10, color='black'),
        hovertemplate='<b>%{x}</b><br>Appearances: %{y}<extra></extra>'
    ))
    fig4.update_layout(
        title=None,
        yaxis_title="Appearances in Top 50",
        xaxis_title="Pokémon Type",
        margin=dict(t=30, b=40, l=40, r=20),
        font=dict(family="Lato, sans-serif"),
        yaxis=dict(range=[0, max(counts) * 1.15]) 
    )
    fig4.write_html("plot4.html", include_plotlyjs='cdn', full_html=False)
    print("Generated plot4.html")

    # --- Visualization 5: Usage Tiers ---
    usage_tiers = [
        ('Elite (>10%)', len(df[df['usage_percent'] >= 10]), '#FF4444'), 
        ('High (5-10%)', len(df[(df['usage_percent'] >= 5) & (df['usage_percent'] < 10)]), '#FF8844'), 
        ('Medium (2-5%)', len(df[(df['usage_percent'] >= 2) & (df['usage_percent'] < 5)]), '#FFCC44'), 
        ('Low (1-2%)', len(df[(df['usage_percent'] >= 1) & (df['usage_percent'] < 2)]), '#B0B0B0'),
        ('Rare (<1%)', len(df[df['usage_percent'] < 1]), '#606060')
    ]
    labels, values, colors = zip(*usage_tiers)

    fig5 = go.Figure(go.Bar(
        y=labels,
        x=values,
        orientation='h',
        marker_color=colors,
        text=values,
        textposition='outside',
        textfont=dict(family="Lato, sans-serif", size=12, color='black'),
        hovertemplate='<b>%{y}</b><br>Pokémon: %{x}<extra></extra>'
    ))
    fig5.update_layout(
        title=None,
        xaxis_title="Number of Pokémon",
        yaxis_title=None,
        yaxis=dict(autorange="reversed"),
        xaxis=dict(range=[0, max(values) * 1.15]), 
        margin=dict(t=20, b=40, l=40, r=20),
        font=dict(family="Lato, sans-serif")
    )
    fig5.write_html("plot5.html", include_plotlyjs='cdn', full_html=False)
    print("Generated plot5.html")
    print("\nAll plots generated successfully!")

else:
    print("\nScript terminated because data file could not be loaded.")