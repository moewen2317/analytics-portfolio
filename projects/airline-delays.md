# Late-arriving aircraft cause 40% of delay minutes, and the raw carrier ranking misleads

A cleaning-and-exploration exercise on 34,013 carrier-airport-month records of US airline delays: find what causes delay minutes, when they peak, and which carriers fare worst. It is also a short lesson in how an average can mislead.

## The question

What drives airline delays, and how do delays vary over time and between carriers?

## Data and set-up

- 34,016 rows, one per carrier, airport and month, with 21 columns of flight counts, delay counts and delay minutes by cause (carrier, weather, national airspace system, security, late aircraft).
- Cleaning: 3 duplicate rows removed, leaving 34,013. 293 missing values filled with zero. 266 of them appear to come from 19 rows missing every flight and delay figure, and those rows should be dropped instead (see below).
- Derived columns: average delay per flight and per delayed flight.

## What I found

**Late aircraft and carrier problems dominate.** Averaged across rows, a late inbound aircraft accounts for about 2,025 delay minutes, carrier issues about 1,674, national airspace system issues about 997 and weather about 324. As shares of total delay minutes: late aircraft 40%, carrier 33%, airspace system 20%, weather 6%, security under 1%. Weather is the smallest of the four main causes.

<figure>
<img src="figures/airline-causes.png" alt="Bar chart of average delay minutes by cause: late aircraft about 2,025, carrier about 1,674, national airspace system about 997 and weather about 324.">
<figcaption>Late aircraft and carrier causes account for about three-quarters of delay minutes.</figcaption>
</figure>

**Delays peak in July and bottom out in October.** Average delay minutes per row run from about 8,300 in July to about 2,750 in October. These totals are not adjusted for flight volume, so part of the pattern is simply more flying in summer.

<figure>
<img src="figures/airline-months.png" alt="Line chart of average delay minutes by month, peaking near 8,300 in July and falling to about 2,750 in October.">
<figcaption>Raw delay minutes peak in July and are lowest in October.</figcaption>
</figure>

**Per flight, the typical delay is modest.** The average is 14.9 minutes per flight and 68.5 minutes per delayed flight.

**Carrier totals mislead; per-flight rates are fairer.** Ranking carriers by total delay minutes mostly lists the biggest airlines. Averaging delay per flight changes the picture: Air Wisconsin stands out at about 33 minutes per flight, well ahead of the next carriers at roughly 22 to 23 minutes. Among the ten highest, CommuteAir and GoJet sit at the bottom with about 17 minutes each.

<figure>
<img src="figures/airline-carriers.png" alt="Horizontal bar chart of the ten carriers with the highest average delay per flight, led by Air Wisconsin at about 33 minutes.">
<figcaption>Air Wisconsin has the highest average delay per flight, at about 33 minutes.</figcaption>
</figure>

## Two data-quality catches

- Two Republic Airline rows report a single flight with an average delay of more than 12 hours. They were excluded from the per-flight ranking.
- The same 12-hour filter also dropped 19 more rows (the counts show 21 rows removed against 2 extreme cases). These are almost certainly the rows whose missing flight counts I had filled with zero: 0 divided by 0 is not a number, so they failed the filter. Filling missing flight counts with zero was the wrong call; dropping those rows is cleaner.

## What this can't show

- The carrier ranking averages row-level ratios, so a carrier-airport-month with one flight counts as much as one with 5,000. Total delay minutes divided by total flights per carrier is the fairer measure.
- "Air Wisconsin Airlines" and "Air Wisconsin Airlines Corp" appear as separate carriers in the chart. They are probably one airline under two names, and grouping by carrier code would merge them.
- The correlation heatmap mostly shows that large airports have more of everything. Rates would be a better basis for correlation.
- I did not apply an outlier method beyond the 12-hour filter.
