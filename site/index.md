---
usemathjax: true
layout: default
---

<script>
    function setPlotSrc(location) {
        document.getElementById("plot").src = location;
        return false;
    }
</script>

{%- assign everything = "" | split: "," -%}
{%- for country in site.data.countries -%}
{%- capture country_text -%}{{ country | replace: " ", "&nbsp;" }}{%- endcapture -%}
{%- capture country_html -%}[{{ country_text }}](#0){:onClick="return setPlotSrc('plots/exponential/svg/{{ country }}.svg');"}{%- endcapture -%}
{% assign everything = country_html | concat: everything %}
{% endfor %}

{{ everything | array_to_sentence_string | replace: ", ", ",&nbsp;&nbsp; " | replace: " and ", " and&nbsp;&nbsp; " }}

<img id="plot" style="display: block; width: 100%; height: auto; border: 1pt solid LightGrey; border-left: 0; border-right: 0;" src="plots/empty.svg">

#### <ins>Quick update!</ins>

There are _more accurate_ but tricker-to-describe plots [**<ins>here</ins>**]({% link logistic.md %}) that I'm still in the process of writing up.

But for the _simplest possible_ case, keep on reading, below...

## What do these plots show?

The Internet is full of dire warnings about the upcoming surge of *covid-19*{:.sc} infections. [Article](https://www.washingtonpost.com/graphics/2020/world/corona-simulator/) after [article](https://covidactnow.org) after [article](https://www.ft.com/coronavirus-latest) warn of a huge and sudden increase in *covid-19*{:.sc} infections. For most of us, the "exponential blow-up" of the pandemic must ultimately be taken as a matter of faith.

There are already several [easy-to-understand](https://youtu.be/fgBla7RepXU), [non-mathematical](https://youtu.be/gxAaO2rsdIs), and [more-mathematical](https://youtu.be/Kas0tIxDvrg) online explanations of disease transmission and the growth of epidemics. But I wanted to make things _even simpler_, and remove some of the "mathematical magic" behind the dire pandemic predictions. And the simplest thing I could think of was plotting some points and drawing straight lines.

The trick is to scale the number of infctions by "order of magnitude". We know that 1,000 people is ten times the magnitude of 100, and we know that 10,000 people is ten times the magnitude of 1,000. And it turns that if we plot the _magnitude_ of *covid-19*{:.sc} infections over time, it is easier to understand how the epidemic is behaving. We can use the past behavior to predict the epidemic will _likely_ behave in the future.

So simply plotting the data and looking at it should be enough to convince almost anyone that we should be very worried indeed.

## How do I interpret the plots?

We draw a **solid** line throught the most recent (rightmost) data points. In most cases, the straight line fits those points very well. That straight line represents "pure" exponential growth in the number of *covid-19*{:.sc} cases. If you project that straight line one or two weeks into the future the numbers that get predicted can be startlingly large.

Now it **is true** that in some cases, for example Italy, where the long-term trend shows more of a curve than a straight line. That shows that the infection rate is decreasing, which is a ~~good~~ great thing. A more complex model would have you draw a curve through the points and continue on up. But note that regardless of whether the future trend is a straight line or if the line flattens out, exponential growth guarantees that a great many more infections are, to some extent, inevetable.

## Acknowledgements

Special thanks to [Johns Hopkins University](https://www.jhu.edu/) and the [ESRI Living Atlas Team](https://livingatlas.arcgis.com/en/) for providing the world with such a valuable resource. Like almost every analysis online, this work was based on the [JHU CSSE Data](https://github.com/CSSEGISandData/COVID-19).
Also, thanks and kudos to [GitHub](https://github.com/) for supporting Open Source software and research!

[![License: CC BY 4.0](https://img.shields.io/github/license/adfernandes/covid19?color=orange&label=License&logo=Creative%20Commons&logoColor=white){: style="vertical-align: middle;"}](https://creativecommons.org/licenses/by/4.0/) This work is licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

This site is generated from [{{ site.github.repository_url }}]({{ site.github.repository_url }}) by automated [actions](https://github.com/adfernandes/covid19/actions?query=workflow%3A%22Build%20%26%20Deploy%22).

Copyright&nbsp;&copy;&nbsp;{{ 'now' | date: "%Y" }} by $${\sfst Andrew\ Fernandes\ \langle\email{andrew}{\scriptsize @}{fernandes.org}\rangle}$$.
