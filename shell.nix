{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "poetry-theme-env";

  buildInputs = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.pandas
    pkgs.python311Packages.tqdm
    pkgs.python311Packages.wikipedia-api
    pkgs.python311Packages.spacy
    pkgs.python311Packages.requests
    pkgs.python311Packages.beautifulsoup4
    pkgs.python311Packages.wikipedia
    pkgs.python311Packages.geopandas
    pkgs.python311Packages.matplotlib
    pkgs.python311Packages.geopy
    pkgs.python311Packages.jupyter
    pkgs.python311Packages.notebook
    pkgs.python311Packages.pip
    pkgs.python311Packages.scikit-learn
    pkgs.python311Packages.sentence-transformers
  ];
}

