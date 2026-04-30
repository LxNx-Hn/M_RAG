# Math Rendering Test

## Test 1: Inline with subscript
$\text{logit}_{\text{final}}$

## Test 2: Multiple inline with subscript
$\mathcal{V}_{\text{target}}$은 목표 언어이고, $\beta$는 강도

## Test 3: w subscript
$w_{\text{dense}} = 0.6$, $w_{\text{bm25}} = 0.4$, $k_{\text{retrieval}} = 20$

## Test 4: escaped underscore in text macro
$\text{scores} = \text{scores} - \alpha \cdot \text{empty\_logits}$

## Test 5: bracket notation with escaped underscore
$\text{scores}[:, \text{non\_target\_ids}] -= \beta$

## Test 6: Block math (should be fine)
$$\text{logit}_{\text{final}}(y_t) = \text{logit}(y_t \mid x, c) - \alpha \cdot \text{logit}(y_t \mid x)$$
