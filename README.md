# Web Catcher

**Which trends should Vans chase?** When a competitor's shoe takes off, a brand has to decide fast: answer it with one of its own shoes, or let it pass. I built Web Catcher as a Product & Merchandising intern at Vans in Shanghai in 2024 to help make that call, and rebuilt it in 2026.

- **Play it in the browser:** [senergunsel.com/projects/web-catcher](https://senergunsel.com/projects/web-catcher/)
- **Run the Python version:** [projectwebcatcher.streamlit.app](https://projectwebcatcher.streamlit.app/)

Every number in it is illustrative. The signals, the ratings and the calls are mine, set to show how the tool works, and none of them is Vans data or anyone's real sales.

## How the call is made

Two scores, each out of 100, and a line at 50.

- **Momentum** is how hot the trend is. Growth over the last year counts for half, buzz for 30% and size for 20%. Each signal is put on the same 0 to 100 scale before it's weighted: growth runs from −50% to +50%, buzz and size from 1 to 5.
- **Fit** is how close a shoe is to the trend: the average of its ratings on six traits (price, function, shape, material, color, pattern), on the same 0 to 100 scale. Of Vans' three core shoes (Old Skool, Authentic, Slip-On), the closest one counts.

| | Close shoe (fit 50+) | No close shoe |
|---|---|---|
| **Hot trend (momentum 50+)** | **Back it** | **Test small** |
| **Not hot** | **Hold** | **Pass** |

How long the trend lasts decides what backing it means. Under six months, new product can't reach the shelf in time, so the play is marketing and the stock you already have. Six to twelve months leaves time for new colors and materials. Over a year is long enough to develop the shoe.

Three launch levers move the ratings by half a point a step: product moves material, color and pattern (at half strength for a 6 to 12 month trend, not at all for a shorter one), marketing moves function, and money moves price. Nothing moves shape quickly.

## Files

- `vans_trend_tool.py`: the Streamlit app.
- `webcatcher_model.py`: the rules, including the coach's search. The JavaScript copy on senergunsel.com runs the same steps in the same order, so both give the same numbers.
- `requirements.txt`: pinned versions, tested together on Python 3.11.

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run vans_trend_tool.py
```

## What changed in the 2026 rebuild

- The shoe ratings now decide where each trend sits on the chart. In the original they were scored, but the chart used a fixed fit for each trend.
- Every signal is scored out of 100 before it's weighted. Sales used to go in as raw units and outweighed growth and buzz.
- A hot trend none of the core shoes fits gets its own call, Test small, instead of the same answer as a dead one.
- The scenario levers move the shoe on the chart instead of only changing the wording, and product work only counts if the trend lasts long enough for it to land.
- A coach line under the call says the cheapest lever move from where you are that would turn it into Back it, or why nothing will.
- Updated to current Streamlit, pandas and Plotly, with every version pinned.
