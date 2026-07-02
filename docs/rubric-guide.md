# Rubric Guide

Rubrics define how a model output should be evaluated.

## Built-in rubrics

- correctness
- faithfulness
- groundedness
- coherence
- helpfulness
- safety
- tone
- completeness
- relevance
- instruction_following

## Rubric fields

- name
- description
- weight
- scoring scale
- prompt template

## Custom rubrics

Custom rubrics can be supplied at runtime through the batch evaluation request.

## Validation

- name and description must be non-empty
- scoring scale must be at least 1
- weight must be non-negative
- prompt overrides are supported through the prompt engine
