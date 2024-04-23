# Releasing the JIPA CLDF dataset

- Install requirements:
  ```shell
  pip install cldfviz[cartopy]
  ```
- Re-create the CLDF dataset running
  ```shell
  cldfbench makecldf cldfbench_jipa.py --glottolog-version v5.0 --with-cldfreadme --with-zenodo
  ```
- Make sure data can be loaded into SQLite
  ```shell
  rm -f jipa.sqlite
  cldf createdb cldf/StructureDataset-metadata.json jipa.sqlite
  ```
- Re-create the README:
  ```shell
  cldfbench readme cldfbench_jipa.py
  ```
- Make sure the data is valid running
  ```shell
  pytest
  ```
- Recreate the coverage map
  ```shell
  cldfbench cldfviz.map cldf --format svg --width 20 --output map.svg --with-ocean --language-properties Family --no-legend --pacific-centered
  ```
- Commit all changes, tag the release, push code and tags.
- Create a release on GitHub and make sure it is picked up by Zenodo.
