from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import datetime
import json
from urllib.parse import quote_plus


class ReporterAgent(Agent):
    def __init__(self, jid: str, password: str):
        super().__init__(jid, password)

    class ReportBehaviour(CyclicBehaviour):
        def __init__(self):
            super().__init__()
            self.findings = []

        async def run(self):
            msg = await self.receive(timeout=60)
            if msg:
                self.findings.append(msg.body)
                print(f"[ReporterAgent] New finding recorded: {msg.body}")
            else:
                print("[ReporterAgent] No new findings yet.")

            if self.findings:
                await self.generate_report()

        def render_finding_div(self, finding: str) -> str:
            css = "info"
            label = "Info"
            icon = "fa-info-circle"

            if "[XSS]" in finding:
                css, label, icon = "xss", "[XSS]", "fa-bug"
            elif "[Reflection]" in finding:
                css, label, icon = "reflection", "[Reflection]", "fa-code"
            elif "[Auth]" in finding:
                css, label, icon = "auth", "[Auth]", "fa-shield-alt"
            elif "[+]" in finding:
                css, label, icon = "info", "[Info]", "fa-info-circle"

            parts = finding.split(" at: ")
            if len(parts) == 2:
                label = parts[0].strip()
                url = parts[1].strip()
            else:
                url = None

            html = f'<div class="finding {css}">'
            html += f'<div class="finding-icon"><i class="fas {icon}"></i></div>'
            html += '<div class="finding-content">'
            html += f'<strong>{label}</strong>'
            if url:
                html += f'<a href="{url}" target="_blank">{url}</a>'
            else:
                html += f'<p>{finding}</p>'
            html += "</div></div>"
            return html

        async def generate_report(self):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Categorize findings
            categories = {"XSS": [], "Reflection": [], "Auth": [], "Info": []}
            for f in self.findings:
                if "[XSS]" in f:
                    categories["XSS"].append(f)
                elif "[Reflection]" in f:
                    categories["Reflection"].append(f)
                elif "[Auth]" in f:
                    categories["Auth"].append(f)
                else:
                    categories["Info"].append(f)

            # Build dashboard cards
            dashboard_html = ''
            icons = {
                "XSS": "fa-bug",
                "Reflection": "fa-code",
                "Auth": "fa-shield-alt",
                "Info": "fa-info-circle"
            }

            for name, items in categories.items():
                dashboard_html += f'''
<div class="stat-card {name.lower()}">
  <div class="stat-card-inner">
    <div class="stat-icon">
      <i class="fas {icons[name]}"></i>
    </div>
    <div class="stat-details">
      <span class="stat-value">{len(items)}</span>
      <span class="stat-label">{name}</span>
    </div>
  </div>
  <div class="stat-progress" style="width: {min(len(items) * 10, 100)}%"></div>
</div>'''

            # Build findings list
            findings_html = ''
            for cat in ["XSS", "Reflection", "Auth", "Info"]:
                if categories[cat]:
                    findings_html += f'<div class="findings-section"><h3 class="section-title {cat.lower()}-title"><i class="fas {icons[cat]}"></i> {cat} Issues ({len(categories[cat])})</h3>'
                    for f in categories[cat]:
                        findings_html += self.render_finding_div(f)
                    findings_html += '</div>'

            # Prepare chart data
            labels = json.dumps(list(categories.keys()))
            data = json.dumps([len(categories[k]) for k in categories])

            # Assemble HTML
            report_html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Security Assessment Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
  <style>
    :root {{
      --xss-color: #e74c3c;
      --xss-gradient: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
      --reflection-color: #f39c12;
      --reflection-gradient: linear-gradient(135deg, #f39c12 0%, #d35400 100%);
      --auth-color: #3498db;
      --auth-gradient: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
      --info-color: #2ecc71;
      --info-gradient: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);

      --bg-primary: #f8fafc;
      --bg-secondary: #ffffff;
      --text-primary: #1e293b;
      --text-secondary: #64748b;
      --border-color: #e2e8f0;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
      --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
      --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
      --radius-sm: 6px;
      --radius-md: 12px;
      --radius-lg: 16px;
    }}

    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{ 
      font-family: 'Inter', system-ui, -apple-system, sans-serif; 
      background-color: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.5;
    }}

    .container {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 0 24px;
    }}

    header {{
      background: var(--bg-secondary);
      padding: 20px 0;
      box-shadow: var(--shadow-sm);
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--border-color);
    }}

    .header-content {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .logo {{
      display: flex;
      align-items: center;
      gap: 12px;
      color: var(--text-primary);
    }}

    .logo i {{
      font-size: 24px;
      background: linear-gradient(135deg, #3498db, #2ecc71);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    h1 {{
      font-size: 20px;
      font-weight: 600;
    }}

    .timestamp {{
      font-size: 14px;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .timestamp i {{
      font-size: 14px;
    }}

    .dashboard-overview {{
      padding: 32px 0;
    }}

    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 24px;
      margin-bottom: 32px;
    }}

    .stat-card {{
      background: var(--bg-secondary);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-md);
      padding: 24px;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .stat-card:hover {{
      transform: translateY(-5px);
      box-shadow: var(--shadow-lg);
    }}

    .stat-card-inner {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: relative;
      z-index: 2;
    }}

    .stat-icon {{
      width: 56px;
      height: 56px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      color: #fff;
    }}

    .xss .stat-icon {{ background: var(--xss-gradient); }}
    .reflection .stat-icon {{ background: var(--reflection-gradient); }}
    .auth .stat-icon {{ background: var(--auth-gradient); }}
    .info .stat-icon {{ background: var(--info-gradient); }}

    .stat-details {{
      text-align: right;
    }}

    .stat-value {{
      display: block;
      font-size: 36px;
      font-weight: 700;
      line-height: 1;
      margin-bottom: 8px;
    }}

    .stat-label {{
      font-size: 14px;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-secondary);
    }}

    .stat-progress {{
      position: absolute;
      bottom: 0;
      left: 0;
      height: 4px;
      border-radius: 0 2px 2px 0;
    }}

    .xss .stat-progress {{ background: var(--xss-color); }}
    .reflection .stat-progress {{ background: var(--reflection-color); }}
    .auth .stat-progress {{ background: var(--auth-color); }}
    .info .stat-progress {{ background: var(--info-color); }}

    .dashboard-content {{
      display: grid;
      grid-template-columns: 1fr 350px;
      gap: 24px;
    }}

    @media (max-width: 1024px) {{
      .dashboard-content {{
        grid-template-columns: 1fr;
      }}
    }}

    .chart-card {{
      background: var(--bg-secondary);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-md);
      padding: 24px;
    }}

    .chart-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }}

    .chart-title {{
      font-size: 18px;
      font-weight: 600;
    }}

    .chart-container {{
      position: relative;
      margin: 0 auto;
      max-width: 300px;
    }}

    .findings-container {{
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}

    .section-title {{
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border-color);
    }}

    .xss-title i {{ color: var(--xss-color); }}
    .reflection-title i {{ color: var(--reflection-color); }}
    .auth-title i {{ color: var(--auth-color); }}
    .info-title i {{ color: var(--info-color); }}

    .finding {{
      background: var(--bg-secondary);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-sm);
      margin-bottom: 16px;
      overflow: hidden;
      display: flex;
      transition: transform 0.2s ease;
    }}

    .finding:hover {{
      transform: translateY(-3px);
      box-shadow: var(--shadow-md);
    }}

    .finding-icon {{
      width: 48px;
      min-width: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      padding: 12px;
    }}

    .finding.xss .finding-icon {{ background: var(--xss-gradient); }}
    .finding.reflection .finding-icon {{ background: var(--reflection-gradient); }}
    .finding.auth .finding-icon {{ background: var(--auth-gradient); }}
    .finding.info .finding-icon {{ background: var(--info-gradient); }}

    .finding-content {{
      padding: 16px;
      flex-grow: 1;
    }}

    .finding-content strong {{
      display: block;
      margin-bottom: 6px;
      font-weight: 600;
    }}

    .finding-content p {{
      color: var(--text-secondary);
      font-size: 14px;
      margin-bottom: 8px;
    }}

    .finding-content a {{
      color: #3498db;
      text-decoration: none;
      font-size: 14px;
      word-break: break-all;
      display: block;
      margin-top: 6px;
    }}

    .finding-content a:hover {{
      text-decoration: underline;
    }}

    .footer {{
      margin-top: 48px;
      padding: 24px 0;
      text-align: center;
      color: var(--text-secondary);
      font-size: 14px;
    }}

    @media (max-width: 768px) {{
      .stats-grid {{
        grid-template-columns: 1fr;
      }}

      .dashboard-content {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="container header-content">
      <div class="logo">
        <i class="fas fa-shield-alt"></i>
        <h1>Penetration Test Report</h1>
      </div>
      <div class="timestamp">
        <i class="far fa-clock"></i>
        Generated on {now}
      </div>
    </div>
  </header>

  <main class="container">
    <section class="dashboard-overview">
      <div class="stats-grid">
        {dashboard_html}
      </div>
    </section>

    <div class="dashboard-content">
      <div class="findings-container">
        <h2>Detected Vulnerabilities</h2>
        {findings_html}
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">Vulnerability Distribution</h3>
        </div>
        <div class="chart-container">
          <canvas id="vulnerabilitiesChart"></canvas>
        </div>
      </div>
    </div>
  </main>

  <footer class="footer container">
    <p>Generated by Automated Penetration Testing System</p>
  </footer>

  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    // Set up the chart
    const ctx = document.getElementById('vulnerabilitiesChart').getContext('2d');

    // Chart configuration
    const vulnerabilitiesChart = new Chart(ctx, {{
      type: 'doughnut',
      data: {{
        labels: {labels},
        datasets: [{{
          data: {data},
          backgroundColor: [
            '#e74c3c', // XSS
            '#f39c12', // Reflection
            '#3498db', // Auth
            '#2ecc71'  // Info
          ],
          borderWidth: 0,
          hoverOffset: 15
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: true,
        cutout: '70%',
        plugins: {{
          legend: {{
            position: 'bottom',
            labels: {{
              usePointStyle: true,
              padding: 20,
              font: {{
                size: 12,
                family: "'Inter', sans-serif"
              }}
            }}
          }},
          tooltip: {{
            backgroundColor: 'white',
            titleColor: '#1e293b',
            bodyColor: '#64748b',
            titleFont: {{
              size: 14,
              weight: 'bold',
              family: "'Inter', sans-serif"
            }},
            bodyFont: {{
              size: 13,
              family: "'Inter', sans-serif"
            }},
            padding: 12,
            boxWidth: 10,
            boxHeight: 10,
            usePointStyle: true,
            borderColor: '#e2e8f0',
            borderWidth: 1,
            cornerRadius: 8,
            displayColors: true,
            callbacks: {{
              label: function(context) {{
                const label = context.label || '';
                const value = context.raw || 0;
                return ` ${{label}}: ${{value}}`;
              }}
            }}
          }}
        }},
        animation: {{
          animateScale: true,
          animateRotate: true
        }}
      }}
    }});
  </script>
</body>
</html>
'''

            with open("pentest_report.html", "w", encoding="utf-8") as f:
                f.write(report_html)

            print("[ReporterAgent] ✅ Modern dashboard report generated: pentest_report.html")

    async def setup(self):
        print("[ReporterAgent] Agent launched.")
        self.add_behaviour(self.ReportBehaviour())