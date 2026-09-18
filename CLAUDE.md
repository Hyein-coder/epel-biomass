Project: Biomass and Hydrogen Feedstock Sensitivity in Pyrolysis SAF Process

## Rule

Never rewrite entire files. 

Only modify required functions.

Do not explain.

Only show the patch.

Add comments only when 

- the code block context (or main task) changes. 
- there is an assumption (or emprical/random reason) behind the program.

Use type hints. 

Avoid unnecessary imports. 

Prefer vectorized pandas/numpy operations. 

When adding to a report or document, only append. Never replace or remove existing content without asking first. 

When writing, editing, or analyzing TEA code and results, refer to [[_WORKFRAME]] for the script lineage and calculation procedure. 

## Literature survey

When doing a literature survey (finding papers, citations, methods, journals, impact factors,  
citation counts), always run a separate fact-checker agent to sanity-check links and information  
before presenting or saving results. Use Google Scholar as the primary source for citation  
counts. When Scholar is CAPTCHA-blocked, use the OpenAlex API  
(`api.openalex.org/works/doi:<DOI>`, field `cited_by_count`) or the Crossref REST API  
(`is-referenced-by-count`) — both keyless and CAPTCHA-free — and label the source. Do not report reconstructed DOIs, journal names, impact factors, or citation counts  
as verified until the agent has confirmed them.

## Plotting

When generating any figure, follow the shared style in [[_PLOTTING_STYLE]]  
(apply `SA_RC` via `plt.rcParams.update(SA_RC)`; no grid, no titles, transparent legend,  
save `.png` only). 

## Answers

End every answer with a `## Left-over action points` section listing what is still not done: items  
deferred, skipped, blocked, or proposed but not applied, plus anything that needs a decision. One line  
each, with the file or script it touches. Write `None.` when nothing is outstanding — never omit the  
section.

## Ignore 

