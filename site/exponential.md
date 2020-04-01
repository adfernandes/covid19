---
usemathjax: true
layout: default
---

<p style="text-align: left;">
    Assuming <b><ins>Dis</ins>continued Physical Distancing</b>
    <span style="float: right; font-size: small;">(<a href="logistic.html">Here</a>&nbsp;is&nbsp;Continued&nbsp;Distancing)</span>
</p>

{% include plots.md model="exponential" %}

## What do these plots show?

{% include show.md %}

The curves show the best-fit [exponential growth model](https://youtu.be/Kas0tIxDvrg) which estimates both how quickly we expect to see new occurrences, under the hopefully-incorrect assumption that we are _nowhere near_ the end of the pandemic. The [exponential growth model](https://youtu.be/Kas0tIxDvrg) is more appropriate when we have **<ins>dis</ins>continued physical distancing** since, under that scenario, transmission of *SARS-CoV-2*{:.sc} is considerably more rapid and can theoretically infect _everybody_, in an "infinite population" sense.

Notice that <ins>dis</ins>continued physical distancing gives **much more pessimistic** population counts than the alternate, more optimistic [logistic growth]({% link logistic.md %}) scenario!


## How do I interpret the plots?

We draw a **solid** line throught the most recent (rightmost) data points. In most cases, the straight line fits those points very well. That straight line represents "pure" exponential growth in the number of *COVID-19*{:.sc} cases. If you project that straight line one or two weeks into the future the numbers that get predicted can be startlingly large.

Now it **is true** that in some cases, for example Italy, where the long-term trend shows more of a curve than a straight line. That shows that the rate of disease spread is decreasing, which is a ~~good~~ great thing. A [more complex model][logistic.md] would have you draw a curve through the points and continue on up. But note that regardless of whether the future trend is a straight line or if the line flattens out, exponential growth guarantees that a great many more infections and disease cases are, to some extent, inevetable.

## Further Background

{% include further.md %}

## Statistical Details

The population counts were fit via weighted ordinary least squares in "log" space to a

$$ \log_2\left(n\right) = \beta_0 + \beta_1\cdot t$$

model, where $$t$$ is the time in days and $$n$$ is the number of people. The number of days used to fit the model parameters was chosen by inspection. The same number of days were used for all countries and populations, and is depicted on the plots by the solid line interpolants.

After a _lot_ of inspection and haggling with statistician and biologist colleagues, a simple linear weighing scheme was chosen to reflect the fact that more recent observations really should be granted slightly more evidentiary weight than those in the past. As with all hyperparmeter tuning, the devil is in the details, so... _caveat emptor_.

## Acknowledgements

{% include thanks.md %}
