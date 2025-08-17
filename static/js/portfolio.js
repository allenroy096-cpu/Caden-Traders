// portfolio.js - Handles fetching and rendering portfolio tables


// Zerodha-style summary, sector bar, and holdings table
document.addEventListener('DOMContentLoaded', function() {
  fetch('/api/stocks')
    .then(r => r.json())
    .then(data => {
      const stocks = data.stocks;
      // --- Summary Cards ---
      const invested = data.portfolio_metrics?.total_investment || 0;
      const presentValue = stocks.reduce((a, s) => a + (s.current_price * s.quantity), 0);
      const unrealizedPL = presentValue - invested;
      const unrealizedPLPct = invested ? (unrealizedPL / invested * 100) : 0;
      document.getElementById('summary-invested').textContent = invested.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2});
      document.getElementById('summary-present-value').textContent = presentValue.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2});
      document.getElementById('summary-unrealized-pl').textContent = unrealizedPL.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2});
      document.getElementById('summary-unrealized-pl-pct').innerHTML = `${unrealizedPL >= 0 ? '<span class="text-success">▲' : '<span class="text-danger">▼'}${unrealizedPLPct.toFixed(2)}%</span>`;
      document.getElementById('summary-xirr').textContent = '-'; // Placeholder

      // --- Last Updated ---
      const lastUpdated = new Date().toLocaleString();
      document.getElementById('portfolio-last-updated').textContent = `Last updated: ${lastUpdated}`;

      // --- Sector Bar ---
      const sectorBar = document.getElementById('portfolio-sector-bar');
      const sectorTotals = {};
      stocks.forEach(s => {
        if (!sectorTotals[s.sector]) sectorTotals[s.sector] = 0;
        sectorTotals[s.sector] += s.total_investment;
      });
      const total = Object.values(sectorTotals).reduce((a, b) => a + b, 0);
      const sectorColors = [
        '#43b97f', '#f4b400', '#4285f4', '#db4437', '#ab47bc', '#00acc1', '#ff7043', '#8d6e63', '#789262', '#cddc39'
      ];
      let colorIdx = 0;
      sectorBar.innerHTML = '<div class="d-flex" style="height:32px;">' +
        Object.entries(sectorTotals).map(([sector, val]) => {
          const width = total ? (val / total * 100) : 0;
          const color = sectorColors[colorIdx++ % sectorColors.length];
          return `<div title="${sector}" style="width:${width}%;background:${color};display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;white-space:nowrap;">${width > 8 ? sector : ''}</div>`;
        }).join('') + '</div>';

      // --- Holdings Table ---
      const holdingsTbody = document.querySelector('#portfolio-holdings-table tbody');
      holdingsTbody.innerHTML = '';
      stocks.forEach(s => {
        const buyValue = s.buy_price * s.quantity;
        const presentValue = s.current_price * s.quantity;
        const pl = presentValue - buyValue;
        const plPct = buyValue ? (pl / buyValue * 100) : 0;
        holdingsTbody.innerHTML += `<tr>
          <td>${s.symbol}</td>
          <td>${s.name || '-'}</td>
          <td>${s.sector || '-'}</td>
          <td>${s.quantity}</td>
          <td>${s.buy_price.toFixed(2)}</td>
          <td>₹${buyValue.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
          <td>₹${s.current_price?.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2}) ?? '-'}</td>
          <td>₹${presentValue.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
          <td class="${pl >= 0 ? 'text-success' : 'text-danger'}">${pl >= 0 ? '+' : ''}${pl.toFixed(2)}</td>
          <td class="${plPct >= 0 ? 'text-success' : 'text-danger'}">${plPct >= 0 ? '+' : ''}${plPct.toFixed(2)}%</td>
        </tr>`;
      });

      // --- Download XLSX (placeholder) ---
      document.getElementById('portfolio-download-xlsx').addEventListener('click', function(e) {
        e.preventDefault();
        alert('Download as XLSX coming soon!');
      });


      // --- Sector-wise split-up tables: only render in Treemap tab ---
      function renderSectorTables() {
        const sectorMap = {};
        stocks.forEach(s => {
          if (!sectorMap[s.sector]) sectorMap[s.sector] = [];
          sectorMap[s.sector].push(s);
        });
        const sectorDiv = document.getElementById('portfolio-sector-tables');
        if (sectorDiv) {
          sectorDiv.innerHTML = '';
          const sectorEntries = Object.entries(sectorMap).filter(([sector, arr]) => arr.length > 0);
          if (sectorEntries.length === 0) {
            sectorDiv.innerHTML = '<div class="alert alert-info">No sector data available.</div>';
          } else {
            sectorEntries.forEach(([sector, sectorStocks]) => {
              // Calculate sector metrics
              const peArr = sectorStocks.map(s => s.pe).filter(x => typeof x === 'number' && !isNaN(x));
              const divYieldArr = sectorStocks.map(s => s.dividend_yield).filter(x => typeof x === 'number' && !isNaN(x));
              const peAvg = peArr.length ? (peArr.reduce((a, b) => a + b, 0) / peArr.length) : 0;
              const divYieldAvg = divYieldArr.length ? (divYieldArr.reduce((a, b) => a + b, 0) / divYieldArr.length) : 0;
              const sectorTotal = sectorStocks.reduce((a, s) => a + (s.total_investment || 0), 0);
              // Calculate sector weight % relative to portfolio (all stocks in this sector)
              const sectorWeightPctPortfolio = sectorTotal && data.portfolio_metrics && data.portfolio_metrics.total_investment ? (sectorTotal / data.portfolio_metrics.total_investment * 100) : 0;
              sectorDiv.innerHTML += `
    <div class="card mb-4">
      <div class="card-header bg-light"><b>${sector} Sector</b> &mdash; <span class="text-muted">P/E Avg: ${peAvg.toFixed(2)}, Div. Yield Avg: ${divYieldAvg.toFixed(2)}%, Sector Total: ₹${sectorTotal.toLocaleString()}, <b>Sector Weight: ${sectorWeightPctPortfolio.toFixed(2)}%</b></span></div>
      <div class="card-body p-2">
        <div style="overflow-x:auto">
        <table class="table table-sm table-bordered">
          <thead>
            <tr>
              <th>Name</th><th>Symbol</th><th>P/E</th><th>Div. Yield</th><th>Price</th><th>Qty</th><th>Invested</th><th>Return %</th><th>Weight %</th>
            </tr>
          </thead>
          <tbody>
            ${sectorStocks.map(s => {
              // Weight %: relative to sector
              const weightPctSector = sectorTotal ? (s.total_investment / sectorTotal * 100) : 0;
              return `<tr>
                <td>${s.name}</td><td>${s.symbol}</td><td>${(typeof s.pe === 'number' && !isNaN(s.pe)) ? s.pe : '-'}</td><td>${(typeof s.dividend_yield === 'number' && !isNaN(s.dividend_yield)) ? s.dividend_yield : '-'}</td><td>₹${s.current_price?.toLocaleString?.() ?? '-'}</td><td>${s.quantity}</td><td>₹${s.total_investment.toLocaleString()}</td><td>${(s.avg_return*100).toFixed(2)}%</td><td>${weightPctSector.toFixed(2)}%</td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
        </div>
      </div>
    </div>
  `;
            });
          }
        }
      }

      // Only render sector tables when Treemap tab is active
      const treemapTab = document.getElementById('treemap-tab');
      if (treemapTab) {
        treemapTab.addEventListener('shown.bs.tab', function() {
          renderSectorTables();
        });
      }
      // If Treemap is already active on load, render immediately
      const treemapElem = document.getElementById('treemap');
      if (treemapElem && treemapElem.classList.contains('show')) {
        renderSectorTables();
      }

      // --- Chart.js chart rendering ---
      // Helper: get unique asset classes
      const assetMap = {};
      stocks.forEach(s => {
        if (!assetMap[s.asset_class]) assetMap[s.asset_class] = 0;
        assetMap[s.asset_class] += s.total_investment;
      });

      // Chart.js: destroy previous charts if they exist
      if (window.accountChartInstance) window.accountChartInstance.destroy();
      if (window.sectorChartInstance) window.sectorChartInstance.destroy();
      if (window.stockChartInstance) window.stockChartInstance.destroy();
      if (window.treemapSectorChartInstance) window.treemapSectorChartInstance.destroy();

      // Account chart (by asset class)
      window.accountChartInstance = new Chart(document.getElementById('accountChart').getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: Object.keys(assetMap),
          datasets: [{
            data: Object.values(assetMap),
            backgroundColor: ['#1a56db', '#f4b400', '#a0aec0', '#43b97f', '#db4437'],
          }]
        },
        options: {
          plugins: { legend: { position: 'right' } },
          cutout: '70%',
        }
      });

      // Sector chart
      window.sectorChartInstance = new Chart(document.getElementById('sectorChart').getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: Object.keys(sectorTotals),
          datasets: [{
            data: Object.values(sectorTotals),
            backgroundColor: sectorColors,
          }]
        },
        options: {
          plugins: { legend: { position: 'right' } },
          cutout: '70%',
          onClick: (e, elements) => {
            if (elements.length > 0) {
              const idx = elements[0].index;
              const sector = window.sectorChartInstance.data.labels[idx];
              filterTableBySector(sector);
            }
          }
        }
      });

      // Stock chart (by symbol)
      const stockMap = {};
      stocks.forEach(s => {
        stockMap[s.symbol] = s.total_investment;
      });
      window.stockChartInstance = new Chart(document.getElementById('stockChart').getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: Object.keys(stockMap),
          datasets: [{
            data: Object.values(stockMap),
            backgroundColor: sectorColors.concat(['#1a56db', '#f4b400', '#a0aec0']),
          }]
        },
        options: {
          plugins: { legend: { position: 'right' } },
          cutout: '70%',
        }
      });

      // Treemap sector chart (single chart for all sectors) as bar chart
      if (document.getElementById('treemapSectorChart')) {
        window.treemapSectorChartInstance = new Chart(document.getElementById('treemapSectorChart').getContext('2d'), {
          type: 'bar',
          data: {
            labels: Object.keys(sectorTotals),
            datasets: [{
              data: Object.values(sectorTotals),
              backgroundColor: sectorColors,
            }]
          },
          options: {
            plugins: { legend: { display: false } },
            indexAxis: 'y',
            scales: {
              x: { beginAtZero: true, title: { display: true, text: 'Investment (₹)' } },
              y: { title: { display: true, text: 'Sector' } }
            }
          }
        });
      }

      // --- Interactivity: filter portfolio table by sector ---
      function filterTableBySector(sector) {
        const rows = document.querySelectorAll('#portfolio-holdings-table tbody tr');
        rows.forEach(row => {
          const symbol = row.children[0].textContent;
          const stock = stocks.find(s => s.symbol === symbol);
          if (!stock || stock.sector !== sector) {
            row.style.display = 'none';
          } else {
            row.style.display = '';
          }
        });
      }

      // Reset table filter on clicking outside chart
      document.getElementById('sectorChart').onclick = function(e) {
        if (e.target.tagName !== 'CANVAS') {
          // Show all rows
          document.querySelectorAll('#portfolio-holdings-table tbody tr').forEach(row => row.style.display = '');
        }
      };

      // --- Insights tab: fetch and render advanced portfolio analytics ---
      function renderAdvancedInsights() {
        fetch('/api/portfolio_insights')
          .then(r => r.json())
          .then(data => {
            const advDiv = document.getElementById('portfolio-advanced-insights');
            if (!advDiv) return;
            // Metrics
            let recommendations = [];
            const m = data.metrics || {};
            let html = `<div class="card mb-3">
              <div class="card-header bg-primary text-white">Portfolio Analytics</div>
              <div class="card-body p-2">
                <ul class="list-group list-group-flush small">
                  <li class="list-group-item">Invested: <b>₹${(m.invested||0).toLocaleString('en-IN',{minimumFractionDigits:2})}</b></li>
                  <li class="list-group-item">Present Value: <b>₹${(m.present_value||0).toLocaleString('en-IN',{minimumFractionDigits:2})}</b></li>
                  <li class="list-group-item">P&amp;L: <b>${(m.pl||0)>=0?'<span class=text-success>':'<span class=text-danger>'}${(m.pl||0).toLocaleString('en-IN',{minimumFractionDigits:2})}</span></b> (${(m.pl_pct||0).toFixed(2)}%)</li>
                  <li class="list-group-item">Volatility: <b>${(m.volatility*100||0).toFixed(2)}%</b></li>
                  <li class="list-group-item">Sharpe Ratio: <b>${(m.sharpe||0).toFixed(2)}</b></li>
                  <li class="list-group-item">VaR (95%): <b>${(m.var_95*100||0).toFixed(2)}%</b></li>
                  <li class="list-group-item">Max Drawdown: <b>${(m.max_drawdown*100||0).toFixed(2)}%</b></li>
                </ul>
              </div>
            </div>`;
            // Sector allocation
            if (data.sector_allocation) {
              html += `<div class="card mb-3"><div class="card-header bg-info text-white">Sector Allocation</div><div class="card-body p-2"><ul class="list-group list-group-flush small">`;
              Object.entries(data.sector_allocation).forEach(([sector, val]) => {
                html += `<li class="list-group-item">${sector}: <b>₹${val.toLocaleString('en-IN',{minimumFractionDigits:2})}</b></li>`;
              });
              html += `</ul></div></div>`;
            }
            // Insights
            let insightFixes = [];
            if (data.insights && data.insights.length > 0) {
              html += `<div class="card mb-3"><div class="card-header bg-warning text-dark">Insights</div><div class="card-body p-2"><ul class="list-group list-group-flush small">`;
              data.insights.forEach((ins, idx) => {
                html += `<li class="list-group-item">${ins}</li>`;
                // Map insight to a suggested fix
                let fix = '';
                let rec = '';
                if (ins.includes('at a loss')) {
                  fix = 'Review your holdings and consider rebalancing or exiting underperforming stocks.';
                  rec = 'Consider switching to fundamentally strong stocks or index funds.';
                } else if (ins.includes('High volatility')) {
                  fix = 'Diversify your portfolio with less volatile assets or sectors.';
                  rec = 'Add blue-chip or defensive sector stocks (e.g., FMCG, Pharma).';
                } else if (ins.includes('drawdown')) {
                  fix = 'Reassess risk management and consider stop-loss strategies.';
                  rec = 'Reduce exposure to high-beta stocks; consider hedging.';
                } else if (ins.includes('Low Sharpe')) {
                  fix = 'Aim to improve risk-adjusted returns by optimizing asset allocation.';
                  rec = 'Increase allocation to high Sharpe ratio funds or ETFs.';
                } else {
                  fix = 'Review this insight and take appropriate action.';
                  rec = 'Consult a financial advisor for tailored recommendations.';
                }
                insightFixes.push({ problem: ins, fix });
                recommendations.push({ problem: ins, fix, rec });
              });
              html += `</ul></div></div>`;
            }
            // Suggested Fixes Table
            if (insightFixes.length > 0) {
              html += `<div class="card mb-3"><div class="card-header bg-secondary text-white">Suggested Fixes</div><div class="card-body p-2">
                <div class="table-responsive"><table class="table table-sm table-bordered align-middle mb-0"><thead class="table-light"><tr><th>Problem</th><th>Suggested Fix</th></tr></thead><tbody>`;
              insightFixes.forEach(row => {
                html += `<tr><td>${row.problem}</td><td>${row.fix}</td></tr>`;
              });
              html += `</tbody></table></div></div></div>`;
            }
            // Top gainers/losers
            if (data.top_gainers && data.top_gainers.length > 0) {
              html += `<div class="card mb-3"><div class="card-header bg-success text-white">Top Gainers</div><div class="card-body p-2"><ul class="list-group list-group-flush small">`;
              data.top_gainers.forEach(([sym, pct]) => {
                html += `<li class="list-group-item"><b>${sym}</b>: ${(pct||0).toFixed(2)}%</li>`;
              });
              html += `</ul></div></div>`;
            }
            if (data.top_losers && data.top_losers.length > 0) {
              html += `<div class="card mb-3"><div class="card-header bg-danger text-white">Top Losers</div><div class="card-body p-2"><ul class="list-group list-group-flush small">`;
              data.top_losers.forEach(([sym, pct]) => {
                html += `<li class="list-group-item"><b>${sym}</b>: ${(pct||0).toFixed(2)}%</li>`;
              });
              html += `</ul></div></div>`;
            }
            // Stock Recommendation Table (append at the end)
            if (typeof recommendations !== 'undefined' && recommendations.length > 0) {
              html += `<div class="card mb-3"><div class="card-header bg-success text-white">Stock Recommendations</div><div class="card-body p-2">
                <div class="table-responsive"><table class="table table-sm table-bordered align-middle mb-0"><thead class="table-light"><tr><th>Recommendation</th></tr></thead><tbody>`;
              recommendations.forEach(row => {
                html += `<tr><td>${row.rec}</td></tr>`;
              });
              html += `</tbody></table></div></div></div>`;
            }
            advDiv.innerHTML = html;
          });
      }

      // Load advanced insights when Insights tab is shown
      const insightsTab = document.getElementById('insights-tab');
      if (insightsTab) {
        insightsTab.addEventListener('shown.bs.tab', function() {
          renderAdvancedInsights();
        });
      }
      // If Insights is already active on load, render immediately
      const insightsElem = document.getElementById('insights');
      if (insightsElem && insightsElem.classList.contains('show')) {
        renderAdvancedInsights();
      }
    });
});
