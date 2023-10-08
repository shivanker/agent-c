## Misc
- Add scratchpad to on-demand memory - as a separate tool. Make agent aware of its hidden scratchpad

## News
- News subscription
- News expert as a chain
- Research / news - kick off multiple parallel directions of research (WebResearchChain)
- Personalized news podcast - conversational, deeper in some topics, counter questions

## Tools / Capabilities
- Explore websites in detail
- Grab PDFs from internet, convert to text (pdfminer.six)
- Upload docs, summary, questions
- Plot charts based on data from multiple docs
- Image search + scenexplain to augment textual responses with images
- Ability to execute random python / bash code in a no-network docker sandbox

## Smarter prompting
- Guardrails for error detection & retrying
- Mixture of experts → parallel chains of self consistency & CoT / least-to-most
- Store *all* passing information in Vector databases (weaviate / chroma) for full articles / pdfs / webpages - with a ttl?
- Mixture of experts but with democracy - vote on the best answer
- AutoGen AI!!!
