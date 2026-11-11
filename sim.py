import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

rng = np.random.default_rng(2026)
N = 4000
rows = []
params = {"Control": dict(p=0.41, med=27), "Variant": dict(p=0.48, med=18)}
for v, p in params.items():
    done = rng.random(N) < p["p"]
    ttfsr = np.where(done, rng.lognormal(np.log(p["med"]), 0.9, N), np.nan)
    ttfsr = np.where(ttfsr > 1440, np.nan, ttfsr)  # outside 24h window = not completed
    done = ~np.isnan(ttfsr)
    for i in range(N):
        rows.append((f"{v[0]}{i:05d}", v, bool(done[i]), None if np.isnan(ttfsr[i]) else round(float(ttfsr[i]),1)))
df = pd.DataFrame(rows, columns=["developer_id","variant","completed","ttfsr_minutes"])
df.to_csv("synthetic_docs_ab_test.csv", index=False)

# weekly tickets per 1000 active developers, 4 weeks before and 4 after
weeks = np.arange(-4, 4)
tickets = pd.DataFrame({"week": weeks,
    "tickets_per_1000": np.round(np.where(weeks < 0, rng.normal(14.0, 0.8, 8), rng.normal(10.5, 0.8, 8)), 1)})
tickets.to_csv("synthetic_weekly_tickets.csv", index=False)

out = {}
for v in params:
    s = df[df.variant==v]
    n, k = len(s), s.completed.sum()
    p = k/n; se = np.sqrt(p*(1-p)/n)
    out[v] = dict(n=n, rate=p, lo=p-1.96*se, hi=p+1.96*se, med=s.ttfsr_minutes.median())
c, t = df[df.variant=="Control"], df[df.variant=="Variant"]
z_p = stats.chi2_contingency(pd.crosstab(df.variant, df.completed), correction=False)[1]
mw_p = stats.mannwhitneyu(c.ttfsr_minutes.dropna(), t.ttfsr_minutes.dropna()).pvalue
for k,v in out.items(): print(k, v)
print("completion p", z_p, "ttfsr p", mw_p)
print(tickets)
print("tickets before", tickets[tickets.week<0].tickets_per_1000.mean(), "after", tickets[tickets.week>=0].tickets_per_1000.mean())

plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})
# chart 1
fig, ax = plt.subplots(figsize=(7,4.5))
names = list(out); rates=[out[n]["rate"]*100 for n in names]
err=[[ (out[n]["rate"]-out[n]["lo"])*100 for n in names],[(out[n]["hi"]-out[n]["rate"])*100 for n in names]]
ax.bar(names, rates, yerr=err, capsize=8, color=["#9aa5b1","#2b6cb0"], width=0.55)
for i,r in enumerate(rates): ax.text(i, r+2.5, f"{r:.1f}%", ha="center", fontweight="bold")
ax.set_ylabel("Task completion rate (%)"); ax.set_ylim(0,60)
ax.set_title("Task completion within 24 hours of first page view\n(simulated data, 95% CI)", fontsize=12)
fig.tight_layout(); fig.savefig("fig1_completion_rate.png", dpi=200)
# chart 2 ECDF
fig, ax = plt.subplots(figsize=(7,4.5))
for v,col in zip(names,["#9aa5b1","#2b6cb0"]):
    x = np.sort(df[df.variant==v].ttfsr_minutes.dropna()); y=np.arange(1,len(x)+1)/len(x)
    ax.step(x,y,where="post",color=col,lw=2,label=f"{v} (median {out[v]['med']:.0f} min)")
ax.set_xscale("log"); ax.set_xlabel("Time to first successful request (minutes, log scale)")
ax.set_ylabel("Share of successful developers"); ax.legend(frameon=False)
ax.set_title("Time to first successful request (simulated data)", fontsize=12)
fig.tight_layout(); fig.savefig("fig2_ttfsr_ecdf.png", dpi=200)
# chart 3 tickets
fig, ax = plt.subplots(figsize=(7,4.5))
ax.plot(tickets.week, tickets.tickets_per_1000, marker="o", color="#2b6cb0", lw=2)
ax.axvline(-0.5, color="#555", ls="--"); ax.text(-0.4, ax.get_ylim()[1]*0.98, "Variant rolled out", va="top")
ax.set_xlabel("Week relative to rollout"); ax.set_ylabel("Tickets per 1,000 active developers")
ax.set_ylim(0, 18); ax.set_title("Weekly support tickets (simulated data)", fontsize=12)
fig.tight_layout(); fig.savefig("fig3_tickets.png", dpi=200)
