---
usemathjax: true
layout: default
---

This is introductory text.

# Header One

Text can be **bold**, _italic_, or ~~strikethrough~~.

## Header Two

> This is a blockquote following a header.
>
> When something is important enough, you do it even if the odds are not in your favor.

### Header Three

This is a test.

The following is a math block:

$$ a + b $$

But next comes a paragraph with an inline math statement:

\$$ c + d $$

If you don’t even want the inline math statement, escape the first two dollar signs:

\$\$ e + f $$

This is a $$x = \int\log\left(\theta\right)\,d\theta$$ math test.

### Header Four

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Mattis pellentesque id nibh tortor id aliquet lectus proin nibh. $$x = \int\log\left(\theta\right)\,d\theta$$ Mauris ultrices eros in cursus turpis massa. Amet mattis vulputate enim nulla aliquet porttitor lacus luctus. Mattis nunc sed blandit libero volutpat sed cras. Blandit aliquam etiam erat velit scelerisque in. Sagittis orci a scelerisque purus. Faucibus et molestie ac feugiat. Bibendum ut tristique et egestas quis ipsum suspendisse ultrices gravida \$\$x = \int\log\left(\theta\right)\,d\theta$$ nulla pellentesque dignissim enim sit amet. Fringilla phasellus faucibus scelerisque eleifend. Malesuada proin libero nunc consequat. Sit amet cursus sit amet dictum sit amet justo donec. In pellentesque massa placerat duis ultricies. Vel pretium lectus quam id. Ridiculus mus mauris vitae ultricies leo integer malesuada nunc vel. Est ultricies integer quis auctor. Enim lobortis scelerisque fermentum dui faucibus in ornare. Diam maecenas ultricies mi eget mauris pharetra et ultrices neque. Sed risus pretium quam vulputate dignissim suspendisse in.

# Plots

Processing Markdown with Liquid gives:

{% for country in site.data.countries %}
* [{{ country }}](plots/svg/{{ country }}.svg){:target="plot"}
{% endfor %}

Hopefully it works!

| ambrosia | gala | red delicious |
| pink lady | jazz | macintosh |
| honeycrisp | granny smith | fuji |

# Contact

You can reach me at $$\text{Andrew Fernandes}\ \email{andrew}{fernandes.org}$$. This site was generated [from here]({{ site.github.repository_url }}).

<div style="display: flex; flex-direction: column;">
<iframe name="plot" style="border: none; flex-grow: 1;"></iframe>
</div>
