# Measuring documentation quality with A/B tests (simulated data)

   Companion code for my Towards Data Science article on measuring whether API docs work, using task completion rate, time to first successful request (TTFSR) and support ticket volume.

   **All data in this repo is simulated.** It was generated to demonstrate the method and does not come from any real company.

   ## Files
   - `sim.py`: generates the datasets, runs the statistical tests and draws the figures
   - `synthetic_docs_ab_test.csv`: one row per simulated developer (variant, completed, ttfsr_minutes)
   - `synthetic_weekly_tickets.csv`: weekly support tickets per 1,000 active developers, 4 weeks either side of rollout
   - `fig1_completion_rate.png`, `fig2_ttfsr_ecdf.png`, `fig3_tickets.png`: figures used in the article

   ## Reproduce
   pip install -r requirements.txt
   python sim.py

   The random seed is fixed (2026), so you get the same numbers as the article.

   ## License
   MIT
