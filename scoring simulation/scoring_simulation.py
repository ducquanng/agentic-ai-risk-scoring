"""
scoring_simulation.py
=====================
Reproducible Monte-Carlo study of the comparative risk-scoring logic (SQ3) from
the thesis "From Risk Taxonomy to Comparable Score: A Model-Validation-Ready Framework for the Second-Line Assessment of Agentic AI in Banking".

This is a STRUCTURAL / BEHAVIOURAL analysis of the aggregation operator: it
establishes properties of the scoring *formula* under stated input assumptions.
It is a verification/exploration exercise (in the sense of Sargent 2010), NOT an
empirical validation of risk levels in deployed systems, which would require real
system data that do not yet exist. There is no external input data; every number
is regenerated from the fixed seed below.

Scoring logic (thesis Chapter 6):
  dimension risk score   R_id  = 1 - prod_j (1 - x_hat_ij)^{w_j}            (Eq. 6.2)
  use-case composite     Risk_i = max( 1 - prod_d (1-R_id)^{W_d},           (Eq. 6.3)
                                       max_{d in C} R_id )
  where C = the critical-control dimensions {Access Control, Action Control,
  Monitoring & Audit}. We simulate at the dimension level: each system is a
  vector R of 7 dimension risk scores in [0,1].

Analytic fact used throughout (proved in the thesis, checked here empirically):
  arithmetic_mean(R)  <=  composite(R)  <=  max(R)   for every R,
  because (i) 1 - GM(1-x) >= 1 - AM(1-x) = AM(x) by AM-GM, so the geometric term
  is >= the arithmetic mean; (ii) both the geometric term and the veto term are
  <= max(R). Hence the rule is *partly compensatory*: it lies strictly between the
  fully-compensatory mean and the non-compensatory maximum.

Sensitivity analysis:
  - Sobol' variance-based indices (first-order S_i, total-effect S_Ti) of the
    composite w.r.t. the 7 independent dimension inputs. Estimators: Saltelli et
    al. (2010) for S_i, Jansen (1999) for S_Ti, on a Sobol' quasi-random Saltelli
    design; 95% CIs by bootstrap. Inputs are independent here, so the classic
    (independent-input) estimators are valid.
  - Ranking robustness under weight uncertainty: Dirichlet-perturbed weights,
    reported as rank-reversal frequency. This is an UNCERTAINTY/ROBUSTNESS
    analysis of the ranking (SMAA-style), NOT a Sobol' index.

Run:   python scoring_simulation.py
Needs: numpy, scipy, matplotlib   (see requirements.txt)
"""
import numpy as np
from scipy.stats import qmc, norm, rankdata
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import csv, os

SEED = 20260713                      # fixed -> fully reproducible
try:                                 # works as a script and inside the notebook
    OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
except NameError:
    OUT = "outputs"
os.makedirs(OUT, exist_ok=True)
rng  = np.random.default_rng(SEED)

DIMS = ["Information Integrity","Goal Integrity","Access Control","Action Control",
        "Human Oversight","Monitoring & Audit","Ecosystem Resilience"]
CRIT = [2, 3, 5]                     # Access Control, Action Control, Monitoring & Audit
W0   = np.ones(7) / 7.0             # equal baseline dimension weights

# ---- scoring functions (vectorised over rows) --------------------------------
def geometric(R, W=W0):             # Eq. 6.2 / first term of Eq. 6.3
    return 1.0 - np.prod((1.0 - R) ** W, axis=-1)
def veto(R):                        # second term of Eq. 6.3 (veto floor)
    return np.asarray(R)[..., CRIT].max(axis=-1)
def composite(R, W=W0):             # Eq. 6.3
    return np.maximum(geometric(R, W), veto(R))
def additive(R, W=W0):              # fully-compensatory baseline (weighted mean)
    return np.asarray(R) @ np.asarray(W)

def band(x):                        # map a score in [0,1] to a Low/Medium/High band
    return "Low" if x < 1/3 else ("Medium" if x < 2/3 else "High")   # equal thirds

def mcse_prop(p, n):                # Monte-Carlo standard error of a proportion
    return float(np.sqrt(p * (1.0 - p) / n))

# ============================================================================
# Experiment A: the three illustrative use cases (Table 7.1)
# ============================================================================
# A Low/Medium/High dimension rating is read as a representative value inside its
# band (Low<1/3, Medium in [1/3,2/3), High>=2/3); band() maps a composite score
# back to the same three bands, so encoding inputs and banding outputs use one scale.
LVL = {"L":0.2, "M":0.5, "H":0.8}   # representative value per risk band
UC_LVL = {
 "UC-A": ["M","L","L","L","L","M","L"],   # credit-memo assistant
 "UC-B": ["H","H","H","H","M","H","M"],   # AML alert triage
 "UC-C": ["H","H","H","H","H","H","H"],   # treasury / payments
}
UC = {k: np.array([LVL[x] for x in v]) for k, v in UC_LVL.items()}
with open(f"{OUT}/use_cases.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["use_case"]+DIMS+["additive","geometric","veto","composite","band"])
    for k,R in UC.items():
        c=float(composite(R))
        w.writerow([k]+[f"{x:.2f}" for x in R]+
                   [f"{float(additive(R)):.3f}",f"{float(geometric(R)):.3f}",
                    f"{float(veto(R)):.3f}",f"{c:.3f}",band(c)])
print("A) illustrative use cases (equal weights):")
for k,R in UC.items():
    c=float(composite(R))
    print(f"   {k}: additive={float(additive(R)):.3f} geometric={float(geometric(R)):.3f} "
          f"veto={float(veto(R)):.3f} composite={c:.3f} band={band(c)}")

# ============================================================================
# Experiment B: random systems -- veto-binding fraction + analytic-bound check
# ============================================================================
N = 200_000
R = rng.uniform(0, 1, size=(N, 7))
g = geometric(R); v = veto(R); comp = np.maximum(g, v)
add = R.mean(axis=1); mx = R.max(axis=1)
veto_bind = float(np.mean(v > g))
# empirical confirmation of the analytic bound  mean <= composite <= max
bound_ok = bool(np.all(comp >= add - 1e-12) and np.all(comp <= mx + 1e-12))
meanB = {"additive":add.mean(),"geometric":g.mean(),"geometric+veto":comp.mean(),"plain max":mx.mean()}
with open(f"{OUT}/random_summary.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["metric","value"])
    w.writerow(["n_random_use_cases",N])
    w.writerow(["veto_floor_binds_fraction",f"{veto_bind:.4f}"])
    w.writerow(["veto_floor_binds_MCSE",f"{mcse_prop(veto_bind,N):.5f}"])
    w.writerow(["analytic_bound_mean_le_comp_le_max_holds",bound_ok])
    for k,val in meanB.items(): w.writerow([f"mean_{k.replace(' ','_')}",f"{val:.4f}"])
print(f"B) over {N:,} iid U(0,1) systems: veto binds in {100*veto_bind:.1f}% "
      f"(MCSE {100*mcse_prop(veto_bind,N):.2f}pp); analytic bound holds: {bound_ok}")
print("   mean composite:", {k:round(val,3) for k,val in meanB.items()})

# ============================================================================
# Experiment B2: robustness of the veto-binding fraction to the input model
# ============================================================================
# The 82.5% is computed under iid Uniform(0,1). It is partly mechanical
# (E[max of 3 U] = 0.75 vs E[mean of 7 U] = 0.50) and moves with the input
# model, so we re-run it under correlated and skewed marginals.
def corr_uniform(n, d, rho, rng):
    cov = np.full((d, d), rho); np.fill_diagonal(cov, 1.0)
    L = np.linalg.cholesky(cov)
    return norm.cdf(rng.standard_normal((n, d)) @ L.T)
scenarios = {}
scenarios["iid Uniform(0,1) [reference]"] = R
scenarios["correlated rho=0.3 (Gaussian copula)"] = corr_uniform(N, 7, 0.3, rng)
scenarios["correlated rho=0.6 (Gaussian copula)"] = corr_uniform(N, 7, 0.6, rng)
scenarios["risk-low: Beta(2,5) marginals"]  = rng.beta(2, 5, size=(N, 7))
scenarios["risk-high: Beta(5,2) marginals"] = rng.beta(5, 2, size=(N, 7))
with open(f"{OUT}/binding_robustness.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["input_model","veto_binds_fraction","MCSE","mean_composite"])
    print("B2) veto-binding fraction under alternative input models:")
    binds=[]
    for name,Rs in scenarios.items():
        gs=geometric(Rs); vs=veto(Rs); p=float(np.mean(vs>gs)); binds.append(p)
        w.writerow([name,f"{p:.4f}",f"{mcse_prop(p,N):.5f}",f"{np.maximum(gs,vs).mean():.4f}"])
        print(f"    {p*100:5.1f}%  {name}")
    print(f"    -> range across input models: {min(binds)*100:.0f}%-{max(binds)*100:.0f}%")

# ============================================================================
# Experiment C: Sobol' variance-based sensitivity of the composite
# ============================================================================
# Inputs: 7 dimension scores ~ independent Uniform(0,1) (independence => the
# classic Sobol' estimators are valid). Output Y = composite(R).
# S_i : Saltelli et al. (2010);  S_Ti : Jansen (1999).
d = 7; m = 14                       # base sample size 2^14 = 16384
sob = qmc.Sobol(d=2*d, scramble=True, seed=SEED)
X = sob.random_base2(m=m)           # (2^m, 14) quasi-random, uniform in [0,1)
A, B = X[:, :d], X[:, d:]
fA, fB = composite(A), composite(B)
fAB = np.empty((d, A.shape[0]))
for i in range(d):
    ABi = A.copy(); ABi[:, i] = B[:, i]
    fAB[i] = composite(ABi)
def sobol_indices(fA, fB, fAB, idx):
    fA_, fB_, fAB_ = fA[idx], fB[idx], fAB[:, idx]
    varY = np.concatenate([fA_, fB_]).var()
    S1 = np.array([np.mean(fB_*(fAB_[i]-fA_))/varY for i in range(d)])     # first-order
    ST = np.array([0.5*np.mean((fA_-fAB_[i])**2)/varY for i in range(d)])  # total-effect
    return S1, ST
n = A.shape[0]
S1, ST = sobol_indices(fA, fB, fAB, np.arange(n))
BOOT = 1000
bs1 = np.empty((BOOT, d)); bst = np.empty((BOOT, d))
for b in range(BOOT):
    idx = rng.integers(0, n, n)
    bs1[b], bst[b] = sobol_indices(fA, fB, fAB, idx)
ci1 = np.percentile(bs1, [2.5, 97.5], axis=0); cit = np.percentile(bst, [2.5, 97.5], axis=0)
with open(f"{OUT}/sobol_indices.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["dimension","critical","S1_first_order","S1_lo","S1_hi",
                                 "ST_total_effect","ST_lo","ST_hi"])
    for i in range(d):
        w.writerow([DIMS[i], i in CRIT, f"{S1[i]:.3f}",f"{ci1[0,i]:.3f}",f"{ci1[1,i]:.3f}",
                    f"{ST[i]:.3f}",f"{cit[0,i]:.3f}",f"{cit[1,i]:.3f}"])
print(f"C) Sobol' indices (N={n:,} base, {n*(d+2):,} model runs):")
print(f"   sum first-order S_i = {S1.sum():.2f} (additivity share); "
      f"critical-dim total-effect share = {ST[CRIT].sum()/ST.sum()*100:.0f}%")
for i in range(d):
    print(f"   {'*' if i in CRIT else ' '} {DIMS[i]:22s} S1={S1[i]:.3f}  ST={ST[i]:.3f}")

# ============================================================================
# Experiment D: ranking robustness under weight uncertainty (not Sobol')
# ============================================================================
# Dirichlet-perturbed weights around equal; report rank-reversal frequency.
extra = {f"UC-{n_}": rng.uniform(0,1,7) for n_ in ["D","E","F"]}
cases = {**UC, **extra}; names=list(cases); Rmat=np.array([cases[n_] for n_ in names])
M = 20_000
Wdraw = rng.dirichlet(W0*40.0, size=M)      # plausible perturbations around equal weights
comps = np.array([composite(Rmat, Wm) for Wm in Wdraw])   # (M, n_cases)

# Ties have to be handled explicitly here, and the reason is structural rather
# than numerical. Two use cases whose critical-control dimensions are all High
# are both pinned to the same value by the veto floor whenever that floor binds,
# whatever the weights are: UC-B and UC-C score exactly 0.800 in ~91% of these
# draws, and in the rest they differ by one unit in the last place (~2e-16) with
# no consistent sign. Ranking those with argsort asks the sort to order two
# numbers that are equal, which it does by position, and the result then depends
# on how the machine rounded the geometric term -- it differs between CPUs.
#
# An earlier version of this script did exactly that, and reported "91% modal
# rank retention" for UC-B and UC-C. That 91% was not a property of the scoring
# rule: it was the share of draws in which the two identical scores happened to
# round to the same double on the machine that ran it (another CPU gives 94%).
# Rounding to TIE_TOL and ranking ties as tied removes the artefact, makes the
# number identical on every machine, and reports the honest result: the ranking
# is stable under weight uncertainty, and UC-B and UC-C are tied, not ordered.
TIE_TOL = 1e-12                                            # << any real score gap
snapped = np.round(comps / TIE_TOL) * TIE_TOL
ranks = rankdata(-snapped, method="min", axis=1).astype(int)   # rank 1 = highest risk
with open(f"{OUT}/rank_stability.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["use_case","baseline_composite","modal_rank",
                                 "P_modal_percent","P_modal_MCSE_pp","rank_min","rank_max"])
    for i,nm in enumerate(names):
        modal=np.bincount(ranks[:,i]).argmax(); p=float(np.mean(ranks[:,i]==modal))
        w.writerow([nm,f"{float(composite(Rmat[i])):.3f}",modal,f"{100*p:.0f}",
                    f"{100*mcse_prop(p,M):.2f}",int(ranks[:,i].min()),int(ranks[:,i].max())])

# Pairwise stability. A pair that is tied in the majority of draws is reported as
# tied rather than counted as agreeing: comparing it with a strict ">" would score
# the one pair that cannot be ordered as the most stable pair of all.
pairs=tctc=tied_pairs=0; tied_names=[]
for i in range(len(names)):
    for j in range(i+1,len(names)):
        pairs+=1
        if np.mean(snapped[:,i]==snapped[:,j])>0.5:
            tied_pairs+=1; tied_names.append(f"{names[i]}/{names[j]}"); continue
        base=float(composite(Rmat[i]))>float(composite(Rmat[j]))
        if np.mean((snapped[:,i]>snapped[:,j])!=base)>0.05: tctc+=1
print(f"D) ranking robustness over {M:,} Dirichlet weight draws: "
      f"{tctc} of {pairs} pairs 'too close to call'; "
      f"{tied_pairs} tied by construction ({', '.join(tied_names) or 'none'})")

# ============================================================================
# Experiment E: sensitivity to the ordinal Low/Medium/High number encoding
# ============================================================================
# L/M/H are ordinal; 0.2/0.5/0.8 fixes spacing and anchors. Re-score under
# alternative monotone codings and check the ordering / bands are invariant.
codings = {"0.2/0.5/0.8 [reference]":(0.2,0.5,0.8), "0.1/0.5/0.9":(0.1,0.5,0.9),
           "0.25/0.5/0.75":(0.25,0.5,0.75), "0.3/0.5/0.7":(0.3,0.5,0.7),
           "0.2/0.4/0.9 (asymmetric)":(0.2,0.4,0.9)}
with open(f"{OUT}/encoding_sensitivity.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["coding","UC-A","UC-A_band","UC-B","UC-B_band",
                                 "UC-C","UC-C_band","order_high_to_low"])
    print("E) ordinal-encoding sensitivity (composite; band):")
    for name,(lo,mi,hi) in codings.items():
        mp={"L":lo,"M":mi,"H":hi}
        sc={k:float(composite(np.array([mp[x] for x in v]))) for k,v in UC_LVL.items()}
        order="; ".join(sorted(sc,key=lambda k:-sc[k]))
        w.writerow([name]+[f"{sc['UC-A']:.3f}",band(sc['UC-A']),f"{sc['UC-B']:.3f}",
                    band(sc['UC-B']),f"{sc['UC-C']:.3f}",band(sc['UC-C']),order])
        print(f"    {name:26s} A={sc['UC-A']:.2f}({band(sc['UC-A'])}) "
              f"B={sc['UC-B']:.2f}({band(sc['UC-B'])}) C={sc['UC-C']:.2f}({band(sc['UC-C'])})")

# ============================================================================
# Experiment F: aggregation ablation (for the figure / Table)
# ============================================================================
with open(f"{OUT}/aggregation_ablation.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["rule","UC-A","UC-B","UC-C","order_high_to_low"])
    for rule,fn in [("additive",additive),("geometric",geometric),("geometric+veto",composite)]:
        sc={k:float(fn(R_)) for k,R_ in UC.items()}
        order="; ".join(sorted(sc,key=lambda k:-sc[k]))
        w.writerow([rule]+[f"{sc[k]:.3f}" for k in ["UC-A","UC-B","UC-C"]]+[order])

# ============================================================================
# Experiment G: consolidated report of every number cited in Section 6.2
# ============================================================================
# Each line prints the exact value that appears in the thesis text, so every
# figure quoted in the chapter is traceable to computed output, not asserted.
def pct(x): return f"{100*x:.1f}%"
uc_comp   = {k: float(composite(UC[k])) for k in ["UC-A","UC-B","UC-C"]}
worst3    = float(veto(R).mean())                 # E[worst of 3 critical dims]  -> 0.75
mean7     = float(R.mean())                        # E[mean of 7 dims]            -> 0.50
bfrac     = {nm: float(np.mean(veto(Rs) > geometric(Rs))) for nm, Rs in scenarios.items()}
floor_nm  = min(bfrac, key=bfrac.get)              # the input model with the LOWEST binding fraction
crit_share= float(ST[CRIT].sum() / ST.sum())       # Sobol total-effect share of the 3 critical dims
noncrit   = [i for i in range(7) if i not in CRIT]
retention = [100*np.mean(ranks[:, i] == np.bincount(ranks[:, i]).argmax()) for i in range(len(names))]
enc_azn   = {k: float(composite(np.array([{"L":0.2,"M":0.4,"H":0.9}[x] for x in lv]))) for k, lv in UC_LVL.items()}
ucA_avg   = float(additive(UC["UC-A"]))            # UC-A under a plain average

REPORT = [
 "="*72,
 "SECTION 6.2 -- every number in the text, as computed output",
 "="*72,
 f"[6.2 examples] UC-A composite = {uc_comp['UC-A']:.2f} ({band(uc_comp['UC-A'])}); "
 f"UC-B = {uc_comp['UC-B']:.2f} ({band(uc_comp['UC-B'])}); "
 f"UC-C = {uc_comp['UC-C']:.2f} ({band(uc_comp['UC-C'])})",
 f"[6.2 F1] veto floor is the larger term in {pct(veto_bind)} of {N:,} random systems "
 f"(MCSE {100*mcse_prop(veto_bind,N):.2f} pp)",
 f"[6.2 F1] worst-of-3 critical dims averages {worst3:.2f}; average of all 7 averages {mean7:.2f}",
 f"[6.2 F1] veto-binding across input models: floor = {pct(bfrac[floor_nm])} ({floor_nm}); "
 f"highest = {pct(max(bfrac.values()))}",
 f"[6.2 F2] mean score -- plain average {meanB['additive']:.2f} | geometric {meanB['geometric']:.2f} | "
 f"geometric+veto {meanB['geometric+veto']:.2f} | worst value {meanB['plain max']:.2f}",
 f"[6.2 F2] analytic bound (mean <= composite <= max) holds for all {N:,} systems: {bound_ok}",
 f"[6.2 F3] critical-control dims carry {crit_share*100:.0f}% of the score's movement "
 f"(Sobol total-effect share); other four ~{ST[noncrit].mean():.2f} each",
 f"[6.2 F4] rank retention {min(retention):.0f}%-{max(retention):.0f}% over {M:,} weight draws; "
 f"pairs too close to call: {tctc} of {pairs}; tied by construction: {tied_pairs} of {pairs} "
 f"({', '.join(tied_names) or 'none'})  [thesis text quotes 91-100%; see README]",
 f"[6.2 F4] encoding 0.2/0.4/0.9 -> UC-A {band(enc_azn['UC-A'])}, UC-B {band(enc_azn['UC-B'])}, "
 f"UC-C {band(enc_azn['UC-C'])} (order unchanged)",
 f"[6.2 F5] UC-A under plain average = {ucA_avg:.2f}; under full rule = {uc_comp['UC-A']:.2f} "
 f"(veto floor trips)",
 "="*72,
]
print("\n".join(REPORT))
with open(f"{OUT}/section_6_2_numbers.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["thesis_reference","quantity","value_in_text","computed_value"])
    w.writerow(["6.2 examples","UC-A / UC-B / UC-C composite","0.50 / 0.80 / 0.80",
                f"{uc_comp['UC-A']:.2f} / {uc_comp['UC-B']:.2f} / {uc_comp['UC-C']:.2f}"])
    w.writerow(["6.2 F1","veto-binding fraction (iid reference)","82.5%",f"{veto_bind*100:.1f}%"])
    w.writerow(["6.2 F1","worst-of-3 mean / mean-of-7","0.75 / 0.50",f"{worst3:.2f} / {mean7:.2f}"])
    w.writerow(["6.2 F1","binding floor / highest across models","82.5% / ~87%",
                f"{bfrac[floor_nm]*100:.1f}% / {max(bfrac.values())*100:.1f}%"])
    w.writerow(["6.2 F2","means additive/geo/geo+veto/max","0.50/0.61/0.77/0.88",
                f"{meanB['additive']:.2f}/{meanB['geometric']:.2f}/{meanB['geometric+veto']:.2f}/{meanB['plain max']:.2f}"])
    w.writerow(["6.2 F2","analytic bound holds","True",str(bound_ok)])
    w.writerow(["6.2 F3","critical-control Sobol total-effect share","93%",f"{crit_share*100:.0f}%"])
    # The text's 91% was a tie-break artefact (see Experiment D); the corrected,
    # machine-independent computation is 100%. Both are shown, as everywhere else.
    w.writerow(["6.2 F4","rank retention min-max","91-100%",f"{min(retention):.0f}-{max(retention):.0f}%"])
    w.writerow(["6.2 F4","pairs too close to call","0 of 15",f"{tctc} of {pairs}"])
    w.writerow(["6.2 F4","pairs tied by construction","not reported",
                f"{tied_pairs} of {pairs} ({', '.join(tied_names) or 'none'})"])
    w.writerow(["6.2 F5","UC-A plain average / full rule","0.29 / 0.50",f"{ucA_avg:.2f} / {uc_comp['UC-A']:.2f}"])

# ============================================================================
# Figure (regenerates sim_scoring.png) -- 3 panels
# ============================================================================
plt.rcParams.update({"font.size":9,"font.family":"serif","axes.spines.top":False,"axes.spines.right":False})
B1,B2,B3,B4="#c6d9f1","#8db4e2","#4472c4","#1f3864"
fig,ax=plt.subplots(1,3,figsize=(13.2,3.4))
# Panel (a): aggregation ablation on the three use cases
ucs=["UC-A","UC-B","UC-C"]
A_add=[float(additive(UC[k])) for k in ucs]; A_geo=[float(geometric(UC[k])) for k in ucs]
A_vet=[float(composite(UC[k])) for k in ucs]
x=np.arange(3); bw=0.26
ax[0].bar(x-bw,A_add,bw,label="additive (mean)",color=B1,edgecolor=B4,lw=.6)
ax[0].bar(x,   A_geo,bw,label="geometric",color=B2,edgecolor=B4,lw=.6)
ax[0].bar(x+bw,A_vet,bw,label="geometric + veto",color=B3,edgecolor=B4,lw=.6)
ax[0].set_xticks(x); ax[0].set_xticklabels(ucs); ax[0].set_ylim(0,1)
ax[0].set_ylabel("composite risk"); ax[0].set_title("(a) The rule changes the score",fontsize=9.5)
ax[0].annotate(f"veto floor lifts UC-A\n{A_add[0]:.2f} $\\to$ {A_vet[0]:.2f} (Low$\\to$Medium)",
    xy=(0+bw,A_vet[0]),xytext=(0.10,0.82),fontsize=7.3,ha="left",
    arrowprops=dict(arrowstyle="->",color=B4,lw=.8))
ax[0].legend(fontsize=7.0,frameon=False,loc="upper right")
# Panel (b): where the rule sits (means over random cases) -- the analytic bound
labels=["additive\n(mean)","geometric","geometric\n+ veto","plain\nmax"]
vals=[meanB["additive"],meanB["geometric"],meanB["geometric+veto"],meanB["plain max"]]
cols=[B1,B2,B3,"#95a5a6"]
ax[1].bar(range(4),vals,color=cols,edgecolor=B4,lw=.6,width=.62)
for i,val in enumerate(vals): ax[1].text(i,val+0.02,f"{val:.2f}",ha="center",fontsize=8)
ax[1].set_xticks(range(4)); ax[1].set_xticklabels(labels,fontsize=8); ax[1].set_ylim(0,1)
ax[1].set_ylabel("mean composite risk"); ax[1].set_title("(b) Partly compensatory: mean $\\leq$ rule $\\leq$ max",fontsize=9.5)
ax[1].annotate("",xy=(0,0.46),xytext=(3,0.46),arrowprops=dict(arrowstyle="<->",color="#888",lw=.8))
ax[1].text(1.5,0.40,"fully compensatory  $\\longleftrightarrow$  non-compensatory",ha="center",fontsize=7,color="#555")
# Panel (c): Sobol' total-effect indices per dimension
order_idx=np.argsort(-ST)
short=["Info. Integrity","Goal Integrity","Access Ctrl","Action Ctrl","Human Overst.","Monitor/Audit","Ecosys. Resil."]
cST=[B3 if i in CRIT else B1 for i in order_idx]
ax[2].barh(range(d),ST[order_idx],color=cST,edgecolor=B4,lw=.6)
ax[2].errorbar(ST[order_idx],range(d),xerr=[ST[order_idx]-cit[0,order_idx],cit[1,order_idx]-ST[order_idx]],
    fmt="none",ecolor="#333",elinewidth=.7,capsize=2)
ax[2].set_yticks(range(d)); ax[2].set_yticklabels([short[i] for i in order_idx],fontsize=7.5)
ax[2].invert_yaxis(); ax[2].set_xlim(0,max(ST)*1.25)
ax[2].set_xlabel("Sobol' total-effect index $S_{Ti}$")
ax[2].set_title("(c) Variance driven by critical controls",fontsize=9.5)
ax[2].text(0.97,0.05,"blue = critical-control\ndimension",transform=ax[2].transAxes,
    ha="right",va="bottom",fontsize=6.8,color=B4)
plt.tight_layout(); plt.savefig(f"{OUT}/sim_scoring.png",dpi=150,bbox_inches="tight")
print(f"\nFigure written to {OUT}/sim_scoring.png ; CSV outputs in {OUT}/")
print("numpy", np.__version__, "| seed", SEED)
