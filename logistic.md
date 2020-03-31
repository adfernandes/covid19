---
usemathjax: true
layout: default
---

**Continued Physical Distancing**

{% include plots.md model="logistic" %}

## What do these plots show?

{% include show.md %}

The curves show the best-fit [logistic growth model](https://youtu.be/Kas0tIxDvrg) which estimates both how quickly we expect to see new occurrences, and what the long-term maximum numbers are likely to be.

The [logistic growth model](https://youtu.be/Kas0tIxDvrg) is more appropriate when we have **continued physical distancing** since, under that scenario, transmission of *covid-19*{:.sc} is considerably slowed.

Notice that continued physical distancing gives **much more optimistic** infection counts than the alternate, more pessimistic [exponential growth]({% link exponential.md %}) scenario!

## Further Background

{% include further.md %}

## Statistical Details

The population counts were fit via ordinary least squares in "logit" space to a

$$ \log_2\left(\frac{n/n_{\text{max}}}{1 - n/n_{\text{max}}}\right) = \beta_0 + \beta_1\cdot t$$

model, where $$t$$ is the time in days and $$n$$ is the number of people. The number of days used to fit the model parameters was chosen by inspection. The same number of days were used for all countries and populations, and is depicted on the plots by the solid line interpolants.

## Acknowledgements

{% include thanks.md %}
