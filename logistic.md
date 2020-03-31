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
{%- capture country_html -%}[{{ country_text }}](#0){:onClick="return setPlotSrc('plots/logistic/svg/{{ country }}.svg');"}{%- endcapture -%}
{% assign everything = country_html | concat: everything %}
{% endfor %}

{{ everything | array_to_sentence_string | replace: ", ", ",&nbsp;&nbsp; " | replace: " and ", " and&nbsp;&nbsp; " }}

<img id="plot" style="display: block; width: 100%; height: auto; border: 1pt solid LightGrey; border-left: 0; border-right: 0;" src="plots/empty.svg">

## What do these plots show?

These are the same data fitted to a [logistic growth model](https://youtu.be/Kas0tIxDvrg), which is a model that can estimate the maximum number of infections that will likely be seen.

_**To be written...**_ Just note that it gives **much** more optimistic answers than the ["pure exponential growth" model]({% link index.md %})!

## Acknowledgements

Special thanks to [Johns Hopkins University](https://www.jhu.edu/) and the [ESRI Living Atlas Team](https://livingatlas.arcgis.com/en/) for providing the world with such a valuable resource. Like almost every analysis online, this work was based on the [JHU CSSE Data](https://github.com/CSSEGISandData/COVID-19).
Also, thanks and kudos to [GitHub](https://github.com/) for supporting Open Source software and research!

[![License: CC BY 4.0](https://img.shields.io/github/license/adfernandes/covid19?color=orange&label=License&logo=Creative%20Commons&logoColor=white){: style="vertical-align: middle;"}](https://creativecommons.org/licenses/by/4.0/) This work is licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

This site is generated from [{{ site.github.repository_url }}]({{ site.github.repository_url }}) by automated [actions](https://github.com/adfernandes/covid19/actions?query=workflow%3A%22Build%20%26%20Deploy%22).

Copyright&nbsp;&copy;&nbsp;{{ 'now' | date: "%Y" }} by $${\sfst Andrew\ Fernandes\ \langle\email{andrew}{\scriptsize @}{fernandes.org}\rangle}$$.
