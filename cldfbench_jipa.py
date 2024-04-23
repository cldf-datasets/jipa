"""
Generates a CLDF dataset for phoneme inventories from the "Journal of the IPA",
aggregated by Baird et al. 2021.
"""
import re
import shlex
import pathlib
import subprocess
import collections
import unicodedata

from unidecode import unidecode
from pyclts import CLTS
from pycldf import Sources
from cldfbench import CLDFSpec
from cldfbench import Dataset as BaseDataset
from clldutils.misc import slug
from clldutils.markup import add_markdown_text
from cldfcatalog import Catalog
from clld.lib.bibtex import unescape

CLTS_RELEASE = "v2.3.0"  # The CLTS release against which we compile the dataset.


def graph(limit=100):
    SQL = """\
SELECT p.CLTS_BIPA, count(v.cldf_id) AS c 
FROM ParameterTable AS p, ValueTable AS v 
WHERE v.cldf_parameterreference = p.cldf_id 
GROUP BY v.cldf_parameterreference ORDER BY c DESC LIMIT {}""".format(limit)
    p1 = subprocess.Popen(["sqlite3", "jipa.sqlite", SQL], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["termgraph", "--delim", "|"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    return SQL, p2.communicate()[0].decode('utf8')


def compute_id(text):
    """
    Returns a codepoint representation to an Unicode string.
    """
    unicode_repr = "".join(["u{0:0{1}X}".format(ord(char), 4) for char in text])
    return "%s_%s" % (slug(unidecode(text)), unicode_repr)


def normalize_grapheme(text):
    """
    Apply simple, non-CLTS, normalization.
    """
    return unicodedata.normalize("NFD", text)


def iter_data(p):
    """
    Reads the raw/*.txt files, yielding (section, lines) pairs.
    """
    sections = {}  # We keep track of sections we've seen before in order to deal with duplicates.
    section, lines = None, []
    for line in p.read_text(encoding='utf-8-sig').split('\n'):
        line = line.strip()
        if line.startswith("#"):  # a section
            if section and lines:
                if section in sections:
                    # If we have seen the section before, make sure content is identical.
                    assert lines == sections[section], '{}: {}'.format(p, section)
                sections[section] = lines
                yield section, lines
                lines = []
            # Store a normalized version of the new section title.
            section = line[1:].strip().lower()
            if section.endswith(':'):
                section = section[:-1].strip()
            section = section.replace(
                'exmaples', 'examples').replace(
                'orthographic notes', 'orthography notes').replace(
                'minim,al', 'minimal')
        else:
            lines.append(line)
    if section and lines:
        # Nen.txt has a duplicate "Reference" section with differing content. We ignore this.
        if not (p.stem == 'Nen' and section == 'reference'):
            if section in sections:
                assert lines == sections[section], '{}: {}'.format(p, section)
            yield section, lines


def iter_phonemes(t, ignore_allophones=False):
    """
    Splits a list of phonemes as provided in the source.

    We need to split by commas, provided they are not within parentheses (used to
    list allophones).
    """
    # Replace double commas introduced by joining lines when reading the raw data.
    t = re.sub(',\s*,', ',', t).replace(',,', ',')
    # A bit of cleaning:
    t = t.replace('\u032al', 'l̪').replace('\u2019', '\u02bc')

    in_allophones = False
    phoneme, allophone, allophones, marginal = '', '', [], False
    for i, c in enumerate(t):
        if c in [',', ';']:  # There's one case where semicolon is used to separate phonemes.
            if in_allophones:  # a new allophone starts.
                assert allophone.strip() or ignore_allophones
                allophones.append(allophone.strip())
                allophone = ''
            else:  # a new phoneme starts.
                assert phoneme.strip()
                yield phoneme.strip(), allophones, marginal
                phoneme, allophone, allophones, marginal = '', '', [], False
        elif c == '(':
            if phoneme.strip():  # If we've already found a phoneme, it's the list of allophones.
                in_allophones = True
            else:  # Otherwise, braces mark a single phoneme as marginal.
                marginal = True
        elif c == ')':
            if in_allophones:
                if allophone.strip():
                    allophones.append(allophone.strip())
                    allophone = ''
                in_allophones = False
            else:
                assert marginal
        else:
            if in_allophones:
                allophone += c
            else:
                if c.strip():
                    assert not allophones, 'Stuff after allophones: {}'.format(t)
                    phoneme += c
    if phoneme.strip():
        yield phoneme.strip(), allophones, marginal


def read_raw_source(filename):
    data = {"metadata": collections.OrderedDict()}

    for section, lines in iter_data(filename):
        if section == "reference":
            data["source"] = ' '.join(lines).strip()
        elif section == "language":
            data["language_name"] = ' '.join(lines).strip()
        elif section == "iso code":
            data["iso_code"] = ' '.join(lines).strip()
        elif section == "consonant inventory":
            data["consonants"] = ','.join(lines)
        elif section == "vowel inventory":
            data["vowels"] = ','.join(lines)
        elif section == 'phoneme inventory size':
            data["inventory"] = int(' '.join(lines).strip())
        else:
            if '\n'.join(lines).strip():
                data['metadata'][section] = '\n'.join(lines).strip()
    return data


class Dataset(BaseDataset):
    """
    CLDF dataset for JIPA inventories.
    """
    dir = pathlib.Path(__file__).parent
    id = "jipa"

    def cldf_specs(self):
        return CLDFSpec(module='StructureDataset', dir=self.cldf_dir)

    def cmd_readme(self, args):
        sql, chart = graph()
        return add_markdown_text(
            super().cmd_readme(args), """
### Coverage

Languages represented in the dataset color-coded by language family.

![](map.svg)

The long tail of phonemes attested in inventories in this dataset can be computed via 
[CLDF SQL](https://github.com/cldf/cldf/blob/master/extensions/sql.md):

```sql
{}
```

```
{}…
```
""".format(sql, chart), section='Description')

    def cmd_makecldf(self, args):
        self._schema(args.writer.cldf)
        glottolog = args.glottolog.api
        with Catalog.from_config('clts', tag=CLTS_RELEASE) as cat:
            args.writer.cldf.add_provenance(wasDerivedFrom=[cat.json_ld()])
            clts = CLTS(cat.dir)

            args.writer.cldf.add_sources(*Sources.from_file(self.raw_dir / "sources.bib"))

            all_glottolog = {lng.id: lng for lng in glottolog.languoids()}
            for row in self.etc_dir.read_csv("languages.csv", dicts=True):
                if row["Glottocode"] and row["Glottocode"] in all_glottolog:
                    lang = all_glottolog[row["Glottocode"]]
                    row.update({
                        "Family": lang.family.name if lang.family else '',
                        "Glottocode": row["Glottocode"],
                        "Latitude": lang.latitude or
                                    lang.parent.latitude or lang.parent.parent.latitude,
                        "Longitude": lang.longitude or
                                     lang.parent.longitude or lang.parent.parent.longitude,
                        "Macroarea": lang.macroareas[0].name if lang.macroareas else None,
                        "Glottolog_Name": lang.name,
                    })
                args.writer.objects['LanguageTable'].append(row)

            source_map = {
                lang["ID"]: lang["Source"] for lang in args.writer.objects['LanguageTable']}

            segment_ids = set()  # We keep track of segments we've already seen.
            counter = 1
            for filename in sorted(self.raw_dir.glob("*.txt"), key=lambda f: f.name):
                md = read_raw_source(filename)
                lang_key = slug(md["language_name"])
                src = args.writer.cldf.sources[source_map[lang_key]]
                args.writer.objects['ContributionTable'].append(dict(
                    ID=lang_key,
                    Name='Illustrations of the IPA: {}'.format(md["language_name"]),
                    Source=[source_map[lang_key]],
                    Contributor=unescape(src['Author']),
                    Citation=src.text(),
                    Comment=md['metadata'].pop('notes', None),
                    URL='https://doi.org/{}'.format(src['Doi']),
                    Metadata={k: v for k, v in md['metadata'].items() if 'minimal pair' not in k},
                    Minimal_Pairs={k: v for k, v in md['metadata'].items() if 'minimal pair' in k},
                ))

                segments = list(iter_phonemes(md["consonants"])) + list(iter_phonemes(md["vowels"]))
                # We compare phonemes we read from the data with stated inventory size. For some
                # languages, these do not match - often explained by errors in the source.
                if md['language_name'] not in [
                    'Central Sama',
                    'Dari Afghan Persian Informal',  # ?
                    'Ibibio',  # ?
                    'Jicarilla Apache',  # ?
                    'Lower Xumi',  # ?
                    'Luanyjang Dinka',  # tones, but ...
                    'Nepali',  # ?
                    'Nivacle Schichaam Lhavos',  # Errors
                    'Setswana South Africa',  # Errors
                    'Upper Sorbian',  # ?
                ]:
                    num_segments = len(segments)
                    if 'toneme inventory' in md['metadata']:
                        # Typically, tonemes are taken into account in the inventory size.
                        num_segments += len(list(iter_phonemes(
                            md['metadata']['toneme inventory'], ignore_allophones=True)))
                    assert int(md['inventory']) in [num_segments, len(segments)], filename

                for segment, allophones, marginal in segments:
                    normalized = normalize_grapheme(segment)
                    assert normalized in clts.transcriptiondata_dict['jipa'].grapheme_map
                    sound = clts.bipa[normalized]
                    par_id = compute_id(normalized)
                    if sound.type == 'unknownsound':
                        bipa_grapheme = None
                        clts_id = None
                    else:
                        bipa_grapheme = str(sound)
                        clts_id = sound.name.replace(' ', '_')

                    if par_id not in segment_ids:
                        segment_ids.add(par_id)
                        args.writer.objects['ParameterTable'].append({
                            "ID": par_id,
                            "Name": normalized,
                            "Description": '',
                            "CLTS_BIPA": bipa_grapheme,
                            "CLTS_Name": clts_id})

                    args.writer.objects['ValueTable'].append(
                        {
                            "ID": str(counter),
                            "Language_ID": lang_key,
                            "Contribution_ID": lang_key,
                            "Parameter_ID": par_id,
                            "Marginal": marginal,
                            "Allophones": allophones,
                            "Value_in_Source": '{}({})'.format(
                                segment, ', '.join(allophones)) if allophones else (
                                '({})'.format(segment) if marginal else segment),
                            "Value": normalized,
                            "Source": [source_map[lang_key]],
                            "InventorySize": md['inventory']
                        }
                    )
                    counter += 1

    def _schema(self, cldf):
        cldf.add_columns(
            "ValueTable",
            {
                "name": "Contribution_ID",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#contributionReference"},
            {
                "name": "Marginal",
                "dc:description": "Whether a segment is described as marginal.",
                "datatype": "boolean"},
            {
                "name": "Allophones",
                "separator": " ",
                "datatype": "string"},
            {
                "name": "InventorySize",
                "datatype": "integer"},
            {
                "name": "Value_in_Source",
                "datatype": "string"})
        cldf['ValueTable'].common_props['dc:description'] = \
            "Rows in this table correspond to phonemes found in a particular inventory."

        t = cldf.add_component(
            'ParameterTable',
            {
                'name': 'CLTS_BIPA',
                'dc:description': "CLTS BIPA grapheme for the segment",
                'datatype': 'string'},
            {
                'name': 'CLTS_Name',
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#cltsReference",
                'datatype': 'string'},
        )
        cldf.remove_columns('ParameterTable', 'ColumnSpec')
        t.common_props['dc:description'] = \
            ("Rows in this table correspond to CLTS BIPA sounds that phonemes found in the "
             "descriptions could be mapped to (in case CLTS_BIPA is non-empty) - or other "
             "sounds, identified by the grapheme used in the description.")
        cldf.add_component("LanguageTable", "Family", "Glottolog_Name")
        t = cldf.add_component(
            "ContributionTable",
            "URL",
            {
                "name": "Source",
                "separator": ";",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#source"},
            {
                "name": "Comment",
                "dc:description": "A comment by the authors of the dataset on the description.",
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#comment"},
            {
                "name": "Metadata",
                "dc:description": "Data extracted by the authors of the dataset from the "
                                  "descriptions",
                "datatype": "json"},
            {
                "name": "Minimal_Pairs",
                "dc:description": "Information on minimal pairs extracted by the authors of the "
                                  "dataset from the descriptions",
                "datatype": "json"},
        )
        t.common_props['dc:description'] = \
            ("Rows in this table correspond to phoneme inventories as described in Illustrations "
             "of the IPA.")
