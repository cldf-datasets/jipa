# CLDF dataset with phoneme inventories from the "Journal of the IPA", aggregated by Baird et al. (2021)

[![CLDF validation](https://github.com/cldf-datasets/jipa/workflows/CLDF-validation/badge.svg)](https://github.com/cldf-datasets/jipa/actions?query=workflow%3ACLDF-validation)

## How to cite

If you use these data please cite
- the original source
  > Baird, L., Evans, N., & Greenhill, S. J. (2021). Blowing in the wind: Using 'North Wind and the Sun' texts to sample phoneme inventories. Journal of the International Phonetic Association, 1–42. doi:10.1017/s002510032000033x
- the derived dataset using the DOI of the [particular released version](../../releases/) you were using

## Description


This dataset is licensed under a CC0-1.0 license

Available online at https://doi.org/10.1017/S002510032000033x



### Coverage

Languages represented in the dataset color-coded by language family.

![](map.svg)

The long tail of phonemes attested in inventories in this dataset can be computed via 
[CLDF SQL](https://github.com/cldf/cldf/blob/master/extensions/sql.md):

```sql
SELECT p.CLTS_BIPA, count(v.cldf_id) AS c 
FROM ParameterTable AS p, ValueTable AS v 
WHERE v.cldf_parameterreference = p.cldf_id 
GROUP BY v.cldf_parameterreference ORDER BY c DESC LIMIT 100
```

```

n  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 160.00
m  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 158.00
k  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 155.00
l  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 151.00
p  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 149.00
s  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 148.00
i  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 148.00
t  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 146.00
j  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 140.00
u  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 138.00
b  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 127.00
a  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 126.00
d  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 122.00
g  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 117.00
o  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 114.00
f  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 113.00
e  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 105.00
h  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 102.00
w  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 101.00
ʃ  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 99.00
z  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 96.00
tʃ : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 91.00
ŋ  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 89.00
ɛ  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 78.00
r  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 77.00
v  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 71.00
dʒ : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 70.00
ɔ  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 68.00
ɲ  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 68.00
ʒ  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 63.00
x  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 63.00
iː : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 59.00
aː : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 54.00
uː : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 53.00
ts : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 51.00
oː : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 50.00
ʔ  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 49.00
ə  : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 47.00
eː : ▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 45.00
ɪ  : ▇▇▇▇▇▇▇▇▇▇▇▇ 41.00
ɾ  : ▇▇▇▇▇▇▇▇▇▇▇▇ 40.00
ɣ  : ▇▇▇▇▇▇▇▇▇▇▇ 36.00
ʊ  : ▇▇▇▇▇▇▇▇▇▇ 34.00
kʰ : ▇▇▇▇▇▇▇▇▇▇ 32.00
ɛː : ▇▇▇▇▇▇▇▇▇ 30.00
tʰ : ▇▇▇▇▇▇▇▇▇ 29.00
pʰ : ▇▇▇▇▇▇▇▇▇ 29.00
c  : ▇▇▇▇▇▇▇▇ 26.00
y  : ▇▇▇▇▇▇▇ 25.00
kʷ : ▇▇▇▇▇▇▇ 24.00
ɑ  : ▇▇▇▇▇▇▇ 24.00
ɔː : ▇▇▇▇▇▇▇ 23.00
ʎ  : ▇▇▇▇▇▇ 22.00
ɟ  : ▇▇▇▇▇▇ 21.00
nː : ▇▇▇▇▇▇ 20.00
ĩ : ▇▇▇▇▇ 19.00
t̪ : ▇▇▇▇▇ 18.00
q  : ▇▇▇▇▇ 18.00
mː : ▇▇▇▇▇ 18.00
lː : ▇▇▇▇▇ 18.00
χ  : ▇▇▇▇▇ 18.00
dz : ▇▇▇▇▇ 18.00
æ  : ▇▇▇▇▇ 18.00
tɕ : ▇▇▇▇▇ 17.00
ɦ  : ▇▇▇▇▇ 17.00
ɕ  : ▇▇▇▇▇ 17.00
ɐ  : ▇▇▇▇▇ 17.00
œ  : ▇▇▇▇▇ 16.00
au : ▇▇▇▇▇ 16.00
ã : ▇▇▇▇▇ 16.00
ũ : ▇▇▇▇ 15.00
θ  : ▇▇▇▇ 15.00
ɹ  : ▇▇▇▇ 15.00
ɬ  : ▇▇▇▇ 15.00
kː : ▇▇▇▇ 15.00
yː : ▇▇▇▇ 14.00
ɯ  : ▇▇▇▇ 14.00
tː : ▇▇▇▇ 14.00
sː : ▇▇▇▇ 14.00
ʁ  : ▇▇▇▇ 14.00
øː : ▇▇▇▇ 14.00
gʷ : ▇▇▇▇ 14.00
ʋ  : ▇▇▇▇ 13.00
ʈ  : ▇▇▇▇ 13.00
ø  : ▇▇▇▇ 13.00
ɓ  : ▇▇▇▇ 13.00
bː : ▇▇▇▇ 13.00
tsʰ: ▇▇▇ 12.00
õ : ▇▇▇ 12.00
gː : ▇▇▇ 12.00
ẽ : ▇▇▇ 12.00
dʑ : ▇▇▇ 12.00
ɗ  : ▇▇▇ 12.00
ai : ▇▇▇ 12.00
ʌ  : ▇▇▇ 12.00
tʃʰ: ▇▇▇ 11.00
ʂ  : ▇▇▇ 11.00
jː : ▇▇▇ 11.00
ɨ  : ▇▇▇ 11.00
ɛ̃ : ▇▇▇ 11.00

…
```


## CLDF Datasets

The following CLDF datasets are available in [cldf](cldf):

- CLDF [StructureDataset](https://github.com/cldf/cldf/tree/master/modules/StructureDataset) at [cldf/StructureDataset-metadata.json](cldf/StructureDataset-metadata.json)