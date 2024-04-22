"""
Generates a CLDF dataset for phoneme inventories from the "Journal of the IPA",
aggregated by Baird et al. 2021.
"""
import re
import pathlib
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
    sections = {}
    section, lines = None, []
    for line in p.read_text(encoding='utf-8-sig').split('\n'):
        line = line.strip()
        if line.startswith("#"):
            if section and lines:
                if section in sections:
                    assert lines == sections[section], '{}: {}'.format(p, section)
                sections[section] = lines
                yield section, lines
                lines = []
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
        if not (p.stem == 'Nen' and section == 'reference'):
            if section in sections:
                assert lines == sections[section], '{}: {}'.format(p, section)
            yield section, lines


def iter_phonemes(t, ignore_allophones=False):
    """
    Splits a list of phonemes as provided in the source.

    We need to split by commas, provided they are not within parentheses (used to
    list allophones). This solution uses a negative-lookahead in regex.
    """
    # Replace double commas introduced by joining lines when reading the raw data.
    t = re.sub(',\s*,', ',', t).replace(',,', ',')
    # Add a couple of missing commans, separating phonemes.
    t = t.replace('\u032al', 'l̪').replace('\u2019', '\u02bc')

    in_allophones = False
    phoneme, allophone, allophones, marginal = '', '', [], False
    for i, c in enumerate(t):
        if c in [',', ';']:
            if in_allophones:  # a new allophone starts.
                if allophone.strip():
                    allophones.append(allophone.strip())
                    allophone = ''
                elif not ignore_allophones:
                    raise ValueError('unexpected separator in allophones: {}'.format(t))
            else:  # a new phoneme starts.
                if phoneme.strip():
                    yield phoneme.strip(), allophones, marginal
                    phoneme, allophone, allophones, marginal = '', '', [], False
                else:
                    raise ValueError('unexpected separator in phonemes: {}; {}'.format(t, t[i-5:i+5]))
        elif c == '(':
            if phoneme.strip():
                in_allophones = True
            else:
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
        return CLDFSpec(
            module='StructureDataset',
            dir=self.cldf_dir,
            data_fnames={'ParameterTable': 'features.csv'}
        )

    def cmd_readme(self, args):
        return add_markdown_text(
            super().cmd_readme(args), """
Languages representd in the dataset color-coded by language family.

![](map.svg)""", section='Description')

    def cmd_makecldf(self, args):
        self._schema(args.writer.cldf)
        glottolog = args.glottolog.api
        with Catalog.from_config('clts', tag='v2.3.0') as cat:
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
                        "Latitude": lang.latitude or lang.parent.latitude or lang.parent.parent.latitude,
                        "Longitude": lang.longitude or lang.parent.longitude or lang.parent.parent.longitude,
                        "Macroarea": lang.macroareas[0].name if lang.macroareas else None,
                        "Glottolog_Name": lang.name,
                    })
                args.writer.objects['LanguageTable'].append(row)

            source_map = {
                lang["ID"]: lang["Source"] for lang in args.writer.objects['LanguageTable']}

            segment_ids = set()
            counter = 1
            for filename in sorted(self.raw_dir.glob("*.txt"), key=lambda f: f.name):
                contents = read_raw_source(filename)
                lang_key = slug(contents["language_name"])

                args.writer.objects['ContributionTable'].append(dict(
                    ID=lang_key,
                    Name='Illustrations of the IPA: {}'.format(contents["language_name"]),
                    Source=[source_map[lang_key]],
                    Contributor=unescape(args.writer.cldf.sources[source_map[lang_key]]['Author']),
                    Citation=args.writer.cldf.sources[source_map[lang_key]].text(),
                    Comment=contents['metadata'].pop('notes', None),
                    URL='https://doi.org/{}'.format(args.writer.cldf.sources[source_map[lang_key]]['Doi']),
                    Metadata={k: v for k, v in contents['metadata'].items() if 'minimal pair' not in k},
                    Minimal_Pairs={k: v for k, v in contents['metadata'].items() if 'minimal pair' in k},
                ))

                ps = ','.join([contents["consonants"], contents["vowels"]])
                segments = list(iter_phonemes(ps))

                if contents['language_name'] not in [
                    'Central Sama',
                    'Dari Afghan Persian Informal',  # ?
                    'Ibibio',  # ?
                    'Jicarilla Apache',  # ?
                    'Lower Xumi',  # ?
                    'Luanyjang Dinka',  # tones, but ...
                    'Lusoga Lutenga',  # ?
                    'Mono',  # Errors
                    'Nepali',  # ?
                    'Nivacle Schichaam Lhavos',  # Errors
                    'Setswana South Africa',  # Errors
                    'Upper Sorbian',  # ?
                ]:
                    num_segments = len(segments)
                    if 'toneme inventory' in contents['metadata']:
                        num_segments += len(list(iter_phonemes(
                            contents['metadata']['toneme inventory'], ignore_allophones=True)))
                    assert int(contents['inventory']) in [num_segments, len(segments)], filename

                for segment, allophones, marginal in segments:
                    normalized = normalize_grapheme(segment)
                    assert normalized in clts.transcriptiondata_dict['jipa'].grapheme_map
                    sound = clts.bipa[normalized]
                    par_id = compute_id(normalized)
                    if sound.type == 'unknownsound':
                        bipa_grapheme = ''
                        desc = ''
                    else:
                        bipa_grapheme = str(sound)
                        desc = sound.name

                    if par_id not in segment_ids:
                        segment_ids.add(par_id)
                        args.writer.objects['ParameterTable'].append({
                            "ID": par_id,
                            "Name": normalized,
                            "Description": '',
                            "CLTS_BIPA": bipa_grapheme,
                            "CLTS_Name": desc})

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
                            "InventorySize": contents['inventory']
                        }
                    )
                    counter += 1

    def _schema(self, cldf):
        cldf.add_columns(
            "ValueTable",
            {"name": "Contribution_ID", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#contributionReference"},
            {"name": "Marginal", "datatype": "boolean"},
            {"name": "Allophones", "separator": " ", "datatype": "string"},
            {"name": "InventorySize", "datatype": "integer"},
            {"name": "Value_in_Source", "datatype": "string"})

        cldf.add_columns(
            'ParameterTable',
            {'name': 'CLTS_BIPA', 'datatype': 'string'},
            {'name': 'CLTS_Name', 'datatype': 'string'})
        cldf.remove_columns('ParameterTable', 'ColumnSpec')
        cldf.add_component("LanguageTable", "Family", "Glottolog_Name")
        cldf.add_component(
            "ContributionTable",
            "URL",
            {"name": "Source", "separator": ";", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#source"},
            {"name": "Comment", "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#comment"},

            {"name": "Metadata", "datatype": "json"},
            {"name": "Minimal_Pairs", "datatype": "json"},
        )
